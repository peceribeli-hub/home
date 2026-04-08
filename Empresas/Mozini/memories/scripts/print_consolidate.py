import csv
import os
from datetime import datetime

folder = '/Users/regisprado/Library/CloudStorage/GoogleDrive-contato@revoadvisory.com.br/Shared drives/REVO Advisory/2. Clientes/Ativos/0. Mozini Advocacia/Interno/Financeiro e Metas'

def parse_money(val, is_american=False):
    if not val: return 0.0
    val_str = str(val).replace('R$', '').strip()
    if is_american:
        try: return float(val_str)
        except: return 0.0
    else:
        val_str = val_str.replace('.', '').replace(',', '.')
        try: return float(val_str)
        except: return 0.0

cash_collect = {m: 0.0 for m in range(1, 13)}
faturamento = {m: 0.0 for m in range(1, 13)}

# 1. Asaas
try:
    with open(os.path.join(folder, 'Extrato Asaas.csv'), 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i in range(2): 
            try: next(reader)
            except: pass
        for row in reader:
            if not row or len(row) < 12: continue
            data_str = row[0].strip()
            tipo_transacao = row[2].strip()
            # Foco apenas no que = Recebimento de fato do cliente
            is_cobranca = "Cobrança recebida" in tipo_transacao
            is_pix_in = "Transação via Pix" in tipo_transacao and row[11].strip() == "Crédito"
            
            if is_cobranca or is_pix_in:
                val = parse_money(row[5], is_american=True)
                if data_str and val > 0:
                    try:
                        dt = datetime.strptime(data_str, '%d/%m/%Y')
                        if dt.year == 2025:
                            cash_collect[dt.month] += val
                    except:
                        pass
except Exception as e: print("Erro Asaas:", e)

# 2. Daily
try:
    with open(os.path.join(folder, 'Mozini Advocacia _ Daily - Dia\u0301ria.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data_str = row.get('Data', '').strip()
            if not data_str: continue
            try:
                dt = datetime.strptime(data_str, '%d/%m/%Y')
                if dt.year == 2025:
                    m = dt.month
                    faturamento[m] += parse_money(row.get(' Faturamento ', 0), is_american=False)
            except Exception as ex:
                pass
except Exception as e: print("Erro Daily:", e)

meses_nomes = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
print(f"{'Mês':<12} | {'Cash Collect (Real)':<20} | {'Faturamento (Ads)':<20}")
print("-" * 60)
for m in range(1, 13):
    if cash_collect[m] > 0 or faturamento[m] > 0:
        print(f"{meses_nomes[m-1]:<12} | R$ {cash_collect[m]:<17,.2f} | R$ {faturamento[m]:<17,.2f}")
