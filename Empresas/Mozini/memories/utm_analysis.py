import csv
from collections import Counter, defaultdict

csv_path = "/Users/regisprado/Library/CloudStorage/GoogleDrive-contato@revoadvisory.com.br/Shared drives/REVO Advisory/2. Clientes/Ativos/0. Mozini Advocacia/Interno/Arquivos/Mozini Advocacia | Leads Kommo | Mar 2026.csv"
output_md_path = "/Users/regisprado/Library/CloudStorage/GoogleDrive-contato@revoadvisory.com.br/Shared drives/REVO Advisory/2. Clientes/Ativos/0. Mozini Advocacia/Interno/⚙️ Aurora — Não Mexer/memories/Mozini Advocacia | Etapa 2.5 - Criativos e Campanhas.md"

def classify_mql_sql(lead):
    qual = lead.get('[MA] Qualificação', '').strip().upper()
    if qual in ['MQL', 'SQL']:
        return qual
    
    etapa = lead.get('Etapa do lead', '').strip().lower()
    
    if etapa == 'contrato fechado' or 'negociação' in etapa or 'reunião' in etapa:
        return 'SQL'
    elif 'resposta inicial' in etapa or 'qualificação' in etapa:
        return 'MQL'
    elif 'venda perdida' in etapa and 'sem legitimidade' not in etapa:
        return 'MQL' 
    
    return 'Lead'

def main():
    leads = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = [k.strip() if k else '' for k in reader.fieldnames]
        reader.fieldnames = fieldnames
        for row in reader:
            leads.append(row)
            
    campaign_stats = defaultdict(lambda: {'Total': 0, 'MQL': 0, 'SQL': 0, 'Contratos': 0})
    content_stats = defaultdict(lambda: {'Total': 0, 'MQL': 0, 'SQL': 0, 'Contratos': 0})

    for lead in leads:
        camp = lead.get('utm_campaign', '').strip() or 'Desconhecida'
        cont = lead.get('utm_content', '').strip() or 'Desconhecido'
        etapa = lead.get('Etapa do lead', '').strip()
        classificacao = classify_mql_sql(lead)
        
        # Only care about Meta or Google where UTMs usually exist
        origem = lead.get('[MA] Origem', '').strip()
        if origem not in ['Meta', 'Google Ads', 'Google', 'Tráfego Agrupado']:
            continue
            
        campaign_stats[camp]['Total'] += 1
        content_stats[cont]['Total'] += 1
        
        if classificacao == 'MQL':
            campaign_stats[camp]['MQL'] += 1
            content_stats[cont]['MQL'] += 1
        elif classificacao == 'SQL':
            campaign_stats[camp]['SQL'] += 1
            content_stats[cont]['SQL'] += 1
            
        if etapa == 'Contrato Fechado':
            campaign_stats[camp]['Contratos'] += 1
            content_stats[cont]['Contratos'] += 1

    # Filter out empty or "Desconhecida" if there's no data
    if 'Desconhecida' in campaign_stats:
        del campaign_stats['Desconhecida']
    if 'Desconhecido' in content_stats:
        del content_stats['Desconhecido']

    md_content = f"""# Mozini Advocacia | Etapa 2.5 — Análise de Campanhas e Criativos

> **Agente:** Copywriter + Data Analyst REVO
> **Objetivo:** Cruzar leads fechados/SQLs com as UTMs de origem para identificar as campanhas e anúncios campeões.
> **Data:** 05/Mar/2026

## 🎯 Top Campanhas (utm_campaign)
Quais campanhas geraram os leads mais qualificados e vendas?

"""
    # Sort by Contratos, then SQLs, then Total
    for camp, stat in sorted(campaign_stats.items(), key=lambda x: (x[1]['Contratos'], x[1]['SQL'], x[1]['Total']), reverse=True):
        if stat['Total'] > 0:
            md_content += f"- **{camp}**: {stat['Total']} Leads | MQL: {stat['MQL'] + stat['SQL']} | SQL: {stat['SQL']} | **Contratos: {stat['Contratos']}**\n"

    md_content += """
## 🎨 Top Criativos/Anúncios (utm_content)
Quais criativos (vídeos/imagens) trouxeram o cliente que compra?

"""
    for cont, stat in sorted(content_stats.items(), key=lambda x: (x[1]['Contratos'], x[1]['SQL'], x[1]['Total']), reverse=True):
        if stat['Total'] > 0:
            md_content += f"- **{cont}**: {stat['Total']} Leads | MQL: {stat['MQL'] + stat['SQL']} | SQL: {stat['SQL']} | **Contratos: {stat['Contratos']}**\n"

    md_content += """
---
## 💡 Insights Iniciais
- **Arquivos disponíveis:** Você pode cruzar os nomes dos criativos (`utm_content`) campeões com os arquivos na pasta interna `Arquivos/Reajuste Abusivo/` para rever a copy exata que o cliente assistiu.
- A partir disso, o **Copywriter** pode identificar os "ganchos" e "ofertas" que mais funcionam e replicá-los na Etapa 3.
"""

    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print(f"Report written to: {output_md_path}")

if __name__ == "__main__":
    main()
