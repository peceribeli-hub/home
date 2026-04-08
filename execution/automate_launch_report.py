import pandas as pd
import re
import os

# Caminhos dos Arquivos
base_dir = '/Users/paola/Downloads/Antigravity/Empresas/NF/MGP'
vendas_path = os.path.join(base_dir, 'Método Gerente de Pasto - 💎 Vendas.csv')
leads_path = os.path.join(base_dir, 'Método Gerente de Pasto | 💸 Leads.csv')
meta_path = os.path.join(base_dir, 'Método Gerente de Pasto | 📈 Dados _ Meta.csv')
template_path = '/Users/paola/Downloads/Antigravity/Empresas/Paola/Modelo de Relatorios/Modelo_Relatorio_Lancamento.md'

def parse_currency(val):
    if pd.isna(val) or val == "": return 0.0
    if not isinstance(val, str): return float(val)
    val = val.replace("R$", "").replace(" ", "").strip()
    if not val: return 0.0
    
    # Se tiver vírgula e ponto, padrão BR: ponto=milhar, vírgula=decimal
    if "," in val and "." in val:
        val = val.replace(".", "").replace(",", ".")
    elif "," in val:
        # Padrão BR apenas com decimal ou milhar
        # Mas em valores pequenos ex: 56,35 -> 56.35
        val = val.replace(",", ".")
    # Se tiver apenas ponto, ex: 193.69 -> assume padrão US/Float, mantém o ponto
    
    try: return float(val)
    except: return 0.0

def format_currency(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def main():
    # 1. Carregamento dos Dados - Forçando string nos IDs para evitar notação científica
    df_vendas = pd.read_csv(vendas_path, dtype={'AD ID': str, 'Ad ID': str})
    df_leads = pd.read_csv(leads_path, dtype={'AD ID': str})
    df_meta = pd.read_csv(meta_path, dtype={'Ad ID': str})

    # 2. Processamento de Vendas
    # Filtrar apenas aprovadas
    df_vendas_aprovadas = df_vendas[df_vendas['Status'].str.contains('Aprovada', case=False, na=False)].copy()
    
    # Limpeza de colunas financeiras
    faturamento_bruto = df_vendas_aprovadas[' Faturamento Total '].apply(parse_currency).sum()
    comissao_liquida_total = df_vendas_aprovadas[' Comissão Líquida '].apply(parse_currency).sum()
    total_vendas = len(df_vendas_aprovadas)
    ticket_medio = faturamento_bruto / total_vendas if total_vendas else 0
    
    # Order Bumps
    # Algumas linhas podem ter múltiplos orderbumps separados por vírgula
    faturamento_ob = df_vendas_aprovadas['Faturamento OB'].apply(parse_currency).sum() if 'Faturamento OB' in df_vendas_aprovadas.columns else 0
    count_ob = df_vendas_aprovadas['Orderbumps'].notna().sum() if 'Orderbumps' in df_vendas_aprovadas.columns else 0

    # Formas de Pagamento
    pagamentos = df_vendas_aprovadas['Forma de Pagamento'].value_counts(normalize=True) * 100
    pix_perc = pagamentos.get('Pix', 0)
    cc_perc = pagamentos.get('Cartão de Crédito', 0)

    # 3. Processamento de Captação & Leads
    # Identificar apenas Leads que vieram do Tráfego Pago ([RA] na campanha)
    df_leads_trafego = df_leads[df_leads['Campaign'].str.contains('\[RA\]', case=False, na=False)].copy()
    total_leads_trafego_gerados = len(df_leads_trafego)
    total_leads_real = len(df_leads)
    
    # Cruzamento de E-mails para Conversão de Tráfego REAL (Leads [RA] que viraram Clientes)
    emails_leads_trafego = set(df_leads_trafego['Email'].str.strip().str.lower().unique())
    emails_vendas = set(df_vendas_aprovadas['Email'].str.strip().str.lower().unique())
    leads_trafego_que_compraram = emails_leads_trafego.intersection(emails_vendas)
    total_vendas_trafego = len(leads_trafego_que_compraram)
    
    # Meta Ads Data
    df_meta['Invest Num'] = df_meta[' Investimento '].apply(parse_currency)
    investimento_total = df_meta['Invest Num'].sum()
    
    # O usuário confirmou que Leads Meta = Leads [RA] (62)
    total_leads_meta = total_leads_trafego_gerados

    # Cruzamento para Melhores Criativos (Real Leads per Ad)
    # Primeiro, somar investimento e pegar o link por Ad ID na tabela Meta
    df_meta_ads = df_meta.groupby(['Ad ID', 'Criativo']).agg({
        'Invest Num': 'sum',
        'Link Criativo': 'first' # Pega o link do primeiro registro do Ad ID
    }).reset_index()
    
    # Segundo, contar leads por Ad ID na tabela de Leads
    df_leads['AD ID'] = df_leads['AD ID'].astype(str).str.strip().str.replace(".0", "", regex=False)
    df_meta_ads['Ad ID'] = df_meta_ads['Ad ID'].astype(str).str.strip().str.replace(".0", "", regex=False)
    
    leads_per_ad = df_leads['AD ID'].value_counts().reset_index()
    leads_per_ad.columns = ['Ad ID', 'Leads Real Count']
    
    # Merge
    df_criativos_full = pd.merge(df_meta_ads, leads_per_ad, on='Ad ID', how='left').fillna(0)
    
    # Métricas de plataforma (Meta Leads) - Agora baseadas no cruzamento [RA]
    df_criativos_full['Leads Meta Count'] = df_criativos_full['Leads Real Count'] # Simplificando conforme premissa do usuário
    
    # Cálculo de CPL Real per Creative
    df_criativos_full['CPL Real'] = df_criativos_full['Invest Num'] / df_criativos_full['Leads Real Count']
    df_criativos_full.loc[df_criativos_full['Leads Real Count'] == 0, 'CPL Real'] = 0
    
    # Top 5 Criativos
    top_5_criativos = df_criativos_full.sort_values('Leads Real Count', ascending=False).head(5)

    cpl_real = investimento_total / total_leads_real if total_leads_real else 0
    cpl_meta_ads = investimento_total / total_leads_meta if total_leads_meta else 0

    # 5. ROAS e Conversão
    roas_bruto = faturamento_bruto / investimento_total if investimento_total else 0
    roas_liquido = comissao_liquida_total / investimento_total if investimento_total else 0
    
    # Diferenciação de Conversão
    conversao_geral = (total_vendas / total_leads_real) * 100 if total_leads_real else 0
    # Conversão de Tráfego: Apenas leads [RA] que compraram / Total leads [RA] gerados
    conversao_trafego = (total_vendas_trafego / total_leads_trafego_gerados) * 100 if total_leads_trafego_gerados else 0

    # 6. Geração do Relatório Markdown
    report_md = f"""# Relatório de Lançamento: Método Gerente de Pasto (MGP)
**Evento:** Lançamento Meteórico - Março/2026 | **Data de Abertura:** 30/03/2026

> **Objetivo deste Relatório:** Centralizar o debriefing e os dados consolidados do lançamento MGP para justificar os resultados e servir como inteligência para os próximos eventos.

---

## 1. Visão Geral do Lançamento (Resultados Finais)
- **Investimento Total:** {format_currency(investimento_total)}
- **Faturamento Bruto:** {format_currency(faturamento_bruto)}
- **Comissão Líquida:** {format_currency(comissao_liquida_total)}
- **ROAS Bruto:** {roas_bruto:.2f}x
- **ROAS Líquido:** {roas_liquido:.2f}x
- **Conver. Geral (Vendas/Base Total):** {conversao_geral:.2f}%
- **Conver. Tráfego (Leads [RA] que compram):** {conversao_trafego:.2f}%
- **Ticket Médio:** {format_currency(ticket_medio)}

---

## 2. Fase 1: Captação de Leads (Real vs Meta Ads)
- **Investimento em Captação:** {format_currency(investimento_total)}
- **Total de Leads:**
    - **Real (Leads.csv):** {total_leads_real} Leads
    - **Meta Ads (Plataforma):** {int(total_leads_meta)} Leads
- **CPL Médio:**
    - **Real:** {format_currency(cpl_real)}
    - **Meta Ads:** {format_currency(cpl_meta_ads)}
- **Análise da Captação:** A discrepância entre Real e Meta (Tracking Loss) é comum em redirecionamentos para WhatsApp.

---

## 3. Fase 2: Vendas e Carrinho Aberto
- **Total de Vendas Aprovadas:** {total_vendas}
- **Faturamento Order Bump:** {format_currency(faturamento_ob)} ({count_ob} itens extras vendidos)
- **Formas de Pagamento:**
    - **Pix:** {pix_perc:.1f}%
    - **Cartão de Crédito:** {cc_perc:.1f}%
- **Análise das Vendas:** O ROAS Líquido de {roas_liquido:.2f}x indica o real lucro direto sobre o investimento em anúncios.

---

## 4. Melhores Criativos (Ranking por Leads REAIS)
| Criativo | Leads Real | Leads Meta | Investimento | CPL Real |
| :--- | :--- | :--- | :--- | :--- |
"""
    for _, row in top_5_criativos.iterrows():
        report_md += f"| {row['Criativo']} | {int(row['Leads Real Count'])} | {int(row['Leads Meta Count'])} | {format_currency(row['Invest Num'])} | {format_currency(row['CPL Real'])} |\n"

    report_md += """
---

## 5. Debriefing e Insights
- **O que funcionou:** A base de leads capturada via Meta Ads converteu com um ROAS expressivo.
- **Ajustes Próximos:** Monitorar a taxa de aprovação de boleto/cartão para otimizar o checkout.
"""

    md_output = os.path.join(base_dir, 'Relatorio_Lancamento_MGP.md')
    with open(md_output, 'w', encoding='utf-8') as f:
        f.write(report_md)

    # 7. Geração do HTML Premium com Branding Oficial
    html_output = os.path.join(base_dir, 'Relatorio_Lancamento_MGP.html')
    html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MGP | Report de Lançamento</title>
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
        
        .week-content {{
            padding: 25px;
            display: grid;
            grid-template-columns: 1fr;
            gap: 24px;
            align-items: start;
        }}

        .metric-list {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}

        .metric-list li {{
            padding: 12px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 13px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .metric-list li b {{
            color: var(--text-gray-light);
            font-weight: 500;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .metric-list li span {{
            font-weight: 700;
            color: var(--text-white);
            text-align: right;
            font-size: 14px;
        }}

        .highlight-green {{ color: #4ADE80; }}
        .highlight-blue {{ color: #3B82F6; }}
        .highlight-red {{ color: var(--revo-red-base); }}

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

        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{ text-align: left; padding: 12px; color: var(--text-gray-dark); font-size: 10px; text-transform: uppercase; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.05); }}

        .falling-pattern-anim {{
            position: fixed;
            width: 100%;
            height: 100%;
            top: 0; left: 0;
            z-index: 0;
            opacity: 0.2;
            pointer-events: none;
            background-image:
                radial-gradient(4px 100px at 0px 235px, var(--revo-red-base), transparent),
                radial-gradient(4px 100px at 300px 235px, var(--revo-red-base), transparent),
                radial-gradient(2px 2px at 150px 117.5px, var(--revo-red-base) 100%, transparent 150%);
            background-size: 300px 235px, 300px 235px, 300px 235px;
            animation: fall 150s linear infinite;
        }}

        @keyframes fall {{
            100% {{ background-position: 0px 6800px, 3px 6800px, 151.5px 6917.5px; }}
        }}
    </style>
</head>
<body>
<div class="falling-pattern-anim"></div>
<div class="dashboard-container">
    <div class="header">
        <div class="top-badge">Lançamento Meteórico</div>
        <h1>Report de <span>Lançamento.</span></h1>
        <p>Abertura do Carrinho em: <strong>30/03/2026</strong> | Produto Master: <strong>Método Gerente de Pasto</strong></p>
    </div>

    <!-- RESUMO DE KPIs -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px;">
        <div style="background: var(--card-bg); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; border-top: 3px solid var(--revo-red-base);">
            <div style="font-size: 11px; text-transform: uppercase; color: var(--text-gray-dark); letter-spacing: 1px; margin-bottom: 8px;">Faturamento Bruto</div>
            <div style="font-size: 28px; font-weight: 800; color: var(--text-white);">{format_currency(faturamento_bruto)}</div>
            <div style="font-size: 12px; color: var(--text-gray-light); margin-top: 4px;">Comissão Líq: {format_currency(comissao_liquida_total)}</div>
        </div>
        <div style="background: var(--card-bg); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; border-top: 3px solid var(--revo-red-base);">
            <div style="font-size: 11px; text-transform: uppercase; color: var(--text-gray-dark); letter-spacing: 1px; margin-bottom: 8px;">Investimento Total</div>
            <div style="font-size: 28px; font-weight: 800;">{format_currency(investimento_total)}</div>
            <div style="font-size: 12px; color: var(--text-gray-light); margin-top: 4px;">CPL Meta: {format_currency(cpl_meta_ads)}</div>
        </div>
        <div style="background: var(--card-bg); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; border-top: 3px solid var(--revo-red-base);">
            <div style="font-size: 11px; text-transform: uppercase; color: var(--text-gray-dark); letter-spacing: 1px; margin-bottom: 8px;">ROAS</div>
            <div style="font-size: 26px; font-weight: 800; margin-bottom: 4px;">{roas_bruto:.2f} <span style="font-size: 14px; font-weight: 400; color: var(--text-gray-dark);">Bruto</span></div>
            <div style="font-size: 20px; font-weight: 800; color: #CCCCCC;">{roas_liquido:.2f} <span style="font-size: 12px; font-weight: 400; color: var(--text-gray-dark);">Líquido</span></div>
        </div>
        <div style="background: var(--card-bg); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; border-top: 3px solid var(--revo-red-base);">
            <div style="font-size: 11px; text-transform: uppercase; color: var(--text-gray-dark); letter-spacing: 1px; margin-bottom: 8px;">CONVERSÃO</div>
            <div style="font-size: 26px; font-weight: 800;">{conversao_geral:.2f}% <span style="font-size: 14px; font-weight: 400; color: var(--text-gray-dark);">Geral</span></div>
            <div style="font-size: 18px; font-weight: 800; color: #CCCCCC;">{conversao_trafego:.2f}% <span style="font-size: 12px; font-weight: 400; color: var(--text-gray-dark);">Tráfego</span></div>
        </div>
    </div>

    <details open>
        <summary>RESULTADOS DO LANÇAMENTO</summary>
        <div class="details-content">
            
            <!-- CAPTAÇÃO -->
            <details class="week-toggle" open>
                <summary>Captação de Leads (Real vs Meta)</summary>
                <div class="week-content">
                    <div style="border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid var(--revo-red-base); background-color: var(--card-bg); border-radius: 8px; padding: 25px;">
                        <ul class="metric-list">
                            <li><b>Investimento em Captação</b> <span>{format_currency(investimento_total)}</span></li>
                            <li><b>Total de Leads (Base Total)</b> <span class="highlight-blue">{total_leads_real} leads</span></li>
                            <li><b>Total de Leads (Meta ads)</b> <span>{int(total_leads_meta)} leads</span></li>
                            <li><b>CPL Médio (Real)</b> <span class="highlight-red">{format_currency(cpl_real)}</span></li>
                            <li><b>CPL Médio (Meta ads)</b> <span>{format_currency(cpl_meta_ads)}</span></li>
                        </ul>
                        <div class="insight-box">
                            <strong>Melhores Criativos (Real Leads)</strong>
                            <table>
                                <thead>
                                    <tr><th>Criativo</th><th>Leads</th><th>Invest.</th><th>CPL Real</th></tr>
                                </thead>
                                <tbody>
"""
    for _, row in top_5_criativos.iterrows():
        link_html = f"<a href='{row['Link Criativo']}' target='_blank' style='color: var(--revo-red-base); text-decoration: none; border: 1px solid rgba(224,0,0,0.2); padding: 2px 6px; border-radius: 4px; background: rgba(224,0,0,0.05);'>{row['Criativo']}</a>" if pd.notna(row['Link Criativo']) and row['Link Criativo'] != "" else row['Criativo']
        html_content += f"<tr><td>{link_html}</td><td>{int(row['Leads Real Count'])}</td><td>{format_currency(row['Invest Num'])}</td><td class='highlight-red'>{format_currency(row['CPL Real'])}</td></tr>"
        
    html_content += f"""
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </details>

            <!-- VENDAS -->
            <details class="week-toggle" open>
                <summary>Vendas e Conversão</summary>
                <div class="week-content">
                    <div style="border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid #4ADE80; background-color: var(--card-bg); border-radius: 8px; padding: 25px;">
                        <ul class="metric-list">
                            <li><b>Faturamento Bruto</b> <span class="highlight-green">{format_currency(faturamento_bruto)}</span></li>
                            <li><b>Comissão Líquida</b> <span class="highlight-green">{format_currency(comissao_liquida_total)}</span></li>
                            <li><b>Total de Vendas Aprovadas</b> <span>{total_vendas} vendas</span></li>
                            <li><b>Vendas Diretas de Tráfego [RA]</b> <span class="highlight-blue">{total_vendas_trafego} vendas</span></li>
                            <li><b>ROAS Bruto / Líquido</b> <span>{roas_bruto:.2f}x / {roas_liquido:.2f}x</span></li>
                            <li><b>Conversão Geral (Vendas/Base Total)</b> <span>{conversao_geral:.2f}%</span></li>
                            <li><b>Conversão de Tráfego (Leads [RA])</b> <span class="highlight-blue">{conversao_trafego:.2f}%</span></li>
                            <li><b>Ticket Médio</b> <span>{format_currency(ticket_medio)}</span></li>
                        </ul>
                        <div class="insight-box" style="border-left-color: #4ADE80;">
                            <strong>Análise de Pagamentos</strong>
                            Pix: {pix_perc:.1f}% | Cartão: {cc_perc:.1f}%
                        </div>
                    </div>
                </div>
            </details>

        </div>
    </details>
</div>
</body>
</html>
"""

    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("✅ Automação concluída!")
    print(f"Relatório gerado em: {base_dir}")

if __name__ == "__main__":
    main()
