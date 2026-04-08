import csv
import re
from collections import Counter
from datetime import datetime

csv_path = "/Users/regisprado/Library/CloudStorage/GoogleDrive-contato@revoadvisory.com.br/Shared drives/REVO Advisory/2. Clientes/Ativos/0. Mozini Advocacia/Interno/Arquivos/Mozini Advocacia | Leads Kommo | Mar 2026.csv"
output_path = "/Users/regisprado/Library/CloudStorage/GoogleDrive-contato@revoadvisory.com.br/Shared drives/REVO Advisory/2. Clientes/Ativos/0. Mozini Advocacia/Interno/⚙️ Aurora — Não Mexer/memories/Mozini Advocacia | Etapa 1 - Padrões de Fechamento.md"

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

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%d.%m.%Y %H:%M:%S')
    except ValueError:
        return None

def main():
    closed_leads = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # normalize field names
        fieldnames = [k.strip() if k else '' for k in reader.fieldnames]
        reader.fieldnames = fieldnames
        
        for row in reader:
            if row.get('Etapa do lead', '').strip() == 'Contrato Fechado':
                closed_leads.append(row)
                
    states_counter = Counter()
    ddds_counter = Counter()
    problems_counter = Counter()
    origins_counter = Counter()
    close_times = []
    
    for lead in closed_leads:
        # Check all possible phone fields
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
        states_counter[state] += 1
        if ddd:
            ddds_counter[ddd] += 1
            
        origem = lead.get('[MA] Origem', '').strip()
        origem = origem if origem else 'Desconhecida'
        origins_counter[origem] += 1
        
        problema = lead.get('[MA] Problema', '').strip()
        problema = problema if problema else 'Não preenchido'
        problems_counter[problema] += 1
        
        created_at = parse_date(lead.get('Criado em', ''))
        closed_at = parse_date(lead.get('Fechado às', ''))
        
        if created_at and closed_at:
            days = (closed_at - created_at).days
            close_times.append(days)

    avg_close_time = sum(close_times) / len(close_times) if close_times else 0
    close_times.sort()
    median_close_time = close_times[len(close_times)//2] if close_times else 0

    md_content = f"""# Mozini Advocacia | Etapa 1 — Padrões e Perfil do Comprador

> **Agente:** Copywriter REVO
> **Objetivo:** Mapear o perfil do cliente ideal com base nos {len(closed_leads)} contratos fechados (Extraídos do Kommo).
> **Data:** 05/Mar/2026

## 🎯 Perfil do Comprador (Quem Compra)

### 📍 Padrão Geográfico
A análise dos DDDs dos {len(closed_leads)} clientes que assinaram contrato revela onde a demanda é mais forte:
"""
    
    for state, count in states_counter.most_common():
        pct = (count / len(closed_leads)) * 100
        md_content += f"- **{state}**: {count} clientes ({pct:.1f}%)\n"
        
    md_content += "\n**Top 5 DDDs (Cidades Específicas):**\n"
    for ddd, count in ddds_counter.most_common(5):
        md_content += f"- **DDD {ddd}**: {count} clientes\n"
        
    md_content += f"""
### ⚖️ Tipo de Problema (Qual dor resolvemos)
O que os clientes que assinaram estavam buscando?
"""
    for prob, count in problems_counter.most_common():
        pct = (count / len(closed_leads)) * 100
        md_content += f"- **{prob}**: {count} clientes ({pct:.1f}%)\n"
        
    md_content += f"""
### 🚦 Origem do Lead (Por onde vieram)
De onde vieram os leads que de fato converteram em caixa?
"""
    for orig, count in origins_counter.most_common():
        pct = (count / len(closed_leads)) * 100
        md_content += f"- **{orig}**: {count} clientes ({pct:.1f}%)\n"
        
    md_content += f"""
### ⏱️ Jornada de Compra (Tempo de Decisão)
Tempo médio entre o lead entrar e o contrato ser assinado:
- **Tempo Médio:** {avg_close_time:.1f} dias
- **Mediana (Mais comum):** {median_close_time:.1f} dias

---
> [!NOTE]
> **Check-point 1:** Este é o extrato do comportamento de compra real. Vamos avançar para a Etapa 2 (Data Analyst) onde cruzaremos isso com os LEADS QUE NÃO FECHARAM para entender gargalos.
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    print("Done")

if __name__ == "__main__":
    main()
