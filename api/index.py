import gspread
import pandas as pd
import re
import os
import hashlib
import traceback
import json
from datetime import datetime, timedelta
from flask import Flask, request, make_response, redirect

app = Flask(__name__)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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

def format_currency(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def clean_stage(val):
    if not val: return "Sem Etapa"
    return re.sub(r'^\d+\.\s*', '', str(val)).strip()

def get_origem_label(orig):
    orig = str(orig).lower()
    if 'indic' in orig: return 'Indicação'
    if 'google' in orig: return 'Google Ads'
    if any(x in orig for x in ['meta', 'inst', 'face']): return 'Meta Ads'
    return 'Desconhecido'

def get_summary_by_origin(df_filter):
    if len(df_filter) == 0: return "0"
    counts = df_filter['Origem'].apply(get_origem_label).value_counts()
    return "<br>".join([f"{v} {k}" for k, v in counts.items()])

def generate_weeks_for_current_and_past_months(months_back=None):
    weeks = []
    today = datetime.now() + timedelta(hours=-3)
    days_to_tue = (1 - today.weekday()) % 7
    current_tue = today.replace(hour=23, minute=59, second=59, microsecond=0) + timedelta(days=days_to_tue)
    
    raw_weeks = []
    iter_tue = current_tue
    while iter_tue.year >= 2026:
        iter_wed = iter_tue - timedelta(days=6)
        if iter_wed.year < 2026: break
        raw_weeks.append({"wed": iter_wed, "tue": iter_tue})
        iter_tue = iter_wed - timedelta(days=1)
    
    month_names = {1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO", 9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"}
    raw_weeks.sort(key=lambda x: x["wed"])
    
    grouped_data = {}
    for w in raw_weeks:
        m_name = month_names[w["wed"].month]
        m_key = f"{m_name} {w['wed'].year}"
        if m_key not in grouped_data: grouped_data[m_key] = []
        num = len(grouped_data[m_key]) + 1
        grouped_data[m_key].append({
            "month": m_key, "name": f"SEMANA {num}", "date_str": f"({w['wed'].strftime('%d/%m')} a {w['tue'].strftime('%d/%m')})",
            "start": w['wed'].strftime("%Y-%m-%d"), "end": w['tue'].strftime("%Y-%m-%d")
        })
    
    final_list = []
    ordered_months = sorted(grouped_data.keys(), key=lambda k: (int(k.split()[1]), list(month_names.values()).index(k.split()[0])), reverse=True)
    for m in ordered_months:
        for s in reversed(grouped_data[m]): final_list.append(s)
    return final_list

def get_client_config(client_id):
    sid = os.environ.get(f'CLIENT_{client_id}_SHEET_ID')
    name = os.environ.get(f'CLIENT_{client_id}_NAME', 'Cliente')
    return {'sheet_id': sid, 'name': name} if sid else None

def authenticate(email, password):
    ph = hash_password(password)
    for i in range(1, 10):
        if os.environ.get(f'CLIENT_{i}_EMAIL') == email and os.environ.get(f'CLIENT_{i}_PASSWORD_HASH') == ph: return i
    return None

def get_session_html_template(client_id):
    if int(client_id) == 2:
        tp = os.path.join(os.path.dirname(__file__), 'templates', 'ifl_dashboard.html')
        try:
            with open(tp, 'r', encoding='utf-8') as f: return f.read()
        except: return "Erro: Template não encontrado."
    return None

def generate_report_ifl(sheet_id, start_date=None, end_date=None):
    """Versão de Ferro: Ultra Estável e Rápida"""
    cred_json = os.environ.get('GOOGLE_CREDENTIALS_2', os.environ.get('GOOGLE_CREDENTIALS'))
    if not cred_json: return {"error": "Sem credenciais Google."}
    
    try:
        gc = gspread.service_account_from_dict(json.loads(cred_json))
        sh = gc.open_by_key(sheet_id)
        ws_v = sh.get_worksheet_by_id(1417375901)
        ws_t = sh.get_worksheet_by_id(2062220158)
        
        if not ws_v or not ws_t: return {"error": "Abas essenciais não encontradas na planilha."}

        # Limite de 1000 linhas para performance
        v_raw = ws_v.get_values('A1:Z1000')
        t_raw = ws_t.get_values('A1:Z1000')

        df_v = pd.DataFrame(v_raw[1:], columns=[c.strip() for c in v_raw[0]]) if v_raw else pd.DataFrame()
        df_t = pd.DataFrame(t_raw[1:], columns=[c.strip() for c in t_raw[0]]) if t_raw else pd.DataFrame()

        def find_c(df, ks):
            cols = [c.lower().strip() for c in df.columns]
            for k in ks:
                for i, c in enumerate(cols):
                    if k in c: return df.columns[i]
            return None

        def clean_val(x):
            if isinstance(x, str):
                x = x.replace('R$', '').replace('.', '').replace(',', '.').replace('%', '').strip()
                try: return float(x)
                except: return 0.0
            return float(x) if pd.notnull(x) else 0.0

        # Detecção de Colunas (Dicionário Expandido)
        cv_data = find_c(df_v, ['data', 'date', 'creation']) or 'Data'
        cv_fat = find_c(df_v, ['fat', 'valor', 'total', 'bruto', 'pago', 'recebido', 'soma', 'preço', 'preco']) or 'Faturamento'
        cv_status = find_c(df_v, ['status', 'situacao', 'situação', 'etapa', 'resultado']) or 'Status'
        cv_prod = find_c(df_v, ['produto', 'ob', 'item', 'offer', 'oferta', 'nome']) or 'Produto'
        
        ct_data = find_c(df_t, ['data', 'date']) or 'Data'
        ct_inv = find_c(df_t, ['invest', 'inv', 'valor', 'gasto', 'custo', 'spending', 'amount', 'spen']) or 'Investimento'
        ct_chk = find_c(df_t, ['check', 'finaliz', 'checkout']) or 'Checkout'
        ct_cli = find_c(df_t, ['clique', 'click', 'clic']) or 'Cliques'
        ct_imp = find_c(df_t, ['impres', 'visualiz', 'imp']) or 'Impressões'
        ct_vis = find_c(df_t, ['visit', 'page', 'visu']) or 'Visitas'
        ct_camp = find_c(df_t, ['campanh', 'camp', 'campaign']) or 'Campanha'
        ct_pub = find_c(df_t, ['público', 'publico', 'conjunto', 'adset', 'pub']) or 'Público'
        ct_cria = find_c(df_t, ['criativo', 'anúncio', 'ad', 'cria']) or 'Criativo'
        ct_link = find_c(df_t, ['link', 'url', 'destin']) or 'Link'
        ct_thumb = find_c(df_t, ['thumb', 'imagem', 'img']) or 'Thumbnail'

        if cv_fat in df_v.columns: df_v[cv_fat] = df_v[cv_fat].apply(clean_val)
        if ct_inv in df_t.columns: df_t[ct_inv] = df_t[ct_inv].apply(clean_val)

        # Filtro de Aprovadas (Dicionário Expandido)
        if cv_status in df_v.columns and not df_v.empty:
            status_ok = ['aprovada', 'aprovado', 'pago', 'paga', 'sucesso', 'liquidado', 'concluido', 'concluí', 'concluída', 'concluído', 'finalizado', 'active']
            df_v_ok = df_v[df_v[cv_status].str.lower().str.strip().isin(status_ok)].copy()
        else:
            df_v_ok = df_v.copy()

        # --- FILTRO DE DATA ---
        if start_date and end_date:
            try:
                d1 = pd.to_datetime(start_date, errors='coerce')
                d2 = pd.to_datetime(end_date, errors='coerce')
                if pd.notnull(d1) and pd.notnull(d2):
                    if cv_data in df_v_ok.columns:
                        df_v_ok[cv_data] = pd.to_datetime(df_v_ok[cv_data], dayfirst=True, errors='coerce')
                        df_v_ok = df_v_ok[(df_v_ok[cv_data] >= d1) & (df_v_ok[cv_data] <= d2)].copy()
                    if ct_data in df_t.columns:
                        df_t[ct_data] = pd.to_datetime(df_t[ct_data], dayfirst=True, errors='coerce')
                        df_t = df_t[(df_t[ct_data] >= d1) & (df_t[ct_data] <= d2)].copy()
            except: pass

        t_rev = df_v_ok[cv_fat].sum() if cv_fat in df_v_ok.columns else 0
        t_inv = df_t[ct_inv].sum() if ct_inv in df_t.columns else 0
        
        # --- NORMALIZAÇÃO DE CHAVES (TRADUÇÃO PARA O DASHBOARD) ---
        # Vendas
        cols_v = {cv_data: 'data', cv_fat: 'fat', cv_prod: 'ob'}
        df_v_dash = df_v_ok[[c for c in cols_v.keys() if c in df_v_ok.columns]].rename(columns=cols_v)
        
        # Tráfego
        cols_t = {
            ct_data: 'data', ct_inv: 'inv', ct_chk: 'chk', ct_cli: 'cli', 
            ct_imp: 'imp', ct_vis: 'vis', ct_camp: 'camp', ct_pub: 'pub', 
            ct_cria: 'cria', ct_link: 'link', ct_thumb: 'thumb'
        }
        df_t_ash = df_t[[c for c in cols_t.keys() if c in df_t.columns]].rename(columns=cols_t)

        # Conversão de Datas de Volta para Texto (Essencial para não travar o JSON)
        if 'data' in df_v_dash.columns:
            df_v_dash['data'] = df_v_dash['data'].apply(lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x))
        if 'data' in df_t_ash.columns:
            df_t_ash['data'] = df_t_ash['data'].apply(lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x))

        last_up = (datetime.now() - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")

        roas = t_rev / t_inv if t_inv > 0 else 0
        v_imersao = 0; v_xrpec = 0
        if not df_v_dash.empty and 'ob' in df_v_dash.columns:
            v_imersao = len(df_v_dash[df_v_dash['ob'].str.contains('Imersão', na=False)])
            v_xrpec = len(df_v_dash[df_v_dash['ob'].str.contains('xR Pec', na=False)])

        ticket = t_rev / (v_imersao + v_xrpec) if (v_imersao + v_xrpec) > 0 else 0
        cac = t_inv / v_imersao if v_imersao > 0 else 0

        def fmt(v): return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        return {
            "fat_total": fmt(t_rev), "inv_total": fmt(t_inv), "roas_geral": f"{roas:.2f}x",
            "ingressos_total": int(v_imersao), "ticket_geral": fmt(ticket), "cac_imersao": fmt(cac),
            "raw_vendas": df_v_dash.fillna(0).to_dict('records') if not df_v_dash.empty else [],
            "raw_traffic": df_t_ash.fillna(0).to_dict('records') if not df_t_ash.empty else [],
            "last_update": last_up,
            "debug": {
                "v_cols": df_v_dash.columns.tolist() if not df_v_dash.empty else [],
                "t_cols": df_t_ash.columns.tolist() if not df_t_ash.empty else [],
                "detected": {"fat": cv_fat, "inv": ct_inv, "status": cv_status, "prod": cv_prod}
            }
        }
    except Exception as e:
        return {"error": f"Erro interno: {str(e)}"}

def generate_report(sheet_id):
    """Fallback para Mozini e outros"""
    cred_json = os.environ.get('GOOGLE_CREDENTIALS')
    if not cred_json: return "<p>Erro: Sem credenciais.</p>"
    try:
        gc = gspread.service_account_from_dict(json.loads(cred_json))
        sh = gc.open_by_key(sheet_id)
        df_k = pd.DataFrame(sh.get_worksheet_by_id(899775580).get_values('A1:K1000')[1:])
        return "Relatório Mozini Gerado."
    except Exception as e: return f"Erro: {str(e)}"

def render_client_dashboard(client_id, config, start=None, end=None):
    cid = int(client_id)
    if cid == 2:
        payload = generate_report_ifl(config['sheet_id'], start, end)
        tmpl = get_session_html_template(2)
        import json
        return tmpl.replace('PYTHON_METRICS_HERE', json.dumps(payload))
    return f"Dashboard {config['name']} em manutenção."

@app.route('/', methods=['GET', 'POST'])
def index():
    ck = 'panel_session'
    cid = request.cookies.get(ck)
    if request.method == 'POST':
        u = request.form.get('email', ''); p = request.form.get('password', '')
        cid = authenticate(u, p)
        if cid:
            res = make_response(render_client_dashboard(cid, get_client_config(cid)))
            res.set_cookie(ck, str(cid), max_age=86400, httponly=True, path='/')
            return res
        return make_response(redirect('/?error=1'))
    
    if request.args.get('logout'):
        res = make_response(redirect('/'))
        res.delete_cookie(ck, path='/')
        return res

    if cid:
        try:
            cfg = get_client_config(int(cid))
            if cfg:
                s = request.args.get('start'); e = request.args.get('end')
                return make_response(render_client_dashboard(cid, cfg, s, e))
        except Exception as e:
            return f"<h1>Erro de Execução (Diagnóstico)</h1><pre>{traceback.format_exc()}</pre>"
    
    tp = os.path.join(os.path.dirname(__file__), 'templates', 'ifl_dashboard.html')
    # Simplificação: O login agora usa o template da própria IFL ou uma página simples
    return make_response(redirect('/login'))

@app.route('/login')
def login():
    # Página de login minimalista para garantir funcionamento
    err = request.args.get('error')
    return f'''
    <html><body style="background:#050505; color:white; font-family:sans-serif; display:flex; align-items:center; justify-content:center; height:100vh;">
    <form method="POST" action="/" style="background:#090909; padding:40px; border-radius:12px; border:1px solid #333; width:300px;">
        <h2 style="margin-bottom:20px; color:#2563eb;">Painel Tráfego</h2>
        { '<p style="color:#ef4444; font-size:12px;">Login inválido</p>' if err else '' }
        <label style="font-size:12px; color:#999;">Usuário</label><br>
        <input name="email" style="width:100%; padding:10px; background:#000; border:1px solid #333; color:white; margin:8px 0;"><br>
        <label style="font-size:12px; color:#999;">Senha</label><br>
        <input name="password" type="password" style="width:100%; padding:10px; background:#000; border:1px solid #333; color:white; margin:8px 0;"><br>
        <button type="submit" style="width:100%; padding:10px; background:#2563eb; color:white; border:none; border-radius:6px; cursor:pointer; font-weight:bold; margin-top:20px;">Entrar</button>
    </form>
    </body></html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
