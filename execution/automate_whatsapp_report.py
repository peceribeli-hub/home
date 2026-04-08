import gspread
import pandas as pd
import re
from datetime import datetime

cred_path = '/Users/paola/Downloads/Antigravity/credentials.json'
sheet_id = '13mau5hBOEO3ji4z0JwvfHMyZw4njECC3h05Nbsowtws'
template_path = '/Users/paola/Downloads/Antigravity/Empresas/Paola/Modelo de Relatorios/Modelo_Relatorio_WhatsApp.html'
output_path = '/Users/paola/Downloads/Antigravity/Empresas/Mozini/M_Modelo_Relatorio_WhatsApp.html'

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

def main():
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

    def clean_stage(val):
        if not val: return "Sem Etapa"
        return re.sub(r'^\d+\.\s*', '', str(val)).strip()

    for df in [df_kommo, df_meta, df_google]:
        if 'Data' in df.columns:
            df['Data format'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()

    weeks = [
        {"month": "MARÇO 2026", "name": "SEMANA 2", "date_str": "(09/03 a 17/03)", "start": "2026-03-09", "end": "2026-03-17"},
        {"month": "MARÇO 2026", "name": "SEMANA 3", "date_str": "(18/03 a 24/03)", "start": "2026-03-18", "end": "2026-03-24"},
        {"month": "MARÇO 2026", "name": "SEMANA 4", "date_str": "(25/03 a 31/03)", "start": "2026-03-25", "end": "2026-03-31"},
        {"month": "ABRIL 2026", "name": "SEMANA 1", "date_str": "(01/04 a 07/04)", "start": "2026-04-01", "end": "2026-04-07"}
    ]

    months_order = ["MARÇO 2026", "ABRIL 2026"]
    
    all_weeks_html = ""
    
    for month_name in months_order:
        month_weeks = [w for w in weeks if w["month"] == month_name]
        if not month_weeks: continue
        
        is_open = 'open' if month_name == "ABRIL 2026" else ''
        
        for w in month_weeks:
            start_dt = pd.to_datetime(w["start"])
            end_dt = pd.to_datetime(w["end"])

            df_k = df_kommo[(df_kommo['Data format'] >= start_dt) & (df_kommo['Data format'] <= end_dt)].copy()
            df_k['Etapa Limpa'] = df_k['Etapa'].apply(clean_stage)
            total_leads = len(df_k)
            
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

            mql_summary = get_summary_by_origin(df_k[df_k['Status'] == 'MQL'])
            sql_count = len(df_k[df_k['Status'] == 'SQL'])
            sql_summary = str(sql_count) if sql_count == 0 else f"{sql_count} {get_origem_label(df_k[df_k['Status'] == 'SQL']['Origem'].iloc[0])}" if len(df_k[df_k['Status'] == 'SQL']) > 0 else "0"
            
            ag_summary = get_summary_by_origin(df_k[df_k['R. Agendada'].str.strip() != ''])
            re_summary = get_summary_by_origin(df_k[df_k['R. Realizada'].str.strip() != ''])
            p_summary = get_summary_by_origin(df_k[df_k['Status'] == 'Perdido'])
            contratos = len(df_k[df_k['Contrato Fechado'].str.strip() != ''])

            # --- ADS DATA ---
            df_m = df_meta[(df_meta['Data format'] >= start_dt) & (df_meta['Data format'] <= end_dt)].copy()
            meta_inv = df_m['Investimento'].apply(parse_float).sum()
            meta_mensagens = pd.to_numeric(df_m['Mensagens'], errors='coerce').sum()
            
            df_k_meta = df_k[df_k['Origem'].apply(get_origem_label) == 'Meta Ads']
            m_meta = len(df_k_meta[df_k_meta['Status'] == 'MQL'])
            cpl_real = meta_inv / m_meta if m_meta else 0
            cpl_meta_ads = meta_inv / meta_mensagens if meta_mensagens else 0

            # Meta Demanda
            demanda_meta = df_k_meta.groupby('Problema').size().to_dict()
            demanda_meta_html = ""
            for prob_name, count in sorted(demanda_meta.items(), key=lambda x: x[1], reverse=True):
                prob_label = prob_name if prob_name else "Desconhecido"
                prob_cpl = meta_inv / count if count else 0
                demanda_meta_html += f'''
                            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px; padding: 12px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 13px; align-items: center;">
                                <b style="color: var(--text-gray-light); font-weight: 500; font-size: 12px; text-transform: uppercase;">{prob_label}</b>
                                <span style="text-align: center; color: var(--text-white); font-weight: 700;">{count} Leads</span>
                                <span style="text-align: right; color: var(--text-gray-light); font-weight: 700;">{format_currency(prob_cpl)}</span>
                            </div>'''

            # Meta Criativos
            df_m['Mensagens Num'] = pd.to_numeric(df_m['Mensagens'], errors='coerce').fillna(0)
            df_m['Invest Num'] = df_m['Investimento'].apply(parse_float)
            top_criativos = df_m.groupby(['Anúncio', 'AD URL', 'AD Status']).agg({'Mensagens Num': 'sum', 'Invest Num': 'sum'}).reset_index()
            top_criativos = top_criativos.sort_values('Mensagens Num', ascending=False).head(5)
            criativos_html = ""
            for _, row in top_criativos.iterrows():
                is_pausado = "Pausado" in str(row['AD Status'])
                text_color = "var(--revo-red-base)" if is_pausado else "var(--text-white)"
                asterisk = "*" if is_pausado else ""
                cpl_criativo = row['Invest Num'] / row['Mensagens Num'] if row['Mensagens Num'] else 0
                criativos_html += f'''
                            <div style="display: grid; grid-template-columns: auto 1fr 1fr; gap: 10px; padding: 12px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 13px; align-items: center;">
                                <b><a href="{row['AD URL']}" target="_blank" class="btn-criativo">{row['Anúncio'][:20]}</a></b>
                                <span style="text-align: center; color: {text_color}; font-weight: 700;">{int(row['Mensagens Num'])} Leads{asterisk}</span>
                                <span style="text-align: right; color: {text_color}; font-weight: 700;">{format_currency(cpl_criativo)}{asterisk}</span>
                            </div>'''

            # --- GOOGLE DATA ---
            df_g = df_google[(df_google['Data format'] >= start_dt) & (df_google['Data format'] <= end_dt)].copy()
            goog_inv = df_g['Investimento'].apply(parse_float).sum()
            goog_convs = pd.to_numeric(df_g['Conversões'], errors='coerce').sum()
            df_k_goog = df_k[df_k['Origem'].apply(get_origem_label) == 'Google Ads']
            m_goog = len(df_k_goog[df_k_goog['Status'] == 'MQL'])
            cpl_goog = goog_inv / m_goog if m_goog else 0
            
            demanda_goog = df_k_goog.groupby('Problema').size().to_dict()
            demanda_goog_html = ""
            for prob_name, count in sorted(demanda_goog.items(), key=lambda x: x[1], reverse=True):
                prob_label = prob_name if prob_name else "Desconhecido"
                prob_cpl = goog_inv / count if count else 0
                demanda_goog_html += f'''
                            <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 10px; padding: 12px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); font-size: 13px; align-items: center;">
                                <b style="color: var(--text-gray-light); font-weight: 500; font-size: 12px; text-transform: uppercase;">{prob_label}</b>
                                <span style="text-align: center; color: var(--text-white); font-weight: 700;">{count} Leads</span>
                                <span style="text-align: right; color: var(--text-gray-light); font-weight: 700;">{format_currency(prob_cpl)}</span>
                            </div>'''

            # --- PIPELINE ---
            pipeline_html = ""
            colors_map = {"Meta Ads": "#3B82F6", "Google Ads": "#22C55E", "Indicação": "#F97316", "Desconhecido": "#A855F7"}
            emoji_map = {"Meta Ads": "🔵", "Google Ads": "🟢", "Indicação": "🟠", "Desconhecido": "🟣"}
            padding_map = {"Meta Ads": "17px", "Google Ads": "20px", "Indicação": "20px", "Desconhecido": "20px"}
            
            for label, group_df in df_k.groupby(df_k['Origem'].apply(get_origem_label)):
                color = colors_map.get(label, "#FFFFFF")
                emoji = emoji_map.get(label, "")
                padding = padding_map.get(label, "20px")
                pipeline_html += f'''
                                    <li style="flex-direction: column; align-items: flex-start; gap: 4px; padding-bottom: 16px;">
                                        <b style="color: {color};">{emoji} {label} ({len(group_df)} Leads)</b>
                                        <div style="font-size: 13px; color: var(--text-gray-light); width: 100%; box-sizing: border-box; padding-right: {padding}; border-left: 2px solid rgba(255,255,255,0.1); padding-left: 10px; margin-top: 4px; line-height: 1.6;">'''
                for prob, prob_df in group_df.groupby('Problema'):
                    prob_label = prob if prob else "Desconhecido"
                    stages = prob_df.groupby('Etapa Limpa').size().to_dict()
                    stages_str = " | ".join([f"{v} {k}" for k, v in stages.items()])
                    pipeline_html += f"<strong>{prob_label} ({len(prob_df)}):</strong> {stages_str}<br>"
                pipeline_html += "</div></li>"

            # --- ALERTA ---
            alertas_leads = df_k[(df_k['Origem'] == '') | (df_k['Status'] == '') | (df_k['Etapa'] == '')]
            alerta_html = ""
            if len(alertas_leads) > 0:
                list_items = " | ".join([f"{row['Nome']} ({row['Data']})" for _, row in alertas_leads.iterrows()])
                alerta_html = f'<div class="insight-box"><strong>⚠️ Alerta de CRM</strong>{len(alertas_leads)} leads sem atualização esta semana.</div>'

            is_week_open = 'open' if w['name'] == 'SEMANA 1' else ''
            
            week_html = f'''
            <!-- {w['name']} -->
            <details class="week-toggle">
                <summary>{w['name']} {w['date_str']}</summary>
                
                <div class="week-content">
                    
                    <!-- CARTÃO COMERCIAL -->
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
                            <li><b>Contratos Fechados</b> <span style="color: var(--revo-red-base); font-weight: bold; font-size: 16px;">{contratos}</span></li>
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

                    <!-- CARTÃO META ADS -->
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

                    <!-- CARTÃO GOOGLE -->
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
            
            all_weeks_html += week_html

    # Read template and replace content
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Replace month sections with generated content
    meses_html = f'''
    <!-- MARÇO 2026 -->
    <details open>
        <summary>MARÇO 2026</summary>
        
        <div class="details-content">
            {''.join([w for w in all_weeks_html.split('<!-- SEMANA')[1:4]])}
        </div>
    </details>

    <!-- ABRIL 2026 -->
    <details open>
        <summary>ABRIL 2026</summary>
        
        <div class="details-content">
            {''.join([w for w in all_weeks_html.split('<!-- SEMANA')[4:]])}
        </div>
    </details>'''
    
    # Simple replacement approach
    template = template.replace(
        '<p>Acompanhamento de Tráfego e Funil Comercial Semanal</p>',
        '<p>Acompanhamento de Tráfego e Funil Comercial Semanal - Mozini Advocacia</p>'
    )
    template = template.replace(
        '<!-- SEMANA 3 -->\n            <details class="week-toggle" open>',
        all_weeks_html.split('<!-- SEMANA')[1] if '<!-- SEMANA' in all_weeks_html else ''
    )
    
    # For simplicity, just generate full HTML
    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel REVO | Report de WhatsApp - Mozini</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-master-dark: #050505;
            --revo-red-base: rgb(224, 0, 0);
            --revo-red-dark: rgb(168, 14, 0);
            --revo-red-glow: rgba(224, 0, 0, 0.4);
            --card-bg: #090909;
            --text-white: #FFFFFF;
            --text-gray-light: #CCCCCC;
            --text-gray-dark: #666666;
            --font-main: 'Inter', sans-serif;
            --border-glow: rgba(224, 0, 0, 0.2);
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
        }}
        .top-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(224, 0, 0, 0.3);
            color: var(--revo-red-base);
            padding: 4px 14px;
            border-radius: 100px;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            margin-bottom: 10px;
            background: rgba(224, 0, 0, 0.05);
        }}
        .header h1 {{
            font-size: 36px;
            font-weight: 900;
            margin: 0;
            color: var(--text-white);
            letter-spacing: -0.02em;
        }}
        .header h1 span {{
            color: var(--revo-red-base);
        }}
        .header p {{
            color: var(--text-gray-light);
            margin: 8px 0 0 0;
            font-size: 14px;
        }}
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
            transition: color 0.2s;
        }}
        details > summary::-webkit-details-marker {{
            display: none;
        }}
        details > summary:hover {{
            color: var(--revo-red-base);
        }}
        details > summary::after {{
            content: '+';
            font-size: 24px;
            color: var(--text-gray-dark);
            font-weight: 300;
        }}
        details[open] > summary::after {{
            content: '−';
            color: var(--revo-red-base);
        }}
        .details-content {{
            padding: 30px 0;
        }}
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
            border-bottom: none;
            letter-spacing: 0.5px;
        }}
        .week-toggle[open] > summary {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            background: #090909;
        }}
        .week-toggle > summary:hover {{
            background: #111111;
        }}
        .week-content {{
            padding: 25px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            align-items: start;
        }}
        @media (max-width: 900px) {{
            .week-content {{
                grid-template-columns: 1fr;
            }}
        }}
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
        .metric-list li:last-child {{
            border-bottom: none;
        }}
        .metric-list li b {{
            color: var(--text-gray-light);
            font-weight: 500;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
            margin-right: 15px;
        }}
        .metric-list li span {{
            font-weight: 700;
            color: var(--text-white);
            text-align: right;
            font-size: 14px;
        }}
        .sub-section-toggle {{
            background: #0A0A0A;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 16px;
            overflow: hidden;
            transition: border-color 0.2s;
        }}
        .sub-section-toggle > summary {{
            padding: 16px;
            cursor: pointer;
            list-style: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: none;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--text-gray-light);
            background: #0A0A0A;
        }}
        .sub-section-toggle > summary::-webkit-details-marker {{
            display: none;
        }}
        .sub-section-toggle[open] > summary {{
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            background: #0D0D0D;
        }}
        .sub-section-toggle > summary::after {{
            content: '+';
            font-size: 16px;
            color: var(--text-gray-dark);
            font-weight: 400;
        }}
        .sub-section-toggle[open] > summary::after {{
            content: '−';
            color: var(--text-white);
        }}
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
            border-left: 3px solid var(--revo-red-base);
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
        a {{
            color: #3B82F6;
            text-decoration: none;
            font-weight: 600;
        }}
        a:hover {{
            color: #60A5FA;
            text-decoration: underline;
        }}
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
            transition: all 0.2s;
            letter-spacing: 0.5px;
        }}
        .btn-criativo:hover {{
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(255, 255, 255, 0.3);
            color: var(--text-white);
            text-decoration: none;
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
                radial-gradient(4px 100px at 0px 235px, var(--revo-red-base), transparent),
                radial-gradient(4px 100px at 300px 235px, var(--revo-red-base), transparent),
                radial-gradient(2px 2px at 150px 117.5px, var(--revo-red-base) 100%, transparent 150%);
            background-size: 300px 235px, 300px 235px, 300px 235px;
            background-position: 0px 220px, 3px 220px, 151.5px 337.5px;
            animation: fall 150s linear infinite;
        }}
        @keyframes fall {{
            100% {{
                background-position: 0px 6800px, 3px 6800px, 151.5px 6917.5px;
            }}
        }}
    </style>
</head>
<body>

<div class="falling-pattern-anim"></div>

<div class="dashboard-container">
    
    <div class="header">
        <div class="top-badge">Painel Contínuo</div>
        <h1>Report de <span>Resultados.</span></h1>
        <p>Acompanhamento de Tráfego e Funil Comercial Semanal - Mozini Advocacia</p>
    </div>

    <details open>
        <summary>MARÇO 2026</summary>
        <div class="details-content">
            {''.join(['<!-- SEMANA' + w for w in all_weeks_html.split('<!-- SEMANA')[1:4]])}
        </div>
    </details>

    <details open>
        <summary>ABRIL 2026</summary>
        <div class="details-content">
            {''.join(['<!-- SEMANA' + w for w in all_weeks_html.split('<!-- SEMANA')[4:]])}
        </div>
    </details>

</div>

</body>
</html>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print("✅ Relatório gerado com sucesso!")
    print(f"Semanas Atualizadas: {[w['name'] for w in weeks]}")

if __name__ == "__main__":
    main()
