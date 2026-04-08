import pandas as pd
import numpy as np
import os
import re

def clean_currency(x):
    if isinstance(x, str):
        x = x.replace('R$', '').replace('.', '').replace(',', '.').strip()
        try:
            return float(x)
        except:
            return 0.0
    return float(x) if pd.notnull(x) else 0.0

def double_check_id(row):
    # Create a unique ID from the last 8 digits of phone + first part of name
    phone = str(row.get('Telefone', ''))
    phone_digits = ''.join(filter(str.isdigit, phone))
    last_8 = phone_digits[-8:] if len(phone_digits) >= 8 else phone_digits
    
    name = str(row.get('Nome', ''))
    first_name = name.split(' ')[0].lower() if name else ''
    return f"{last_8}_{first_name}"

def main():
    base_dir = r'/Users/paola/Downloads/Antigravity/Paola (me baixe)/Lançamento NF'
    vendas_path = os.path.join(base_dir, 'Dados Vendas.csv')
    meta_ads_path = os.path.join(base_dir, 'Dados Meta Ads.csv')
    leads_path = os.path.join(base_dir, 'Dados Leads.csv')
    pesquisa_path = os.path.join(base_dir, 'Dados Pesquisa Imersão.csv')
    
    df_vendas = pd.read_csv(vendas_path)
    df_meta = pd.read_csv(meta_ads_path)
    df_leads = pd.read_csv(leads_path)
    df_pesquisa = pd.read_csv(pesquisa_path)

    for col in [' Faturamento Total ', ' Comissão Líquida ', ' Taxas ', ' Faturamento Ingresso ', ' Faturamento OB ', ' Investimento ']:
        if col in df_vendas.columns:
            df_vendas[col] = df_vendas[col].apply(clean_currency)
        if col in df_meta.columns:
            df_meta[col] = df_meta[col].apply(clean_currency)

    df_vendas_aprovadas = df_vendas[df_vendas['Status'] == 'Aprovada'].copy()
    
    # --- 1. Financial metrics ---
    print("\n=== 1. FINANCIAL METRICS ===")
    total_rev = df_vendas_aprovadas[' Faturamento Total '].sum()
    ingresso_rev = df_vendas_aprovadas[df_vendas_aprovadas['Produto'].str.contains('Imersão', na=False)][' Faturamento Ingresso '].sum()
    ob_rev = df_vendas_aprovadas[df_vendas_aprovadas['Produto'].str.contains('Imersão', na=False)][' Faturamento OB '].sum()
    commissions = df_vendas_aprovadas[' Comissão Líquida '].sum()
    investments = df_meta[' Investimento '].sum()
    roas = total_rev / investments if investments > 0 else 0
    
    vendas_imersao = df_vendas_aprovadas[df_vendas_aprovadas['Produto'].str.contains('Imersão', na=False)].shape[0]
    vendas_xrpec = df_vendas_aprovadas[df_vendas_aprovadas['Produto'].str.contains('xR Pec', na=False)].shape[0]
    ticket_medio = total_rev / (vendas_imersao + vendas_xrpec) if (vendas_imersao + vendas_xrpec) > 0 else 0
    cac = investments / vendas_imersao if vendas_imersao > 0 else 0

    print(f"Totais Faturamento: R$ {total_rev:.2f}")
    print(f"Faturamento Ingressos + OB: R$ {ingresso_rev + ob_rev:.2f}")
    print(f"Commissions: R$ {commissions:.2f}")
    print(f"Investments: R$ {investments:.2f}")
    print(f"ROAS: {roas:.2f}x")
    print(f"Ticket Médio: R$ {ticket_medio:.2f}")
    print(f"CAC (Imersão): R$ {cac:.2f}")

    # --- 2. Ad creatives analysis ---
    print("\n=== 2. AD CREATIVES ANALYSIS ===")
    # Remove totals/empty
    df_meta_valid = df_meta[df_meta['Criativo'].notna()].copy()
    
    # Clean creative name for grouping (e.g. 'AD006 - Imersão prática 1 dia - L0' -> 'AD006 - Imersão prática 1 dia')
    def get_base_criativo(name):
        name = str(name).strip()
        # Remove trailing variations like ' - L0', ' - L1', ' VAR1', etc.
        name = re.sub(r'\s*-\s*[A-Z\d]+\s*$', '', name)
        name = re.sub(r'\s*VAR\d+\s*', ' ', name)
        # Fix AD006 specific case if it wasn't caught
        if 'AD006' in name:
            name = 'AD006 - Imersão prática 1 dia'
        return name.strip()

    df_meta_valid['Base_Criativo'] = df_meta_valid['Criativo'].apply(get_base_criativo)

    # Top 5 Ingressos CPA
    sales_col = [c for c in df_meta.columns if 'Vendas' in c and '(real)' in c]
    if sales_col:
        # Group by Base_Criativo
        grouped_cpa = df_meta_valid.groupby('Base_Criativo').agg({
            ' Investimento ': 'sum',
            sales_col[0]: 'sum'
        }).reset_index()
        
        grouped_cpa['CPA'] = grouped_cpa[' Investimento '] / grouped_cpa[sales_col[0]].replace(0, np.nan)
        top5_cpa = grouped_cpa[grouped_cpa[sales_col[0]] > 0].sort_values('CPA').head(5)[['Base_Criativo', ' Investimento ', sales_col[0], 'CPA']]
        print("Top 5 Ingressos CPA (Merged):")
        print(top5_cpa.to_string(index=False))

    # Video vs Estático
    df_meta_valid['Type'] = df_meta_valid['Criativo'].apply(lambda x: 'Video' if 'VD' in str(x).upper() else 'Estático')
    
    if sales_col:
        # Group Video
        vid_df = df_meta_valid[df_meta_valid['Type'] == 'Video']
        grouped_vid = vid_df.groupby('Base_Criativo').agg({' Investimento ': 'sum', sales_col[0]: 'sum'}).reset_index()
        grouped_vid['CPA'] = grouped_vid[' Investimento '] / grouped_vid[sales_col[0]].replace(0, np.nan)
        top3_video = grouped_vid[grouped_vid[sales_col[0]] > 0].sort_values('CPA').head(3)[['Base_Criativo', ' Investimento ', sales_col[0], 'CPA']]
        print("\nTop 3 Videos CPA (Merged):")
        print(top3_video.to_string(index=False))
        
        # Group Static
        est_df = df_meta_valid[df_meta_valid['Type'] == 'Estático']
        grouped_est = est_df.groupby('Base_Criativo').agg({' Investimento ': 'sum', sales_col[0]: 'sum'}).reset_index()
        grouped_est['CPA'] = grouped_est[' Investimento '] / grouped_est[sales_col[0]].replace(0, np.nan)
        top3_estatico = grouped_est[grouped_est[sales_col[0]] > 0].sort_values('CPA').head(3)[['Base_Criativo', ' Investimento ', sales_col[0], 'CPA']]
        print("\nTop 3 Estáticos CPA (Merged):")
        print(top3_estatico.to_string(index=False))

    type_stats = df_meta_valid.groupby('Type')[' Investimento '].sum()
    print("\nInvestimento Geral Video vs Estático:")
    print(type_stats)
    
    # Top 3 ROAS Total
    roas_col = [c for c in df_meta.columns if 'Faturamento (Bruto)' in c]
    if roas_col:
        df_meta_valid[roas_col[0]] = df_meta_valid[roas_col[0]].apply(clean_currency)
        grouped_roas = df_meta_valid.groupby('Base_Criativo').agg({
            ' Investimento ': 'sum',
            roas_col[0]: 'sum'
        }).reset_index()
        
        grouped_roas['ROAS_criativo'] = grouped_roas[roas_col[0]] / grouped_roas[' Investimento '].replace(0, np.nan)
        top3_roas = grouped_roas.sort_values('ROAS_criativo', ascending=False).head(3)[['Base_Criativo', 'ROAS_criativo']]
        print("\nTop 3 ROAS Total (Merged):")
        print(top3_roas.to_string(index=False))

    # --- 3. Persona Analysis ---
    print("\n=== 3. PERSONA ANALYSIS ===")
    # Join Vendas Imersão & xR Pec with Pesquisa
    df_pesquisa['Email'] = df_pesquisa['E-mail Cadastrado'].str.lower().str.strip()
    df_vendas_aprovadas['Email'] = df_vendas_aprovadas['Email'].str.lower().str.strip()
    
    merged = pd.merge(df_vendas_aprovadas, df_pesquisa, on='Email', how='inner')
    
    xr_pec_buyers = merged[merged['Produto'].str.contains('xR Pec', na=False)]
    imersao_buyers = merged[merged['Produto'].str.contains('Imersão', na=False)]
    
    print(f"Total Pesquisas Cruzadas com Vendas: {merged.shape[0]}")
    desc_col = 'Qual dessas descrições se parece mais com a sua realidade?'
    if desc_col in imersao_buyers.columns:
        print("\nTop 3 Atuações (Imersão):")
        print(imersao_buyers[desc_col].value_counts(normalize=True).head(3) * 100)
        
    if desc_col in xr_pec_buyers.columns and not xr_pec_buyers.empty:
        print("\nTop 3 Atuações (xR Pec Lite):")
        print(xr_pec_buyers[desc_col].value_counts(normalize=True).head(3) * 100)

    # --- 4. Funnel conversion rates ---
    print("\n=== 4. FUNNEL CONVERSION RATES ===")
    # Combo vs Ingresso vs Gravação -> check 'Oferta' or 'Orderbumps'
    leads_capturados = df_leads.shape[0]
    print(f"Leads Capturados: {leads_capturados}")
    
    # Order bumps adoption
    vendas_imersao_df = df_vendas_aprovadas[df_vendas_aprovadas['Produto'].str.contains('Imersão', na=False)]
    has_ob = vendas_imersao_df[vendas_imersao_df['Orderbumps'].notna() & (vendas_imersao_df['Orderbumps'] != '')]
    print(f"Conversão Lead -> Ingresso: {(vendas_imersao / leads_capturados * 100):.1f}%")
    print(f"Adoção de Order Bumps Total: {has_ob.shape[0]} compradores ({(has_ob.shape[0]/vendas_imersao * 100):.1f}%)")
    
    print("Detalhamento de Order Bumps (Adoção Única ou Combo):")
    ob_counts = has_ob['Orderbumps'].value_counts()
    for ob_name, count in ob_counts.items():
        print(f" - {ob_name}: {count} compradores ({(count/vendas_imersao * 100):.1f}%)")
        
    print(f"\nConversão Upsell (xR Pec Lite): {vendas_xrpec} compradores ({(vendas_xrpec/vendas_imersao * 100):.1f}%)")

    # --- 5. Cohort / Lotes with double check ---
    print("\n=== 5. COHORT / LOTES (Double Check) ===")
    df_vendas_aprovadas['DoubleCheckID'] = df_vendas_aprovadas.apply(double_check_id, axis=1)
    
    df_imersao = df_vendas_aprovadas[df_vendas_aprovadas['Produto'].str.contains('Imersão', na=False)]
    df_xrpec = df_vendas_aprovadas[df_vendas_aprovadas['Produto'].str.contains('xR Pec', na=False)]
    
    # Map doublecheck IDs of XR Pec buyers
    xrpec_ids = set(df_xrpec['DoubleCheckID'].tolist())
    xrpec_emails = set(df_xrpec['Email'].tolist())
    
    df_imersao['Comprou_Upsell'] = df_imersao.apply(
        lambda row: row['DoubleCheckID'] in xrpec_ids or row['Email'] in xrpec_emails, axis=1
    )
    
    cohort_stats = df_imersao.groupby('Oferta').agg(
        Ingressos=('DoubleCheckID', 'count'),
        Upsells=('Comprou_Upsell', 'sum')
    ).reset_index()
    
    cohort_stats['Lote_Num'] = cohort_stats['Oferta'].str.extract('(\d+)').astype(float)
    cohort_stats = cohort_stats.sort_values('Lote_Num').drop('Lote_Num', axis=1)
    
    cohort_stats['Conversao_Upsell_%'] = (cohort_stats['Upsells'] / cohort_stats['Ingressos'] * 100).round(1)
    
    print(cohort_stats.to_string(index=False))


if __name__ == '__main__':
    main()
