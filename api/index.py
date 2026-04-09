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
    # Ajuste para horário de Brasília (Vercel usa UTC)
    today = datetime.now() + timedelta(hours=-3)
    
    # Encontra a Terça-feira de fechamento do ciclo atual
    # Se hoje é quarta, a terça de fechamento é a próxima. Se hoje é terça, é hoje.
    days_to_tue = (1 - today.weekday()) % 7
    current_tue = today.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_to_tue)
    
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

def get_session_html_template(client_id):
    """Retorna o template HTML correto baseado no ID do cliente."""
    # Cliente 2 é NaFazenda (IFL)
    if client_id == 2:
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'ifl_dashboard.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Erro: Template IFL não encontrado ({str(e)})."
    # Padrão para outros clientes (Mozini etc)
    return None

def generate_report_ifl(sheet_id, start_date=None, end_date=None):
    """Geração de relatório específica para NaFazenda (IFL) com suporte a filtro de data no servidor."""
    cred_json = os.environ.get('GOOGLE_CREDENTIALS_2', os.environ.get('GOOGLE_CREDENTIALS'))
    if not cred_json:
        return {"error": "GOOGLE_CREDENTIALS não configurado"}
    
    try:
        # Autenticação direta e rápida na Vercel
        gc = gspread.service_account_from_dict(json.loads(cred_json))
        sh = gc.open_by_key(sheet_id)
        
        # Abas específicas da NaFazenda
        ws_vendas = sh.get_worksheet_by_id(1417375901)
        ws_trafego = sh.get_worksheet_by_id(2062220158)
        ws_leads = sh.get_worksheet_by_id(621645250)
        ws_pesquisa = sh.get_worksheet_by_id(1970699103)

        # Otimização: get_values() é muito mais rápido que get_all_records()
        data_v_raw = ws_vendas.get_values('A1:Z5000')
        data_t_raw = ws_trafego.get_values('A1:Z5000')
        data_l_raw = ws_leads.get_values('A1:Z5000')
        data_p_raw = ws_pesquisa.get_values('A1:Z5000')

        df_vendas = pd.DataFrame(data_v_raw[1:], columns=[c.strip() for c in data_v_raw[0]]) if data_v_raw else pd.DataFrame()
        df_meta = pd.DataFrame(data_t_raw[1:], columns=[c.strip() for c in data_t_raw[0]]) if data_t_raw else pd.DataFrame()
        df_leads = pd.DataFrame(data_l_raw[1:], columns=[c.strip() for c in data_l_raw[0]]) if data_l_raw else pd.DataFrame()
        df_pesquisa = pd.DataFrame(data_p_raw[1:], columns=[c.strip() for c in data_p_raw[0]]) if data_p_raw else pd.DataFrame()
        
        # Funções de Apoio (Fuzzy Search e Limpeza)
        def find_col(df, keywords):
            cols = [c.lower().strip() for c in df.columns]
            for k in keywords:
                for i, c in enumerate(cols):
                    if k in c: return df.columns[i]
            return None

        def clean_val(x):
            if isinstance(x, str):
                x = x.replace('R$', '').replace('.', '').replace(',', '.').replace('%', '').strip()
                try: return float(x)
                except: return 0.0
            return float(x) if pd.notnull(x) else 0.0

        # Normalização de colunas
        df_vendas.columns = [c.strip() for c in df_vendas.columns]
        df_meta.columns = [c.strip() for c in df_meta.columns]
        
        # Detecção Inteligente de Colunas com Fallbacks
        col_v_data = find_col(df_vendas, ['data', 'date', 'creation']) or 'Data'
        col_v_fat = find_col(df_vendas, ['faturamento', 'fat', 'valor', 'total']) or 'Faturamento Total'
        col_v_status = find_col(df_vendas, ['status', 'situacao', 'situação']) or 'Status'
        col_v_prod = find_col(df_vendas, ['produto', 'item', 'offer', 'ob']) or 'Produto'
        
        col_t_data = find_col(df_meta, ['data', 'date']) or 'Data'
        col_t_inv = find_col(df_meta, ['investimento', 'inv', 'valor', 'gasto']) or 'Investimento'
        
        # Debug info para o painel
        debug_info = {
            "vendas_cols": df_vendas.columns.tolist(),
            "meta_cols": df_meta.columns.tolist(),
            "detected": {
                "v_data": col_v_data, "v_fat": col_v_fat, "v_status": col_v_status,
                "t_inv": col_t_inv
            }
        }

        # Limpeza de valores nas colunas detectadas (Apenas se existirem)
        if col_v_fat in df_vendas.columns: df_vendas[col_v_fat] = df_vendas[col_v_fat].apply(clean_val)
        if col_t_inv in df_meta.columns: df_meta[col_t_inv] = df_meta[col_t_inv].apply(clean_val)
        
        # Filtro de vendas aprovadas (Flexível)
        if col_v_status in df_vendas.columns and not df_vendas.empty:
            status_validos = ['aprovada', 'aprovado', 'pago', 'paga', 'sucesso', 'liquidado', 'conluído', 'concluido']
            df_v_aprov = df_vendas[df_vendas[col_v_status].str.lower().str.strip().isin(status_validos)].copy()
        else:
            df_v_aprov = df_vendas.copy()

        total_rev = df_v_aprov[col_v_fat].sum() if col_v_fat in df_v_aprov.columns and not df_v_aprov.empty else 0
        investments = df_meta[col_t_inv].sum() if col_t_inv in df_meta.columns and not df_meta.empty else 0
        
        # --- FILTRO DE DATA NO SERVIDOR (ESTILO MOZINI) ---
        if start_date and end_date:
            try:
                d1 = pd.to_datetime(start_date, errors='coerce')
                d2 = pd.to_datetime(end_date, errors='coerce')
                
                if pd.notnull(d1) and pd.notnull(d2):
                    # Filtrar Vendas
                    if col_v_data in df_v_aprov.columns:
                        df_v_aprov[col_v_data] = pd.to_datetime(df_v_aprov[col_v_data], dayfirst=True, errors='coerce')
                        df_v_aprov = df_v_aprov[(df_v_aprov[col_v_data] >= d1) & (df_v_aprov[col_v_data] <= d2)].copy()
                    
                    # Filtrar Tráfego
                    if col_t_data in df_meta.columns:
                        df_meta[col_t_data] = pd.to_datetime(df_meta[col_t_data], dayfirst=True, errors='coerce')
                        df_meta = df_meta[(df_meta[col_t_data] >= d1) & (df_meta[col_t_data] <= d2)].copy()
                    
                    # Recalcular totais após filtro
                    total_rev = df_v_aprov[col_v_fat].sum() if col_v_fat in df_v_aprov.columns and not df_v_aprov.empty else 0
                    investments = df_meta[col_t_inv].sum() if col_t_inv in df_meta.columns and not df_meta.empty else 0
            except:
                pass # Em caso de erro na data, mantém o total geral

        last_update_str = (datetime.now() - timedelta(hours=3)).strftime("%d/%m/%Y %H:%M")

    except Exception as e:
        return {"error": f"Erro ao acessar planilhas: {str(e)}"}
    
    # Ingressos (Imersão)
    if not df_v_aprov.empty and col_v_prod in df_v_aprov.columns:
        df_imersao = df_v_aprov[df_v_aprov[col_v_prod].str.contains('Imersão', na=False)]
        vendas_imersao = len(df_imersao)
        vendas_xrpec = len(df_v_aprov[df_v_aprov[col_v_prod].str.contains('xR Pec', na=False)])
    else:
        vendas_imersao = 0
        vendas_xrpec = 0
    
    # Métricas Gerais
    roas = total_rev / investments if investments > 0 else 0
    ticket = total_rev / (vendas_imersao + vendas_xrpec) if (vendas_imersao + vendas_xrpec) > 0 else 0
    cac = investments / vendas_imersao if vendas_imersao > 0 else 0
    
    # Preparar JSON para o Dashboard
    payload = {
        "fat_total": f"R$ {total_rev:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "inv_total": f"R$ {investments:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "ingressos_total": vendas_imersao,
        "roas_geral": f"{roas:.2f}x",
        "ticket_geral": f"R$ {ticket:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "cac_imersao": f"R$ {cac:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "raw_vendas": df_v_aprov[[c for c in [col_v_data, col_v_fat, col_v_prod] if c in df_v_aprov.columns]].rename(columns={col_v_fat: 'fat', col_v_data: 'data', col_v_prod: 'ob'}).to_dict('records') if not df_v_aprov.empty else [],
        "raw_traffic": df_meta[[c for c in [col_t_data, col_t_inv, 'Campanha', 'Conjunto de anúncios', 'Criativo'] if c in df_meta.columns]].rename(columns={
            col_t_data: 'data', 'Campanha': 'camp', 'Conjunto de anúncios': 'pub', 
            'Criativo': 'cria', col_t_inv: 'inv'
        }).to_dict('records') if not df_meta.empty else [],
        "last_update": last_update_str,
        "debug": debug_info
    }
    
    return payload


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
    
    for i, w in enumerate(weeks):
        start_dt = pd.to_datetime(w["start"])
        end_dt = pd.to_datetime(w["end"])

        df_k = df_kommo[(df_kommo['Data format'] >= start_dt) & (df_kommo['Data format'] <= end_dt)].copy()
        df_m = df_meta[(df_meta['Data format'] >= start_dt) & (df_meta['Data format'] <= end_dt)].copy()
        df_g = df_google[(df_google['Data format'] >= start_dt) & (df_google['Data format'] <= end_dt)].copy()
        
        if i > 0 and len(df_k) == 0 and len(df_m) == 0 and len(df_g) == 0:
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
            demanda_meta_html += f'''<div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px; padding: 12px 0; border-bottom: 1px solid var(--border-dim); font-size: 13px; align-items: center;"><b style="color: var(--text-gray-light); font-weight: 500; font-size: 12px; text-transform: uppercase;">{prob_label}</b><span style="text-align: center; color: var(--text-white); font-weight: 700;">{count} Leads</span><span style="text-align: right; color: var(--text-gray-light); font-weight: 700;">{format_currency(prob_cpl)}</span></div>'''

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
            criativos_html += f'''<div style="display: grid; grid-template-columns: auto 1fr 1fr; gap: 10px; padding: 12px 0; border-bottom: 1px solid var(--border-dim); font-size: 13px; align-items: center;"><b><a href="{row['AD URL']}" target="_blank" class="btn-criativo">{row['Anúncio'][:20]}</a></b><span style="text-align: center; color: {text_color}; font-weight: 700;">{int(row['Mensagens Num'])} Leads{asterisk}</span><span style="text-align: right; color: {text_color}; font-weight: 700;">{format_currency(cpl_criativo)}{asterisk}</span></div>'''

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
            demanda_goog_html += f'''<div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px; padding: 12px 0; border-bottom: 1px solid var(--border-dim); font-size: 13px; align-items: center;"><b style="color: var(--text-gray-light); font-weight: 500; font-size: 12px; text-transform: uppercase;">{prob_label}</b><span style="text-align: center; color: var(--text-white); font-weight: 700;">{count} Leads</span><span style="text-align: right; color: var(--text-gray-light); font-weight: 700;">{format_currency(prob_cpl)}</span></div>'''

        pipeline_html = ""
        colors_map = {"Meta Ads": "#3B82F6", "Google Ads": "#22C55E", "Indicação": "#F97316", "Desconhecido": "#A855F7"}
        emoji_map = {"Meta Ads": "🔵", "Google Ads": "🟢", "Indicação": "🟠", "Desconhecido": "🟣"}
        padding_map = {"Meta Ads": "17px", "Google Ads": "20px", "Indicação": "20px", "Desconhecido": "20px"}
        
        for label, group_df in df_k.groupby(df_k['Origem'].apply(get_origem_label)):
            color = colors_map.get(label, "#FFFFFF")
            emoji = emoji_map.get(label, "")
            padding = padding_map.get(label, "20px")
            pipeline_html += f'''<li style="flex-direction: column; align-items: flex-start; gap: 4px; padding-bottom: 16px;"><b style="color: {color};">{emoji} {label} ({len(group_df)} Leads)</b><div style="font-size: 13px; color: var(--text-gray-light); width: 100%; box-sizing: border-box; padding-right: {padding}; border-left: 2px solid var(--border-color); padding-left: 10px; margin-top: 4px; line-height: 1.6;">'''
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

        is_current_week = (i == 0)
        
        week_html = f'''
        <details class="week-toggle" {"open" if is_current_week else ""}>
            <summary>{w['name']} {w['date_str']}</summary>
            <div class="week-content">
                <details open style="border: 1px solid var(--border-dim); border-left: 4px solid #F59E0B; background-color: var(--card-bg); border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); grid-column: 1 / -1;">
                    <summary style="cursor: pointer; font-size: 16px; font-weight: bold; color: var(--text-white); padding: 20px 24px; outline: none; list-style: none;">1. Report Comercial (CRM)</summary>
                    <div style="padding: 0 24px 24px 24px; border-top: 1px solid var(--border-color); padding-top: 20px;">
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
                <details open style="border: 1px solid var(--border-dim); border-left: 4px solid #3B82F6; background-color: var(--card-bg); border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    <summary style="cursor: pointer; font-size: 16px; font-weight: bold; color: var(--text-white); padding: 20px 24px; outline: none; list-style: none;">2. Report Meta Ads</summary>
                    <div style="padding: 0 24px 24px 24px; border-top: 1px solid var(--border-color); padding-top: 20px;">
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
                <details style="border: 1px solid var(--border-dim); border-left: 4px solid #34A853; background-color: var(--card-bg); border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);">
                    <summary style="cursor: pointer; font-size: 16px; font-weight: bold; color: var(--text-white); padding: 20px 24px; outline: none; list-style: none;">3. Report Google Ads</summary>
                    <div style="padding: 0 24px 24px 24px; border-top: 1px solid var(--border-color); padding-top: 20px;">
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
            --bg-master: #050505;
            --brand-color: rgb(37, 99, 235);
            --card-bg: #090909;
            --input-bg: #0A0A0A;
            --text-white: #FFFFFF;
            --text-gray-light: #CCCCCC;
            --text-gray-dark: #666666;
            --border-color: rgba(255, 255, 255, 0.1);
        }}
        [data-theme="light"] {{
            --bg-master: #F3F4F6;
            --card-bg: #FFFFFF;
            --input-bg: #FFFFFF;
            --text-white: #111827;
            --text-gray-light: #4B5563;
            --text-gray-dark: #9CA3AF;
            --border-color: rgba(0, 0, 0, 0.1);
        }}
        .theme-text::after {{ content: "Modo claro"; }}
        .icon-sun {{ display: block; fill: currentColor; width: 16px; height: 16px; }}
        .icon-moon {{ display: none; fill: currentColor; width: 16px; height: 16px; }}
        [data-theme="light"] .theme-text::after {{ content: "Modo escuro"; }}
        [data-theme="light"] .icon-sun {{ display: none; }}
        [data-theme="light"] .icon-moon {{ display: block; }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-master);
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
            border: 1px solid var(--border-color);
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
            background: var(--input-bg);
            border: 1px solid var(--border-color);
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
    <button class="theme-toggle" onclick="toggleTheme()" style="position:fixed; top:24px; right:24px; background:var(--card-bg); border:1px solid var(--border-color); color:var(--text-gray-light); padding:8px 16px; border-radius:8px; cursor:pointer; display:flex; align-items:center; gap:8px; transition:0.3s; font-family:'Inter',sans-serif; font-size:13px; font-weight:600;"><svg class="icon-sun" viewBox="0 0 24 24"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg><svg class="icon-moon" viewBox="0 0 24 24"><path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-3.03 0-5.5-2.47-5.5-5.5 0-1.82.89-3.42 2.26-4.4C12.92 3.04 12.46 3 12 3zm0 16c-3.86 0-7-3.14-7-7s3.14-7 7-7c.18 0 .35.02.52.05-.2.85-.31 1.74-.31 2.66 0 4.15 2.65 7.68 6.44 8.78-1.92 1.58-4.28 2.51-6.65 2.51z"/></svg><span class="theme-text"></span></button>
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

<script>
    function setTheme(theme) {{
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }}
    function toggleTheme() {{
        const current = localStorage.getItem('theme') || 'dark';
        setTheme(current === 'dark' ? 'light' : 'dark');
    }}
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
</script>
</body>
</html>'''

def render_client_dashboard(client_id, config, start_date=None, end_date=None):
    """Renderiza o dashboard correto baseado no ID do cliente com suporte a filtros."""
    client_id = int(client_id)
    if client_id == 2:
        # NaFazenda (IFL)
        data_payload = generate_report_ifl(config['sheet_id'], start_date, end_date)
        template = get_session_html_template(2)
        
        if isinstance(data_payload, dict) and "error" in data_payload:
            return f"Erro ao processar dados: {data_payload['error']}"
            
        # Injeta os dados no template da IFL de forma robusta e simples
        import json
        session_html = template.replace('PYTHON_METRICS_HERE', json.dumps(data_payload))
        return session_html
    else:
        # Padrão (Mozini etc)
        return get_session_page(config['name'], client_id, generate_report(config['sheet_id']))

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
            session_html = render_client_dashboard(client_id, config)
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
        try:
            config = get_client_config(int(client_id))
            if config:
                start = request.args.get('start')
                end = request.args.get('end')
                session_html = render_client_dashboard(client_id, config, start, end)
                return make_response(session_html)
        except Exception as e:
            error_details = traceback.format_exc()
            return f"<h1>Erro de Execução (Diagnóstico)</h1><pre>{error_details}</pre>"

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
            --bg-master: #050505;
            --brand-color: rgb(37, 99, 235);
            --brand-color-dark: rgb(29, 78, 216);
            --card-bg: #090909;
            --text-white: #FFFFFF;
            --text-gray-light: #CCCCCC;
            --text-gray-dark: #666666;
            --border-color: rgba(255, 255, 255, 0.1);
            --border-dim: rgba(255, 255, 255, 0.05);
            --section-bg: #0A0A0A;
            --section-hover: #0D0D0D;
            --font-main: 'Inter', sans-serif;
        }}
        [data-theme="light"] {{
            --bg-master: #F3F4F6;
            --card-bg: #FFFFFF;
            --text-white: #111827;
            --text-gray-light: #4B5563;
            --text-gray-dark: #9CA3AF;
            --border-color: rgba(0, 0, 0, 0.1);
            --border-dim: rgba(0, 0, 0, 0.05);
            --section-bg: #F9FAFB;
            --section-hover: #F3F4F6;
        }}
        .theme-text::after {{ content: "Modo claro"; }}
        .icon-sun {{ display: block; fill: currentColor; width: 14px; height: 14px; }}
        .icon-moon {{ display: none; fill: currentColor; width: 14px; height: 14px; }}
        [data-theme="light"] .theme-text::after {{ content: "Modo escuro"; }}
        [data-theme="light"] .icon-sun {{ display: none; }}
        [data-theme="light"] .icon-moon {{ display: block; }}
        body {{
            background-color: var(--bg-master);
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
            border-bottom: 1px solid var(--border-color);
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
            border: 1px solid var(--border-color);
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
            border-bottom: 1px solid var(--border-color);
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
            background: var(--section-bg);
            border: 1px solid var(--border-dim);
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .week-toggle > summary {{
            padding: 20px 25px;
            font-size: 16px;
            font-weight: 700;
            background: var(--section-hover);
        }}
        .week-toggle[open] > summary {{
            border-bottom: 1px solid var(--border-dim);
            background: var(--card-bg);
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
            border-bottom: 1px solid var(--border-dim);
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
            background: var(--section-bg);
            border: 1px solid var(--border-dim);
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
            background: var(--section-bg);
        }}
        .sub-section-toggle > summary::-webkit-details-marker {{ display: none; }}
        .sub-section-toggle[open] > summary {{ border-bottom: 1px solid var(--border-dim); background: var(--section-hover); }}
        .sub-section-toggle > summary::after {{ content: '+'; font-size: 16px; color: var(--text-gray-dark); margin-left: 8px; }}
        .sub-section-toggle[open] > summary::after {{ content: '−'; color: var(--text-white); }}
        .sub-section {{
            background: var(--section-bg);
            border: 1px solid var(--border-dim);
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
            background: var(--section-bg);
            border: 1px solid var(--border-dim);
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
            background: var(--border-dim);
            border: 1px solid var(--border-color);
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
            <button class="theme-toggle" onclick="toggleTheme()" style="background:transparent; border:1px solid var(--border-color); color:var(--text-gray-light); padding:0 12px; border-radius:6px; cursor:pointer; display:flex; align-items:center; gap:8px; height:36px; transition:all 0.3s; font-family:'Inter',sans-serif; font-size:13px; font-weight:600;"><svg class="icon-sun" viewBox="0 0 24 24"><path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/></svg><svg class="icon-moon" viewBox="0 0 24 24"><path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9c0-.46-.04-.92-.1-1.36-.98 1.37-2.58 2.26-4.4 2.26-3.03 0-5.5-2.47-5.5-5.5 0-1.82.89-3.42 2.26-4.4C12.92 3.04 12.46 3 12 3zm0 16c-3.86 0-7-3.14-7-7s3.14-7 7-7c.18 0 .35.02.52.05-.2.85-.31 1.74-.31 2.66 0 4.15 2.65 7.68 6.44 8.78-1.92 1.58-4.28 2.51-6.65 2.51z"/></svg><span class="theme-text"></span></button>
            <button class="btn-refresh" onclick="refreshReport(this)">
                <span class="spinner"></span>
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
        console.error("Erro na atualização:", error);
        alert("Erro ao conectar com a planilha. Verifique se as abas não foram renomeadas ou tente novamente em instantes. Detalhe: " + error.message);
    }} finally {{
        btn.classList.remove('loading');
        btn.disabled = false;
    }}
}}
</script>
<script>
    function setTheme(theme) {{
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }}
    function toggleTheme() {{
        const current = localStorage.getItem('theme') || 'dark';
        setTheme(current === 'dark' ? 'light' : 'dark');
    }}
    const savedTheme = localStorage.getItem('theme') || 'dark';
    setTheme(savedTheme);
</script>
</body>
</html>'''
