import os
import json
import pandas as pd
from datetime import datetime, timedelta
import gspread
from flask import Flask, render_template, request, make_response, redirect, jsonify
import traceback
import re
import hashlib

app = Flask(__name__)

# --- SEGURANÇA E AUTH (VERCEL ENVS) ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def authenticate(email, password):
    password_hash = hash_password(password)
    for i in range(1, 10):
        stored_email = os.environ.get(f'CLIENT_{i}_EMAIL', '')
        stored_hash = os.environ.get(f'CLIENT_{i}_PASSWORD_HASH', '')
        if stored_email == email and stored_hash == password_hash:
            return i
    return None

def get_client_config(client_id):
    sheet_id = os.environ.get(f'CLIENT_{client_id}_SHEET_ID')
    client_name = os.environ.get(f'CLIENT_{client_id}_NAME', 'Cliente')
    if sheet_id:
        return {'sheet_id': sheet_id, 'name': client_name}
    return None

# --- AUXILIARES GERAIS ---
def parse_float(val):
    if val is None or val == "": return 0.0
    if not isinstance(val, str): return float(val) if pd.notna(val) else 0.0
    val = val.replace("R$", "").replace(" ", "").strip()
    if not val or val == "-": return 0.0
    if "," in val and "." in val:
        val = val.replace(".", "").replace(",", ".")
    elif "," in val:
        val = val.replace(",", ".")
    try: return float(val)
    except: return 0.0

# --- MOTOR MOZINI (AUTOMÁTICO) ---
def get_week_range(date_obj):
    weekday = date_obj.weekday() 
    if weekday >= 2: # Quarta ou depois
        start = date_obj - timedelta(days=weekday - 2)
    else: # Seg ou Ter
        start = date_obj - timedelta(days=weekday + 5)
    end = start + timedelta(days=6)
    return start.replace(hour=0, minute=0, second=0), end.replace(hour=23, minute=59, second=59)

def generate_report_mozini(sheet_id):
    cred_json = os.environ.get('GOOGLE_CREDENTIALS')
    if not cred_json: return "<p>Erro: Sem credenciais Google.</p>"
    try:
        gc = gspread.service_account_from_dict(json.loads(cred_json))
        sh = gc.open_by_key(sheet_id)
        
        ws_crm = sh.get_worksheet_by_id(899775580)
        data_crm = ws_crm.get_values('A1:L2000')
        df_crm = pd.DataFrame(data_crm[1:], columns=data_crm[0])
        
        ws_google = sh.get_worksheet_by_id(677341941)
        data_g = ws_google.get_values('A1:K1000')
        df_google = pd.DataFrame(data_g[1:], columns=[c.strip() for c in data_g[0]])
        
        ws_meta = sh.get_worksheet_by_id(0)
        data_m = ws_meta.get_values('A1:K1000')
        df_meta = pd.DataFrame(data_m[1:], columns=[c.strip() for c in data_m[0]])

        # Normalização de Datas para evitar o erro de Timestamp
        df_crm['Data format'] = pd.to_datetime(df_crm['Data'], format='%d/%m/%Y', errors='coerce').dt.tz_localize(None)
        df_google['Data format'] = pd.to_datetime(df_google['Dia'], format='%d/%m/%Y', errors='coerce').dt.tz_localize(None)
        df_meta['Data format'] = pd.to_datetime(df_meta['Dia'], format='%d/%m/%Y', errors='coerce').dt.tz_localize(None)
        
        # Gerar semanas automáticas
        now = datetime.now() - timedelta(hours=3)
        all_html = ""
        for i in range(4): # Últimas 4 semanas
            s, e = get_week_range(now - timedelta(weeks=i))
            df_c = df_crm[(df_crm['Data format'] >= s) & (df_crm['Data format'] <= e)]
            df_g = df_google[(df_google['Data format'] >= s) & (df_google['Data format'] <= e)]
            df_m = df_meta[(df_meta['Data format'] >= s) & (df_meta['Data format'] <= e)]
            
            fechados = len(df_c[df_c['Status'].str.contains('Fechado', na=False)])
            meta_inv = df_m['Valor usado (BRL)'].apply(parse_float).sum()
            goog_inv = df_g['Investimento'].apply(parse_float).sum()
            
            all_html += f'''
            <details style="background:rgba(20,20,20,0.8); border:1px solid rgba(255,255,255,0.1); border-radius:12px; margin-bottom:15px; overflow:hidden;">
                <summary style="padding:20px; font-weight:600; cursor:pointer; list-style:none; display:flex; justify-content:space-between;">
                    Semana {s.strftime('%d/%m')} a {e.strftime('%d/%m')}
                    <span style="color:#2563eb;">Ver Detalhes</span>
                </summary>
                <div style="padding:20px; border-top:1px solid rgba(255,255,255,0.1); display:grid; grid-template-columns:1fr 1fr; gap:20px;">
                    <div>
                        <h4 style="margin:0; font-size:11px; color:#a0a0a0; text-transform:uppercase;">Comercial</h4>
                        <p style="margin:10px 0; font-size:13px;">Fechados: <b>{fechados}</b></p>
                    </div>
                    <div>
                        <h4 style="margin:0; font-size:11px; color:#a0a0a0; text-transform:uppercase;">Tráfego</h4>
                        <p style="margin:10px 0; font-size:13px;">Gasto: <b>R$ {meta_inv + goog_inv:,.2f}</b></p>
                    </div>
                </div>
            </details>'''
        return all_html
    except Exception as e:
        return f"Erro Mozini: {str(e)}"

# --- MOTOR IFL (VERSÃO DE FERRO) ---
def generate_report_ifl(sheet_id, start_date=None, end_date=None):
    cred_json = os.environ.get('GOOGLE_CREDENTIALS_2', os.environ.get('GOOGLE_CREDENTIALS'))
    if not cred_json: return {"error": "Sem credenciais Google."}
    try:
        gc = gspread.service_account_from_dict(json.loads(cred_json))
        sh = gc.open_by_key(sheet_id)
        ws_v = sh.get_worksheet_by_id(1417375901)
        ws_t = sh.get_worksheet_by_id(2062220158)
        
        v_raw = ws_v.get_values('A1:Z2000')
        t_raw = ws_t.get_values('A1:Z2000')
        
        df_v = pd.DataFrame(v_raw[1:], columns=[c.strip() for c in v_raw[0]])
        df_t = pd.DataFrame(t_raw[1:], columns=[c.strip() for c in t_raw[0]])
        
        def find_c(df, ks):
            cols = [c.lower().strip() for c in df.columns]
            for k in ks:
                for i, c in enumerate(cols):
                    if k in c: return df.columns[i]
            return None

        cv_data = find_c(df_v, ['data', 'date']) or 'Data'
        cv_fat = find_c(df_v, ['fat', 'valor', 'total', 'bruto', 'preço', 'preco']) or 'Faturamento'
        cv_status = find_c(df_v, ['status', 'situacao', 'situação']) or 'Status'
        cv_prod = find_c(df_v, ['produto', 'offer', 'oferta']) or 'Produto'
        cv_origem = find_c(df_v, ['origem', 'src', 'utm_source']) or 'Origem'
        
        ct_data = find_c(df_t, ['data', 'date']) or 'Data'
        ct_inv = find_c(df_t, ['invest', 'inv', 'valor', 'gasto', 'custo']) or 'Investimento'
        ct_v_meta = find_c(df_t, ['venda', 'conversion', 'concurr', 'result']) or 'Vendas Plataforma'

        # Normalização de Datas
        for df, col in [(df_v, cv_data), (df_t, ct_data)]:
            if col in df.columns: df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce').dt.tz_localize(None)

        start = pd.to_datetime(start_date, dayfirst=True).tz_localize(None) if start_date else (datetime.now() - timedelta(days=7)).replace(hour=0,minute=0,second=0)
        end = pd.to_datetime(end_date, dayfirst=True).tz_localize(None) if end_date else datetime.now().replace(hour=23,minute=59,second=59)

        df_v_ok = df_v[(df_v[cv_data] >= start) & (df_v[cv_data] <= end)].copy()
        df_t_ok = df_t[(df_t[ct_data] >= start) & (df_t[ct_data] <= end)].copy()

        # Filtro de Aprovadas
        if cv_status in df_v_ok.columns:
            status_ok = ['aprovada', 'aprovado', 'pago', 'paga', 'sucesso', 'concluido', 'concluído', 'active']
            df_v_ok = df_v_ok[df_v_ok[cv_status].str.lower().str.strip().isin(status_ok)].copy()

        t_rev = df_v_ok[cv_fat].apply(parse_float).sum() if cv_fat in df_v_ok.columns else 0
        t_inv = df_t_ok[ct_inv].apply(parse_float).sum() if ct_inv in df_t_ok.columns else 0
        
        last_up = (datetime.now() - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")

        return {
            "fat_total": f"R$ {t_rev:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "inv_total": f"R$ {t_inv:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.'),
            "roas_geral": f"{(t_rev/t_inv if t_inv > 0 else 0):.2f}x",
            "last_update": last_up,
            "raw_vendas": df_v_ok.head(10).to_dict('records'),
            "raw_traffic": df_t_ok.head(10).to_dict('records')
        }
    except Exception as e:
        return {"error": f"Erro IFL: {str(e)}"}

# --- FRONT-END UNIFICADO (AZUL) ---
def get_session_page(client_name, client_id, report_html):
    return f'''
<!DOCTYPE html>
<html lang="pt-BR" data-theme="dark">
<head>
    <meta charset="UTF-8"><title>Painel Tráfego | {client_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{ --brand-color: #2563eb; --bg-dark: #050505; --card-bg: rgba(20, 20, 20, 0.8); --border-color: rgba(255, 255, 255, 0.1); }}
        body {{ background: var(--bg-dark); color: white; font-family: 'Inter', sans-serif; margin: 0; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 40px; border-bottom: 1px solid var(--border-color); background: rgba(0,0,0,0.5); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 100; }}
        h1 span {{ color: var(--brand-color); }}
        .btn {{ padding: 8px 16px; border-radius: 6px; border: 1px solid var(--border-color); background: transparent; color: white; cursor: pointer; text-decoration: none; font-size: 13px; font-weight: 600; }}
        .btn-refresh {{ background: var(--brand-color); border: none; }}
        .container {{ max-width: 1200px; margin: 40px auto; padding: 0 20px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Report de <span>Resultados.</span></h1>
        <div style="display:flex; gap:15px; align-items:center;">
            <span style="font-size:12px; color:#a0a0a0;">{client_name}</span>
            <button class="btn btn-refresh" onclick="location.reload()">Atualizar</button>
            <a href="/?logout=1" class="btn">Sair</a>
        </div>
    </div>
    <div class="container">{report_html}</div>
</body>
</html>'''

def get_session_html_template(client_id):
    if client_id == 2:
        path = os.path.join(os.path.dirname(__file__), 'templates', 'ifl_dashboard.html')
        try:
            with open(path, 'r', encoding='utf-8') as f: return f.read()
        except: return "Erro ao carregar template IFL."
    return None

def render_client_dashboard(client_id, config):
    cid = int(client_id)
    if cid == 2: # IFL
        payload = generate_report_ifl(config['sheet_id'], request.args.get('start'), request.args.get('end'))
        tmpl = get_session_html_template(2)
        if payload and '<script id="python-metrics-payload"' in tmpl:
            import re
            return re.sub(r'<script id="python-metrics-payload".*?</script>', f'<script id="python-metrics-payload" type="application/json">{json.dumps(payload)}</script>', tmpl, flags=re.DOTALL)
        return tmpl
    else: # Outros (Mozini)
        report_html = generate_report_mozini(config['sheet_id'])
        return get_session_page(config['name'], cid, report_html)

@app.route('/', methods=['GET', 'POST'])
def index():
    ck = 'panel_session'
    cid = request.cookies.get(ck)
    if request.method == 'POST':
        u = request.form.get('email', ''); p = request.form.get('password', '')
        cid = authenticate(u, p)
        if cid:
            res = make_response(redirect('/'))
            res.set_cookie(ck, str(cid), max_age=86400, httponly=True, path='/')
            return res
        return redirect('/?error=1')
    if request.args.get('logout'):
        res = make_response(redirect('/'))
        res.delete_cookie(ck, path='/')
        return res
    if cid:
        cfg = get_client_config(cid)
        if cfg: return render_client_dashboard(cid, cfg)
    
    # Login Minimalista
    err = request.args.get('error')
    return f'''
    <html><body style="background:#050505; color:white; font-family:sans-serif; display:flex; align-items:center; justify-content:center; height:100vh;">
    <form method="POST" style="background:#111; padding:40px; border-radius:12px; border:1px solid #333; width:300px;">
        <h2 style="color:#2563eb;">Painel Tráfego</h2>
        { '<p style="color:red; font-size:12px;">Login inválido</p>' if err else '' }
        <input name="email" placeholder="Usuário" style="width:100%; padding:10px; background:#000; border:1px solid #333; color:white; margin:8px 0;">
        <input name="password" type="password" placeholder="Senha" style="width:100%; padding:10px; background:#000; border:1px solid #333; color:white; margin:8px 0;">
        <button type="submit" style="width:100%; padding:10px; background:#2563eb; color:white; border:none; border-radius:6px; cursor:pointer;">Entrar</button>
    </form>
    </body></html>'''

if __name__ == '__main__':
    app.run(debug=True)
