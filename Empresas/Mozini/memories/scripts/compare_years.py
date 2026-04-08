import csv
import os
from datetime import datetime

folder = '/Users/regisprado/Library/CloudStorage/GoogleDrive-contato@revoadvisory.com.br/Shared drives/REVO Advisory/2. Clientes/Ativos/0. Mozini Advocacia/Interno/Financeiro e Metas'

def parse_money(val, is_american=False):
    if not val: return 0.0
    val_str = str(val).replace('+', '').replace('R$', '').replace('R$ ', '').strip()
    if is_american:
        try: return float(val_str)
        except: return 0.0
    else:
        val_str = val_str.replace(' ', '').replace('.', '').replace(',', '.')
        try: return float(val_str)
        except: return 0.0

anos = [2024, 2025, 2026]
metricas = {
    ano: {
        'cash_collect': {m: 0.0 for m in range(1, 13)},
        'faturamento': {m: 0.0 for m in range(1, 13)},
        'custos': {m: 0.0 for m in range(1, 13)},
        'investimento': {m: 0.0 for m in range(1, 13)},
        'lucro_distribuido': {m: 0.0 for m in range(1, 13)},
        'cash_collect_asaas': {m: 0.0 for m in range(1, 13)},
        'cash_collect_infinite': {m: 0.0 for m in range(1, 13)},
        'cash_collect_duplicado': {m: 0.0 for m in range(1, 13)}
    }
    for ano in anos
}

asaas_entries = [] 
infinitepay_entries = []

# 1. Asaas (Cash Collect E Custos)
try:
    with open(os.path.join(folder, 'Extrato Asaas.csv'), 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for _ in range(2): 
            try: next(reader)
            except: pass
        for row in reader:
            if not row or len(row) < 12: continue
            data_str = row[0].strip()
            tipo_transacao = row[2].strip()
            val = parse_money(row[5], is_american=True)
            tipo_lancamento = row[11].strip()
            
            try:
                dt = datetime.strptime(data_str, '%d/%m/%Y')
                ano = dt.year
                m = dt.month
                if ano in anos:
                    if tipo_lancamento == "Crédito":
                        # Apenas Cobrança Recebida bate exato com os 124K do print do Asaas
                        if "Cobrança recebida" in tipo_transacao:
                            if val > 0:
                                asaas_entries.append({'data': dt, 'valor': val, 'tipo': 'Asaas'})
                                metricas[ano]['cash_collect_asaas'][m] += val
                    
                    elif tipo_lancamento == "Débito":
                        tipo_lower = tipo_transacao.lower()
                        # Se for taxa explícita do Asaas (Taxa de boleto, Taxa do Pix, etc)
                        if "taxa" in tipo_lower:
                            metricas[ano]['custos'][m] += val
                        else:
                            # Transferência, Pix enviado ou Pagamento de Conta (Ex: Aluguel) -> Retiradas
                            metricas[ano]['lucro_distribuido'][m] += val
            except:
                pass
except Exception as e: print("Erro Asaas:", e)

# 2. InfinitePay (Apenas Cash Collect)
infinite_pay_path = os.path.join(folder, 'relato\u0301rio.csv') # O Mac converte o acento em \u0301 as vezes
if os.path.exists(infinite_pay_path):
    try:
        with open(infinite_pay_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data_str = row.get('Data', '').strip()
                tipo_transacao = row.get('Tipo de transação', '').strip()
                
                # Vamos considerar as vendas processadas pela infinitepay
                if tipo_transacao == 'Depósito de vendas' or row.get('Nome', '') == 'Vendas':
                    valor_str = row.get('Valor', '').strip()
                    val = parse_money(valor_str)
                    if data_str and val > 0:
                        try:
                            # Formato da data na InfinitePay nova: YYYY-MM-DD
                            dt = datetime.strptime(data_str, '%Y-%m-%d')
                            if dt.year in anos:
                                infinitepay_entries.append({'data': dt, 'valor': val, 'tipo': 'InfinitePay'})
                                metricas[dt.year]['cash_collect_infinite'][dt.month] += val
                        except Exception as dt_err: 
                            pass
    except Exception as e: print("Erro InfinitePay:", e)

# 3. Deduplicação Cash Collect (Corrigida e Definitiva)
# DESCOBERTA: A Bruna gera uma "Cobrança" no Asaas e paga com o saldo da InfinitePay.
# Ou seja, os 124.947,86 do Asaas JÁ CONTÊM 100% das vendas da InfinitePay!
# Para mostrar separado sem inflar, vamos identificar no Asaas o que foi transferência dela (InfinitePay)
# e o que foi de Fatura Direta de Cliente (Asaas Puro).

# 3. Deduplicação Cash Collect (Corrigida e Definitiva)
# DESCOBERTA: A Bruna gera uma "Cobrança" no Asaas e paga com o saldo da InfinitePay.
# Ou seja, os 124.947,86 do Asaas JÁ CONTÊM 100% das vendas da InfinitePay!
# Para manter a métrica pura e idêntica ao Asaas:
for ano in anos:
    for m in range(1, 13):
        metricas[ano]['cash_collect'][m] = metricas[ano]['cash_collect_asaas'][m]
        # Aqui, o "duplicado" é na verdade 100% da InfinitePay que já está no Asaas.
        metricas[ano]['cash_collect_duplicado'][m] = metricas[ano]['cash_collect_infinite'][m]

# 4. Investimento Ads (Daily Diária)
try:
    arquivo_google = os.path.join(folder, 'Mozini Advocacia _ Daily - 📈 Dados _ Google.csv')
    if os.path.exists(arquivo_google):
        with open(arquivo_google, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data_str = row.get('Data', '').strip()
                if not data_str:
                    continue
                try:
                    dt = datetime.strptime(data_str, '%d/%m/%Y')
                    if dt.year in anos:
                        val_str = row.get(' Investimento ', '').strip()
                        val = parse_money(val_str, is_american=False)
                        metricas[dt.year]['investimento'][dt.month] += val
                except ValueError:
                    pass
                    
    arquivo_meta = os.path.join(folder, 'Mozini Advocacia _ Daily - 📈 Dados _ Meta Ads.csv')
    if os.path.exists(arquivo_meta):
        with open(arquivo_meta, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data_str = row.get('Data', '').strip()
                if not data_str:
                    continue
                try:
                    dt = datetime.strptime(data_str, '%d/%m/%Y')
                    if dt.year in anos:
                        val_str = row.get('Investimento', '').strip()
                        val = parse_money(val_str, is_american=False)
                        metricas[dt.year]['investimento'][dt.month] += val
                except ValueError:
                    pass
except Exception as e: print("Erro Daily:", e)

# 5. Faturamento Real (Leads Whatsapp) - Ajustado para Data de Recebimento
try:
    with open(os.path.join(folder, 'Mozini Advocacia _ Daily - Leads _ Whatsapp.csv'), 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # User pediu "data de recebimento como referencia". 
            # Na planilha, as colunas sao: 'Data Reunião Realizada', ' Recebimento Reunião ', 'Data Contrato Fechado', etc.
            data_str = row.get(' Recebimento Reunião ', '').strip()
            if not data_str:
                data_str = row.get('Data Reunião Realizada', '').strip()
            if not data_str:
                data_str = row.get('Data Contrato Fechado', '').strip()
            
            if not data_str: continue
            
            try:
                dt = datetime.strptime(data_str.split(' ')[0], '%d/%m/%Y')
                ano = dt.year
                if ano in anos:
                    m = dt.month
                    val = parse_money(row.get(' Valor Total Contrato ', ''), is_american=False)
                    metricas[ano]['faturamento'][m] += val
            except Exception as ex:
                pass
except Exception as e: print("Erro Leads Whatsapp:", e)


# Print Results
meses_nomes = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

for ano in anos:
    print(f"\n======================================")
    print(f"       ANALISE ANO {ano}")
    print(f"======================================")
    print(f"{'Mês':<12} | {'Asaas':<12} | {'Inf.Pay':<10} | {'(-Dedup)':<10} | {'CC Líquido':<12} | {'Faturamento':<12} | {'Custos':<9} | {'Inv(Ads)':<9} | {'Margem Oper.':<14} | {'(Saque)'}")
    print("-" * 135)
    
    total_asaas = 0
    total_inf = 0
    total_dedup = 0
    total_cc = 0
    total_custos = 0
    total_inv = 0
    total_fat = 0
    total_margem = 0
    total_saque = 0

    for m in range(1, 13):
        asaas = metricas[ano]['cash_collect_asaas'][m]
        inf = metricas[ano]['cash_collect_infinite'][m]
        dedup = metricas[ano]['cash_collect_duplicado'][m]
        cc = metricas[ano]['cash_collect'][m]
        custos = abs(metricas[ano]['custos'][m]) # Treat as positive for math
        inv = metricas[ano]['investimento'][m]
        fat = metricas[ano]['faturamento'][m]
        saque = abs(metricas[ano]['lucro_distribuido'][m])
        
        margem = cc - custos - inv
        
        total_asaas += asaas
        total_inf += inf
        total_dedup += dedup
        total_cc += cc
        total_custos += custos
        total_inv += inv
        total_fat += fat
        total_margem += margem
        total_saque += saque

        if cc > 0 or fat > 0 or custos > 0:
             print(f"{meses_nomes[m-1]:<12} | R$ {asaas:<9,.2f} | R$ {inf:<7,.2f} | R$ {dedup:<7,.2f} | R$ {cc:<9,.2f} | R$ {fat:<9,.2f} | R$ {custos:<6,.2f} | R$ {inv:<6,.2f} | R$ {margem:<11,.2f} | (R$ {saque:,.2f})")
    
    print("-" * 135)
    print(f"{'TOTAL ANO':<12} | R$ {total_asaas:<9,.2f} | R$ {total_inf:<7,.2f} | R$ {total_dedup:<7,.2f} | R$ {total_cc:<9,.2f} | R$ {total_fat:<9,.2f} | R$ {total_custos:<6,.2f} | R$ {total_inv:<6,.2f} | R$ {total_margem:<11,.2f} | (R$ {total_saque:,.2f})")
