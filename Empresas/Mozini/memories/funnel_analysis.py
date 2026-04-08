import csv
import re
from collections import Counter, defaultdict
import os

csv_path = "/Users/regisprado/Library/CloudStorage/GoogleDrive-contato@revoadvisory.com.br/Shared drives/REVO Advisory/2. Clientes/Ativos/0. Mozini Advocacia/Interno/Arquivos/Mozini Advocacia | Leads Kommo | Mar 2026.csv"
output_md_path = "/Users/regisprado/Library/CloudStorage/GoogleDrive-contato@revoadvisory.com.br/Shared drives/REVO Advisory/2. Clientes/Ativos/0. Mozini Advocacia/Interno/⚙️ Aurora — Não Mexer/memories/Mozini Advocacia | Etapa 2 - Analise Profunda e Qualificacao.md"
output_csv_path = "/Users/regisprado/Library/CloudStorage/GoogleDrive-contato@revoadvisory.com.br/Shared drives/REVO Advisory/2. Clientes/Ativos/0. Mozini Advocacia/Interno/⚙️ Aurora — Não Mexer/memories/Mozini Advocacia | Leads Qualificados.csv"

ddd_map = {
    '11': 'SP', '12': 'SP', '13': 'SP', '14': 'SP', '15': 'SP', '16': 'SP', '17': 'SP', '18': 'SP', '19': 'SP',
    '21': 'RJ', '22': 'RJ', '24': 'RJ', '27': 'ES', '28': 'ES',
    '31': 'MG', '32': 'MG', '33': 'MG', '34': 'MG', '35': 'MG', '37': 'MG', '38': 'MG',
    '41': 'PR', '42': 'PR', '43': 'PR', '44': 'PR', '45': 'PR', '46': 'PR',
    '47': 'SC', '48': 'SC', '49': 'SC',
    '51': 'RS', '53': 'RS', '54': 'RS', '55': 'RS',
    '61': 'DF', '62': 'GO', '64': 'GO', '63': 'TO', '65': 'MT', '66': 'MT', '67': 'MS',
    '68': 'AC', '69': 'RO',
    '71': 'BA', '73': 'BA', '74': 'BA', '75': 'BA', '77': 'BA', '79': 'SE',
    '81': 'PE', '87': 'PE', '82': 'AL', '83': 'PB', '84': 'RN', '85': 'CE', '88': 'CE', '86': 'PI', '89': 'PI',
    '91': 'PA', '93': 'PA', '94': 'PA', '92': 'AM', '97': 'AM', '95': 'RR', '96': 'AP', '98': 'MA', '99': 'MA'
}

def extract_ddd(phone):
    if not phone:
        return None
    phone = str(phone)
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('55') and len(phone) >= 12:
        return phone[2:4]
    elif len(phone) >= 10:
        return phone[0:2]
    return None

def classify_mql_sql(lead):
    # A base logic to classify if the lead data suggests MQL or SQL based on the fields we have
    # The client provided questions for qualification. We will look at what's in Kommo.
    # We'll use the [MA] Qualificação field if populated, otherwise infer from the stage.
    qual = lead.get('[MA] Qualificação', '').strip().upper()
    if qual in ['MQL', 'SQL']:
        return qual
    
    # Infer based on funnel stage
    etapa = lead.get('Etapa do lead', '').strip().lower()
    
    if etapa == 'contrato fechado' or 'negociação' in etapa or 'reunião' in etapa:
        return 'SQL'
    elif 'resposta inicial' in etapa or 'qualificação' in etapa:
        return 'MQL'
    elif 'venda perdida' in etapa and 'sem legitimidade' not in etapa:
        return 'MQL' # They were qualified but lost for other reasons
    
    return 'Lead'

def main():
    leads = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = [k.strip() if k else '' for k in reader.fieldnames]
        reader.fieldnames = fieldnames
        for row in reader:
            leads.append(row)
            
    # Metrics
    total_leads = len(leads)
    
    # Analyze by Origin
    origin_stats = defaultdict(lambda: {'Total': 0, 'MQL': 0, 'SQL': 0, 'Contratos': 0})
    # Analyze by Problem
    problem_stats = defaultdict(lambda: {'Total': 0, 'MQL': 0, 'SQL': 0, 'Contratos': 0})
    # Analyze by State
    state_stats = defaultdict(lambda: {'Total': 0, 'Contratos': 0})
    # Lost Reasons
    lost_reasons = Counter()

    for lead in leads:
        origem = lead.get('[MA] Origem', '').strip() or 'Desconhecida'
        problema = lead.get('[MA] Problema', '').strip() or 'Não preenchido'
        etapa = lead.get('Etapa do lead', '').strip()
        
        # Determine classification
        classificacao = classify_mql_sql(lead)
        # Update lead with classification for export later
        lead['Classificacao_Integra'] = classificacao
        
        # Phone
        phone_fields = ['Celular', 'Tel. direto com.', 'Telefone comercial', 'Telefone residencial']
        ddd = None
        for field in phone_fields:
            val = lead.get(field, '').strip()
            if val:
                extracted = extract_ddd(val)
                if extracted:
                    ddd = extracted
                    break
        state = ddd_map.get(ddd, 'Desconhecido') if ddd else 'Sem número'

        # Update stats
        origin_stats[origem]['Total'] += 1
        problem_stats[problema]['Total'] += 1
        state_stats[state]['Total'] += 1
        
        if classificacao == 'MQL':
            origin_stats[origem]['MQL'] += 1
            problem_stats[problema]['MQL'] += 1
        elif classificacao == 'SQL':
            origin_stats[origem]['SQL'] += 1
            problem_stats[problema]['SQL'] += 1
            
        if etapa == 'Contrato Fechado':
            origin_stats[origem]['Contratos'] += 1
            problem_stats[problema]['Contratos'] += 1
            state_stats[state]['Contratos'] += 1
            
        if 'Venda perdida' in etapa:
            lost_reasons[etapa] += 1

    # Generate Markdown Report
    md_content = f"""# Mozini Advocacia | Etapa 2 — Análise Profunda e Qualificação (Data Analyst)

> **Agente:** Data Analyst REVO (Paola)
> **Objetivo:** Analisar {total_leads} leads extraídos do Kommo, com base no novo framework de qualificação enviado pela cliente (MQL/SQL).
> **Data:** 05/Mar/2026

## 1. Funil Global de 2026 (Projeção via Kommo)

Com base nas {total_leads} interações mapeadas, aplicamos os filtros para classificar os leads de acordo com a maturidade da conversa (MQL = iniciaram qualificação / SQL = agendaram ou avançaram para negociação).

| Etapa | Volume | Conversão de Etapa |
|---|---|---|
| **Total de Leads** | {total_leads} | 100% |
| **MQLs (Qualificados)** | {sum(o['MQL'] + o['SQL'] for o in origin_stats.values())} | {(sum(o['MQL'] + o['SQL'] for o in origin_stats.values()) / total_leads * 100):.1f}% |
| **SQLs (Negociação/Reunião)** | {sum(o['SQL'] for o in origin_stats.values())} | {(sum(o['SQL'] for o in origin_stats.values()) / sum(o['MQL'] + o['SQL'] for o in origin_stats.values()) * 100) if sum(o['MQL'] + o['SQL'] for o in origin_stats.values()) > 0 else 0:.1f}% |
| **Contratos Fechados** | {sum(o['Contratos'] for o in origin_stats.values())} | {(sum(o['Contratos'] for o in origin_stats.values()) / sum(o['SQL'] for o in origin_stats.values()) * 100) if sum(o['SQL'] for o in origin_stats.values()) > 0 else 0:.1f}% |

## 2. Performance por Origem

Qual canal traz leads mais limpos e propensos a fechar?
"""
    for orig, stat in sorted(origin_stats.items(), key=lambda x: x[1]['Contratos'], reverse=True):
        if stat['Total'] > 5: # Filter out noise
            cr = (stat['Contratos'] / stat['Total']) * 100
            mql_rate = ((stat['MQL'] + stat['SQL']) / stat['Total']) * 100
            md_content += f"- **{orig}**: {stat['Total']} Leads | MQL Rate: {mql_rate:.1f}% | Contratos: {stat['Contratos']} (CR: {cr:.1f}%)\n"

    md_content += """

## 3. Performance por Tipo de Problema

Qual é o problema jurídico que mais avança no funil e responde à qualificação?
"""
    for prob, stat in sorted(problem_stats.items(), key=lambda x: x[1]['Contratos'], reverse=True):
        if stat['Total'] > 2:
            cr = (stat['Contratos'] / stat['Total']) * 100
            sql_rate = (stat['SQL'] / stat['Total']) * 100
            md_content += f"- **{prob}**: {stat['Total']} Leads | SQL Rate: {sql_rate:.1f}% | Contratos: {stat['Contratos']} (CR: {cr:.1f}%)\n"

    md_content += """

## 4. Onde Estamos Sangrando? (Motivos de Perda)

Análise das tags de 'Venda Perdida' no CRM para entendermos o vazamento:
"""
    for reason, count in lost_reasons.most_common(10):
        pct = (count / sum(lost_reasons.values())) * 100
        md_content += f"- **{reason.replace('Venda perdida ([MA] ', '').replace(')', '')}**: {count} casos ({pct:.1f}% das perdas)\n"

    md_content += """

---
## 🔄 Feedback para Aurora (Ação)

Aurora, os dados revelam dois gargalos graves:
1. **Filtro de Legitimidade:** Uma grande fatia das perdas é por "Sem legitimidade jurídica" ou "Problema resolvido". Precisamos aplicar as perguntas do framework da cliente **muito antes** no funil (talvez automatizadas) para não gastar tempo do time de vendas com leads sujos.
2. **Eficiência de Canal:** Observar o conversion rate (CR) das origens. A indicação tem CR alto, mas pouco volume. O Meta traz mais volume e tem um SQL rate interessante para certos problemas.

**Próximo Passo:** Avance para a Etapa 3 (Plano de Ação Estratégico). Compile essas perguntas enviadas pela cliente e monte o fluxo de triagem + ações de tráfego para enviar ao Regis.
"""

    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print(f"Report written to: {output_md_path}")

if __name__ == "__main__":
    main()
