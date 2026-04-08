import gspread
import pandas as pd
import re
import os
import json
from datetime import datetime, timedelta
import hashlib
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
    # Ajuste para horário de Brasília (Vercel usa UTC)
    today = datetime.now() + timedelta(hours=-3)
    
    # Encontra a Terça-feira mais recente (weekday 1)
    days_since_tue = (today.weekday() - 1) % 7
    current_tue = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_tue)
    
    # Gera semanas retroativamente até o início de 2026
    raw_weeks = []
    iter_tue = current_tue
    while iter_tue.year >= 2026:
        iter_wed = iter_tue - timedelta(days=6)
        if iter_wed.year < 2026:
            break
            
        raw_weeks.append({
            "wed": iter_wed,
            "tue": iter_tue
        })
        iter_tue = iter_wed - timedelta(days=1)
    
    # Agrupa por mês e numera (Semana 1, 2...)
    month_names = {
        1: "JANEIRO", 2: "FEVEREIRO", 3: "MARÇO", 4: "ABRIL", 
        5: "MAIO", 6: "JUNHO", 7: "JULHO", 8: "AGOSTO", 
        9: "SETEMBRO", 10: "OUTUBRO", 11: "NOVEMBRO", 12: "DEZEMBRO"
    }
    
    # Organiza do mais antigo para o mais novo para numerar
    raw_weeks.sort(key=lambda x: x["wed"])
    
    grouped_data = {}
    for w in raw_weeks:
        m_name = month_names[w["wed"].month]
        m_key = f"{m_name} {w['wed'].year}"
        
        if m_key not in grouped_data:
            grouped_data[m_key] = []
        
        num = len(grouped_data[m_key]) + 1
        grouped_data[m_key].append({
            "month": m_key,
            "name": f"SEMANA {num}",
            "date_str": f"({w['wed'].strftime('%d/%m')} a {w['tue'].strftime('%d/%m')})",
            "start": w['wed'].strftime("%Y-%m-%d"),
            "end": w['tue'].strftime("%Y-%m-%d")
        })
    
    # Achata a lista de volta para o formato esperado, do mais recente para o antigo
    # Mas mantendo o agrupamento mensal
    final_list = []
    ordered_months = sorted(grouped_data.keys(), key=lambda k: (int(k.split()[1]), list(month_names.values()).index(k.split()[0])), reverse=True)
    
    for m in ordered_months:
        # Semanas do mês do mais recente para o antigo
        for s in reversed(grouped_data[m]):
            final_list.append(s)
            
    return final_list

def get_client_config(client_id):
    sheet_id = os.environ.get(f'CLIENT_{client_id}_SHEET_ID')
    client_name = os.environ.get(f'CLIENT_{client_id}_NAME', 'Cliente')
    if sheet_id:
        return {'sheet_id': sheet_id, 'name': client_name}
    return None

def get_all_clients():
    clients = []
    for i in range(1, 10):
        config = get_client_config(i)
        if config:
            clients.append({'id': i, 'name': config['name']})
    return clients

def authenticate(email, password):
    password_hash = hash_password(password)
    
    for i in range(1, 10):
        stored_email = os.environ.get(f'CLIENT_{i}_EMAIL', '')
        stored_hash = os.environ.get(f'CLIENT_{i}_PASSWORD_HASH', '')
        
        if stored_email == email and stored_hash == password_hash:
            return i
    
    return None

def generate_report(sheet_id):
    import tempfile
    cred_json = os.environ.get('GOOGLE_CREDENTIALS')
    if not cred_json:
        return "<p style='color:red;'>Erro: GOOGLE_CREDENTIALS não configurado</p>"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(json.loads(cred_json), f)
        cred_path = f.name
    
    try:
        gc = gspread.service_account(filename=cred_path)
        sh = gc.open_by_key(sheet_id)
        ws_kommo = sh.get_worksheet_by_id(899775580)
        data_k = ws_kommo.get_values('A1:K1000')
        df_kommo = pd.DataFrame(data_k[1:], columns=[c.strip() for c in data_k[0]])

        ws_meta = sh.get_worksheet_by_id(1936428443)
        data_m = ws_meta.get_values('A1:Z5000')
        df_meta = pd.DataFrame(data_m[1:], columns=[c.strip() for c in data_m[0]])

        ws_google = sh.get_worksheet_by_id(677341941)
        data_g = ws_google.get_values('A1:K1000')
        df_google = pd.DataFrame(data_g[1:], columns=[c.strip() for c in data_g[0]])
    except Exception as e:
        return f"<p style='color:red;'>Erro ao acessar planilhas: {str(e)}</p>"
    
    for df in [df_kommo, df_meta, df_google]:
        if 'Data' in df.columns:
            df['Data format'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()

    # Gera as semanas dinamicamente desde Jan/2026 seguindo ciclo Quarta-Terça
    weeks = generate_weeks_for_current_and_past_months()
    all_months_html = {}
    
    for w in weeks:
        start_dt = pd.to_datetime(w["start"])
        end_dt = pd.to_datetime(w["end"])

        df_k = df_kommo[(df_kommo['Data format'] >= start_dt) & (df_kommo['Data format'] <= end_dt)].copy()
        
        if len(df_k) == 0:
            continue
            
        df_k['Etapa Limpa'] = df_k['Etapa'].apply(clean_stage)
        total_leads = len(df_k)
        
        mql_summary = get_summary_by_origin(df_k[df_k['Status'] == 'MQL'])
        sql_count = len(df_k[df_k['Status'] == 'SQL'])
        sql_summary = str(sql_count) if sql_count == 0 else f"{sql_count} {get_origem_label(df_k[df_k['Status'] == 'SQL']['Origem'].iloc[0])}" if len(df_k[df_k['Status'] == 'SQL']) > 0 else "0"
        
        ag_summary = get_summary_by_origin(df_k[df_k['R. Agendada'].str.strip() != ''])
        re_summary = get_summary_by_origin(df_k[df_k['R. Realizada'].str.strip() != ''])
        p_summary = get_summary_by_origin(df_k[df_k['Status'] == 'Perdido'])
        contratos = len(df_k[df_k['Contrato Fechado'].str.strip() != ''])

        df_m = df_meta[(df_meta['Data format'] >= start_dt) & (df_meta['Data format'] <= end_dt)].copy()
        meta_inv = float(df_m['Investimento'].apply(parse_float).sum()) if len(df_m) > 0 else 0.0
        meta_mensagens = float(pd.to_numeric(df_m['Mensagens'], errors='coerce').sum()) if len(df_m) > 0 else 0.0
        
        df_k_meta = df_k[df_k['Origem'].apply(get_origem_label) == 'Meta Ads']
        m_meta = len(df_k_meta[df_k_meta['Status'] == 'MQL'])
        cpl_real = meta_inv / m_meta if m_meta else 0
        cpl_meta_ads = meta_inv / meta_mensagens if meta_mensagens else 0

        demanda_meta = df_k_meta.groupby('Problema').size().to_dict()
        demanda_meta_html = ""
        for prob_name, count in sorted(demanda_meta.items(), key=lambda x: x[1], reverse=True):
            prob_label = prob_name if prob_name else "Desconhecido"
            prob_cpl = meta_inv / count if count else 0
            demanda_meta_html += f'''<div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px; padding: 12px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 13px; align-items: center;"><b style="color: var(--text-gray-light); font-weight: 500; font-size: 12px; text-transform: uppercase;">{prob_label}</b><span style="text-align: center; color: var(--text-white); font-weight: 700;">{count} Leads</span><span style="text-align: right; color: var(--text-gray-light); font-weight: 700;">{format_currency(prob_cpl)}</span></div>'''

        df_m['Mensagens Num'] = pd.to_numeric(df_m['Mensagens'], errors='coerce').fillna(0)
        df_m['Invest Num'] = df_m['Investimento'].apply(parse_float)
        top_criativos = df_m.groupby(['Anúncio', 'AD URL', 'AD Status']).agg({'Mensagens Num': 'sum', 'Invest Num': 'sum'}).reset_index()
        top_criativos = top_criativos.sort_values('Mensagens Num', ascending=False).head(5)
        criativos_html = ""
        for _, row in top_criativos.iterrows():
            is_pausado = "Pausado" in str(row['AD Status'])
            text_color = "var(--brand-color)" if is_pausado else "var(--text-white)"
            asterisk = "*" if is_pausado else ""
            cpl_criativo = row['Invest Num'] / row['Mensagens Num'] if row['Mensagens Num'] else 0
            criativos_html += f'''<div style="display: grid; grid-template-columns: auto 1fr 1fr; gap: 10px; padding: 12px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 13px; align-items: center;"><b><a href="{row['AD URL']}" target="_blank" class="btn-criativo">{row['Anúncio'][:20]}</a></b><span style="text-align: center; color: {text_color}; font-weight: 700;">{int(row['Mensagens Num'])} Leads{asterisk}</span><span style="text-align: right; color: {text_color}; font-weight: 700;">{format_currency(cpl_criativo)}{asterisk}</span></div>'''

        df_g = df_google[(df_google['Data format'] >= start_dt) & (df_google['Data format'] <= end_dt)].copy()
        goog_inv = float(df_g['Investimento'].apply(parse_float).sum()) if len(df_g) > 0 else 0.0
        goog_convs = float(pd.to_numeric(df_g['Conversões'], errors='coerce').sum()) if len(df_g) > 0 else 0.0
        df_k_goog = df_k[df_k['Origem'].apply(get_origem_label) == 'Google Ads']
        m_goog = len(df_k_goog[df_k_goog['Status'] == 'MQL'])
        cpl_goog = goog_inv / m_goog if m_goog else 0
        
        demanda_goog = df_k_goog.groupby('Problema').size().to_dict()
        demanda_goog_html = ""
        for prob_name, count in sorted(demanda_goog.items(), key=lambda x: x[1], reverse=True):
            prob_label = prob_name if prob_name else "Desconhecido"
            prob_cpl = goog_inv / count if count else 0
            demanda_goog_html += f'''<div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px; padding: 12px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 13px; align-items: center;"><b style="color: var(--text-gray-light); font-weight: 500; font-size: 12px; text-transform: uppercase;">{prob_label}</b><span style="text-align: center; color: var(--text-white); font-weight: 700;">{count} Leads</span><span style="text-align: right; color: var(--text-gray-light); font-weight: 700;">{format_currency(prob_cpl)}</span></div>'''

        pipeline_html = ""
        colors_map = {"Meta Ads": "#3B82F6", "Google Ads": "#22C55E", "Indicação": "#F97316", "Desconhecido": "#A855F7"}
        emoji_map = {"Meta Ads": "🔵", "Google Ads": "🟢", "Indicação": "🟠", "Desconhecido": "🟣"}
        padding_map = {"Meta Ads": "17px", "Google Ads": "20px", "Indicação": "20px", "Desconhecido": "20px"}
        
        for label, group_df in df_k.groupby(df_k['Origem'].apply(get_origem_label)):
            color = colors_map.get(label, "#FFFFFF")
            emoji = emoji_map.get(label, "")
            padding = padding_map.get(label, "20px")
            pipeline_html += f'''<li style="flex-direction: column; align-items: flex-start; gap: 4px; padding-bottom: 16px;"><b style="color: {color};">{emoji} {label} ({len(group_df)} Leads)</b><div style="font-size: 13px; color: var(--text-gray-light); width: 100%; box-sizing: border-box; padding-right: {padding}; border-left: 2px solid rgba(255,255,255,0.1); padding-left: 10px; margin-top: 4px; line-height: 1.6;">'''
            for prob, prob_df in group_df.groupby('Problema'):
                prob_label = prob if prob else "Desconhecido"
                stages = prob_df.groupby('Etapa Limpa').size().to_dict()
                stages_str = " | ".join([f"{v} {k}" for k, v in stages.items()])
                pipeline_html += f"<strong>{prob_label} ({len(prob_df)}):</strong> {stages_str}<br>"
            pipeline_html += "</div></li>"

        alertas_leads = df_k[(df_k['Origem'] == '') | (df_k['Status'] == '') | (df_k['Etapa'] == '')]
        alerta_html = ""
        if len(alertas_leads) > 0:
            alerta_html = f'<div class="insight-box"><strong>⚠️ Alerta de CRM</strong>{len(alertas_leads)} leads sem atualização esta semana.</div>'

        is_current_week = w["name"] == "SEMANA 1" and datetime.now().strftime("%Y-%m") == w["start"][:7]
        
        week_html = f'''
        <details class="week-toggle" {"open" if is_current_week else ""}>
            <summary>{w['name']} {w['date_str']}</summary>
            <div class="week-content">
                <details open style="border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid #F59E0B; background-color: var(--card-bg); border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); grid-column: 1 / -1;">
                    <summary style="cursor: pointer; font-size: 16px; font-weight: bold; color: var(--text-white); padding: 20px 24px; outline: none; list-style: none;">1. Report Comercial (CRM)</summary>
                    <div style="padding: 0 24px 24px 24px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 20px;">
                    <ul class="metric-list">
                        <li><b>Leads Recebidos (Total)</b> <span>{total_leads} Leads</span></li>
                        <li><b>Leads MQL (Qualificados)</b> <span style="line-height: 1.6;">{mql_summary}</span></li>
                        <li><b>Leads SQL (Oportunidade)</b> <span>{sql_count if sql_count == 0 else sql_summary}</span></li>
                        <li><b>Reunião Agendada</b> <span>{ag_summary}</span></li>
                        <li><b>Reunião Realizada</b> <span>{re_summary}</span></li>
                        <li><b>Leads Perdidos</b> <span style="line-height: 1.6;">{p_summary}</span></li>
                        <li><b>Contratos Fechados</b> <span style="color: var(--brand-color); font-weight: bold; font-size: 16px;">{contratos}</span></li>
                    </ul>
                    <details class="sub-section-toggle">
                        <summary>Pipeline do Comercial (Etapas do CRM)</summary>
                        <div style="padding: 16px;">
                            <ul class="metric-list" style="margin-bottom: 0;">{pipeline_html}</ul>
                        </div>
                    </details>
                    {alerta_html}
                    </div>
                </details>
                <details open style="border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid #3B82F6; background-color: var(--card-bg); border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    <summary style="cursor: pointer; font-size: 16px; font-weight: bold; color: var(--text-white); padding: 20px 24px; outline: none; list-style: none;">2. Report Meta Ads</summary>
                    <div style="padding: 0 24px 24px 24px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 20px;">
                    <ul class="metric-list">
                        <li><b>Investimento total</b> <span>{format_currency(meta_inv)}</span></li>
                        <li><b>Leads Gerados</b> <span style="line-height: 1.6;">{m_meta} Real<br>{int(meta_mensagens)} Meta Ads</span></li>
                        <li><b>Custo por Lead (CPL)</b> <span style="line-height: 1.6;">{format_currency(cpl_real)} Real<br>{format_currency(cpl_meta_ads)} Meta Ads</span></li>
                    </ul>
                    <div class="sub-section">
                        <h4>Volume por Demanda</h4>
                        {demanda_meta_html if demanda_meta_html else '<div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px; padding: 12px 0; font-size: 13px; align-items: center;"><b style="color: var(--text-gray-light); font-weight: 500; font-size: 12px; text-transform: uppercase;">Sem dados</b><span style="text-align: center; color: var(--text-gray-dark); font-weight: 700;">-</span><span style="text-align: right; color: var(--text-gray-dark); font-weight: 700;">-</span></div>'}
                    </div>
                    <div class="sub-section">
                        <h4>Top Criativos</h4>
                        {criativos_html if criativos_html else '<div style="display: grid; grid-template-columns: auto 1fr 1fr; gap: 10px; padding: 12px 0; font-size: 13px; align-items: center;"><b style="color: var(--text-gray-light);">Sem criativos</b></div>'}
                    </div>
                    </div>
                </details>
                <details style="border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid #34A853; background-color: var(--card-bg); border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    <summary style="cursor: pointer; font-size: 16px; font-weight: bold; color: var(--text-white); padding: 20px 24px; outline: none; list-style: none;">3. Report Google Ads</summary>
                    <div style="padding: 0 24px 24px 24px; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 20px;">
                    <ul class="metric-list">
                        <li><b>Investimento total</b> <span>{format_currency(goog_inv)}</span></li>
                        <li><b>Leads Gerados</b> <span>{int(goog_convs)} Leads</span></li>
                        <li><b>Custo por Lead (CPL)</b> <span>{format_currency(cpl_goog)}</span></li>
                    </ul>
                    <div class="sub-section">
                        <h4>Volume por Demanda</h4>
                        {demanda_goog_html if demanda_goog_html else '<div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px; padding: 12px 0; font-size: 13px; align-items: center;"><b style="color: var(--text-gray-light); font-weight: 500; font-size: 12px; text-transform: uppercase;">Sem dados</b><span style="text-align: center; color: var(--text-gray-dark); font-weight: 700;">-</span><span style="text-align: right; color: var(--text-gray-dark); font-weight: 700;">-</span></div>'}
                    </div>
                    </div>
                </details>
            </div>
        </details>'''
        
        month_key = w['month']
        if month_key not in all_months_html:
            all_months_html[month_key] = []
        all_months_html[month_key].append(week_html)
    
    months_html = ""
    # Remove o sorted() para manter a ordem cronológica reversa (mais recente primeiro)
    for month_name, weeks_html in all_months_html.items():
        # Lógica simplificada para abrir o primeiro mês (o mais recente)
        is_first = months_html == ""
        months_html += f'''
        <details {"open" if is_first else ""}>
            <summary>{month_name}</summary>
            <div class="details-content">
                {"".join(weeks_html)}
            </div>
        </details>'''
    
    return months_html

def get_login_page(error=None):
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Painel Tráfego</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-master-dark: #050505;
            --brand-color: rgb(37, 99, 235);
            --card-bg: #090909;
            --text-white: #FFFFFF;
            --text-gray-light: #CCCCCC;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-master-dark);
            color: var(--text-white);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .login-container {{
            background: var(--card-bg);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 40px;
            width: 100%;
            max-width: 400px;
        }}
        .logo {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .logo h1 {{
            font-size: 28px;
            font-weight: 900;
            color: var(--text-white);
        }}
        .logo h1 span {{
            color: var(--brand-color);
        }}
        .logo p {{
            color: var(--text-gray-light);
            font-size: 14px;
            margin-top: 8px;
        }}
        .form-group {{
            margin-bottom: 20px;
        }}
        .form-group label {{
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-gray-light);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .form-group input {{
            width: 100%;
            padding: 14px 16px;
            background: #0A0A0A;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: var(--text-white);
            font-size: 14px;
            font-family: 'Inter', sans-serif;
        }}
        .form-group input:focus {{
            outline: none;
            border-color: var(--brand-color);
        }}
        .btn-login {{
            width: 100%;
            padding: 14px;
            background: var(--brand-color);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .btn-login:hover {{
            background: rgb(29, 78, 216);
        }}
        .error {{
            background: rgba(37, 99, 235, 0.1);
            border: 1px solid var(--brand-color);
            border-radius: 8px;
            padding: 12px;
            color: var(--brand-color);
            font-size: 13px;
            margin-bottom: 20px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="login-container">
        <div class="logo">
            <h1>Painel <span>Tráfego</span></h1>
        </div>
        {"<div class='error'>E-mail ou senha incorretos</div>" if error else ""}
        <form method="POST">
            <div class="form-group">
                <label for="email">Usuário</label>
                <input type="text" id="email" name="email" required placeholder="mozini.adv">
            </div>
            <div class="form-group">
                <label for="password">Senha</label>
                <input type="password" id="password" name="password" required placeholder="••••••••">
            </div>
            <button type="submit" class="btn-login">Entrar</button>
        </form>
    </div>
</body>
</html>'''

@app.route('/', methods=['GET', 'POST'])
def index():
    cookie_name = 'panel_session'
    client_id = request.cookies.get(cookie_name)

    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')

        client_id = authenticate(email, password)

        if client_id:
            config = get_client_config(client_id)
            session_html = get_session_page(config['name'], client_id, generate_report(config['sheet_id']))
            resp = make_response(session_html)
            resp.set_cookie(cookie_name, str(client_id), max_age=86400, httponly=True, path='/')
            return resp
        else:
            return make_response(get_login_page(error=True))

    if request.args.get('logout'):
        resp = make_response(redirect('/'))
        resp.delete_cookie(cookie_name, path='/')
        return resp

    if client_id:
        config = get_client_config(int(client_id))
        if config:
            session_html = get_session_page(config['name'], client_id, generate_report(config['sheet_id']))
            return make_response(session_html)

    return make_response(get_login_page())

def get_session_page(client_name, client_id, report_html):
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Tráfego | {client_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-master-dark: #050505;
            --brand-color: rgb(37, 99, 235);
            --brand-color-dark: rgb(29, 78, 216);
            --card-bg: #090909;
            --text-white: #FFFFFF;
            --text-gray-light: #CCCCCC;
            --text-gray-dark: #666666;
            --font-main: 'Inter', sans-serif;
        }}
        body {{
            background-color: var(--bg-master-dark);
            color: var(--text-white);
            font-family: var(--font-main);
            margin: 0;
            padding: 40px;
            overflow-x: hidden;
        }}
        .dashboard-container {{
            max-width: 1100px;
            margin: 0 auto;
            position: relative;
            z-index: 10;
        }}
        .header {{
            margin-bottom: 40px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header-left {{ flex: 1; }}
        .header-right {{
            display: flex;
            align-items: center;
            gap: 16px;
        }}
        .client-name {{
            color: var(--text-gray-light);
            font-size: 14px;
        }}
        .btn-logout {{
            background: transparent;
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: var(--text-gray-light);
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.3s;
        }}
        .btn-logout:hover {{
            border-color: var(--brand-color);
            color: var(--brand-color);
        }}
        .btn-refresh {{
            background: var(--brand-color);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s;
        }}
        .btn-refresh:hover {{
            background: var(--brand-color-dark);
        }}
        .btn-refresh:disabled {{
            opacity: 0.6;
            cursor: not-allowed;
        }}
        .btn-refresh .spinner {{
            width: 16px;
            height: 16px;
            border: 2px solid white;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            display: none;
        }}
        .btn-refresh.loading .spinner {{ display: block; }}
        .btn-refresh.loading .icon {{ display: none; }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        .top-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(37, 99, 235, 0.3);
            color: var(--brand-color);
            padding: 4px 14px;
            border-radius: 100px;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            margin-bottom: 10px;
            background: rgba(37, 99, 235, 0.05);
        }}
        .header h1 {{
            font-size: 36px;
            font-weight: 900;
            margin: 0;
            color: var(--text-white);
            letter-spacing: -0.02em;
        }}
        .header h1 span {{ color: var(--brand-color); }}
        details {{
            background: transparent;
            margin-bottom: 20px;
        }}
        details > summary {{
            padding: 15px 0;
            font-size: 24px;
            font-weight: 800;
            cursor: pointer;
            list-style: none;
            display: flex;
            align-items: center;
            justify-content: space-between;
            color: var(--text-white);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        details > summary::-webkit-details-marker {{ display: none; }}
        details > summary:hover {{ color: var(--brand-color); }}
        details > summary::after {{
            content: '+';
            font-size: 24px;
            color: var(--text-gray-dark);
        }}
        details[open] > summary::after {{ content: '−'; color: var(--brand-color); }}
        .details-content {{ padding: 30px 0; }}
        .week-toggle {{
            background: #0A0A0A;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .week-toggle > summary {{
            padding: 20px 25px;
            font-size: 16px;
            font-weight: 700;
            background: #0D0D0D;
        }}
        .week-toggle[open] > summary {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            background: #090909;
        }}
        .week-content {{
            padding: 25px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            align-items: start;
        }}
        @media (max-width: 900px) {{ .week-content {{ grid-template-columns: 1fr; }} }}
        .metric-list {{
            list-style: none;
            padding: 0;
            margin: 0 0 24px 0;
        }}
        .metric-list li {{
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 13px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .metric-list li:last-child {{ border-bottom: none; }}
        .metric-list li b {{
            color: var(--text-gray-light);
            font-weight: 500;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .metric-list li span {{
            font-weight: 700;
            color: var(--text-white);
            font-size: 14px;
        }}
        .sub-section-toggle {{
            background: #0A0A0A;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 16px;
            overflow: hidden;
        }}
        .sub-section-toggle > summary {{
            padding: 16px;
            cursor: pointer;
            list-style: none;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            color: var(--text-gray-light);
            background: #0A0A0A;
        }}
        .sub-section-toggle > summary::-webkit-details-marker {{ display: none; }}
        .sub-section-toggle[open] > summary {{ border-bottom: 1px solid rgba(255, 255, 255, 0.05); background: #0D0D0D; }}
        .sub-section-toggle > summary::after {{ content: '+'; font-size: 16px; color: var(--text-gray-dark); margin-left: 8px; }}
        .sub-section-toggle[open] > summary::after {{ content: '−'; color: var(--text-white); }}
        .sub-section {{
            background: #0A0A0A;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        .sub-section h4 {{
            margin: 0 0 12px 0;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-gray-dark);
        }}
        .insight-box {{
            background: #0A0A0A;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-left: 3px solid var(--brand-color);
            padding: 16px 20px;
            border-radius: 8px;
            font-size: 13px;
            color: var(--text-gray-light);
            line-height: 1.5;
            margin-top: 20px;
        }}
        .insight-box strong {{
            color: var(--text-white);
            font-weight: 700;
            display: block;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 11px;
        }}
        a {{ color: #3B82F6; text-decoration: none; }}
        a:hover {{ color: #60A5FA; }}
        .btn-criativo {{
            display: inline-block;
            padding: 4px 10px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            color: var(--text-white);
            text-decoration: none;
            font-weight: 600;
            font-size: 11px;
        }}
        .falling-pattern-anim {{
            position: fixed;
            width: 100%;
            height: 100%;
            top: 0; left: 0;
            background-color: transparent;
            z-index: 0;
            opacity: 0.4;
            pointer-events: none;
            background-image:
                radial-gradient(4px 100px at 0px 235px, var(--brand-color), transparent),
                radial-gradient(4px 100px at 300px 235px, var(--brand-color), transparent),
                radial-gradient(2px 2px at 150px 117.5px, var(--brand-color) 100%, transparent 150%);
            background-size: 300px 235px, 300px 235px, 300px 235px;
            background-position: 0px 220px, 3px 220px, 151.5px 337.5px;
            animation: fall 150s linear infinite;
        }}
        @keyframes fall {{ 100% {{ background-position: 0px 6800px, 3px 6800px, 151.5px 6917.5px; }} }}
    </style>
</head>
<body>
<div class="falling-pattern-anim"></div>
<div class="dashboard-container">
    <div class="header">
        <div class="header-left">
            <div class="top-badge">Painel Tráfego</div>
            <h1>Report de <span>Resultados.</span></h1>
        </div>
        <div class="header-right">
            <span class="client-name">{client_name}</span>
            <button class="btn-refresh" onclick="refreshReport(this)">
                <span class="spinner"></span>
                <span class="icon">🔄</span>
                <span class="text">Atualizar</span>
            </button>
            <a href="/?logout=1" class="btn-logout">Sair</a>
        </div>
    </div>
    <div id="report-content">
        {report_html}
    </div>
</div>
<script>
async function refreshReport(btn) {{
    btn.classList.add('loading');
    btn.disabled = true;
    try {{
        const response = await fetch(window.location.pathname);
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newContent = doc.getElementById('report-content');
        if (newContent) {{
            document.getElementById('report-content').innerHTML = newContent.innerHTML;
        }}
    }} catch (error) {{
        alert('Erro ao atualizar. Tente novamente.');
    }} finally {{
        btn.classList.remove('loading');
        btn.disabled = false;
    }}
}}
</script>
</body>
</html>'''
