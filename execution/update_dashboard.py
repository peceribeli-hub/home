import gspread
import pandas as pd
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime

# Configurações do Projeto
CRED_PATH = '/Users/paola/Downloads/Antigravity/credentials.json'
SHEET_ID = '1KwQPKbyo8pTK2saUVORbywBMIwvqWWQsIREkf2YmAwM'
HTML_PATH = '/Users/paola/Downloads/Antigravity/Empresas/Paola/Dashboard/dashboard_model.html'

def clean_currency(val):
    try:
        val_str = str(val).strip().replace("R$", "").replace(".", "").replace(",", ".").strip()
        return float(val_str) if val_str else 0.0
    except:
        return 0.0

def clean_int(val):
    try:
        return int(str(val).strip().replace(".0", ""))
    except:
        return 0

def clean_float(val):
    try:
        val_str = str(val).strip().replace("%", "").replace(",", ".")
        return float(val_str) if val_str else 0.0
    except:
        return 0.0

def format_brl(val):
    if val is None or val == "-": return "-"
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_roas(val):
    if val is None or val == "-": return "-"
    return f"{val:.2f}x"

def process_data():
    print("Conectando ao Google Sheets...")
    gc = gspread.service_account(filename=CRED_PATH)
    sh = gc.open_by_key(SHEET_ID)
    
    # --- ABA DE VENDAS ---
    print("Processando Vendas (Caixa)...")
    vendas_ws = sh.worksheet("💎 Vendas")
    vendas_data = vendas_ws.get_all_values()
    df_vendas = pd.DataFrame(vendas_data[1:], columns=vendas_data[0])
    
    # Removendo linhas vazias
    df_vendas = df_vendas[df_vendas['Email'].astype(str).str.strip() != '']
    
    # Mapeando colunas de vendas com strip()
    v_cols = {c.strip(): c for c in df_vendas.columns}
    fat_col_v = v_cols.get('Faturamento Total')
    date_col_v = v_cols.get('Data da compra')
    prod_col_v = v_cols.get('Orderbumps', v_cols.get('Produto'))

    df_vendas[fat_col_v] = df_vendas[fat_col_v].apply(clean_currency)
    
    fat_total = df_vendas[fat_col_v].sum()
    ingressos_total = len(df_vendas) 
    
    obs_raw = df_vendas[prod_col_v].fillna("").astype(str).str.lower()
    
    raw_vendas = []
    for _, row in df_vendas.iterrows():
        raw_vendas.append({
            "data": str(row.get(date_col_v, '')).strip(),
            "fat": float(row.get(fat_col_v, 0)),
            "ob": str(row.get(prod_col_v, '')).lower()
        })
    
    ob_gravacao = obs_raw.str.contains("grava").sum()
    ob_ebook = obs_raw.str.contains("book|e-book|ebook").sum()
    ob_planilha = obs_raw.str.contains("planilha").sum()
    ob_combo = obs_raw.str.contains("combo").sum()
    ob_total = ob_gravacao + ob_ebook + ob_planilha + ob_combo

    # --- ABA DE TRÁFEGO ---
    print("Processando Tráfego (Painel)...")
    trafego_ws = sh.worksheet("📈 Dados | Tráfego Conversão")
    trafego_data = trafego_ws.get_all_values()
    df_trafego = pd.DataFrame(trafego_data[1:], columns=trafego_data[0])
    
    # Limpeza Tráfego Geral - Usando strip() para evitar KeyError de espaços
    cols = {c.strip(): c for c in df_trafego.columns}
    
    inv_col = cols.get('Investimento')
    fat_col = cols.get('Faturamento (Bruto)')
    
    df_trafego[inv_col] = df_trafego[inv_col].apply(clean_currency)
    df_trafego[fat_col] = df_trafego.get(fat_col, pd.Series(['0']*len(df_trafego))).apply(clean_currency)
    
    # Tratando colunas de Vendas
    col_vd = cols.get('Vendas')
    col_vd_real = cols.get('Vendas (real)')
    col_chk = cols.get('Leads (checkout real)')
    
    df_trafego[col_vd] = df_trafego[col_vd].apply(clean_int)
    df_trafego[col_vd_real] = df_trafego[col_vd_real].apply(clean_int)
    df_trafego[col_chk] = df_trafego.get(col_chk, pd.Series(['0']*len(df_trafego))).apply(clean_int)
    
    # KPIs Básicos Meta
    inv_total = df_trafego[inv_col].sum()
    fat_meta = df_trafego[fat_col].sum()
    
    ingressos_meta = df_trafego[col_vd].sum()
    ingressos_real_meta = df_trafego[col_vd_real].sum()
    
    ingressos_organico = max(0, ingressos_total - ingressos_real_meta)
    fat_organico = max(0, fat_total - fat_meta)
    
    cpv_geral = inv_total / ingressos_total if ingressos_total > 0 else 0
    cpv_meta = inv_total / ingressos_meta if ingressos_meta > 0 else 0
    cpv_real_meta = inv_total / ingressos_real_meta if ingressos_real_meta > 0 else 0
    
    ticket_geral = fat_total / ingressos_total if ingressos_total > 0 else 0
    ticket_meta = fat_meta / ingressos_meta if ingressos_meta > 0 else 0
    ticket_real_meta = fat_meta / ingressos_real_meta if ingressos_real_meta > 0 else 0
    ticket_organico = fat_organico / ingressos_organico if ingressos_organico > 0 else 0
    
    roas_geral = fat_total / inv_total if inv_total > 0 else 0
    roas_real_meta = fat_meta / inv_total if inv_total > 0 else 0
    
    print("Exportando Base Relacional (Raw Traffic)...")
    
    col_cli = cols.get('Cliques')
    col_imp = cols.get('Impressões')
    col_vis = cols.get('Visitou Página')
    
    df_trafego[col_cli] = df_trafego.get(col_cli, pd.Series(['0']*len(df_trafego))).apply(clean_int)
    df_trafego[col_imp] = df_trafego.get(col_imp, pd.Series(['0']*len(df_trafego))).apply(clean_int)
    df_trafego[col_vis] = df_trafego.get(col_vis, pd.Series(['0']*len(df_trafego))).apply(clean_int)
    
    raw_traffic = []
    df_valid = df_trafego[df_trafego['Campanha'].astype(str).str.strip() != '']
    
    for _, row in df_valid.iterrows():
        thumb = str(row.get('Thumbnail URL', ''))
        link = str(row.get('Link Criativo', ''))
        raw_traffic.append({
            "data": str(row.get('Data', '')).strip(),
            "camp": str(row['Campanha']),
            "pub": str(row['Público']),
            "cria": str(row['Criativo']),
            "inv": float(row[inv_col]),
            "fat": float(row[fat_col]),
            "vend": int(row[col_vd_real]),
            "chk": int(row[col_chk]),
            "cli": int(row[col_cli]),
            "imp": int(row[col_imp]),
            "vis": int(row[col_vis]),
            "thumb": thumb if thumb != 'nan' else "",
            "link": link if link != 'nan' else ""
        })

    payload = {
        "fat_total": format_brl(fat_total),
        "inv_total": format_brl(inv_total),
        "ingressos_total": int(ingressos_total),
        "ingressos_meta": int(ingressos_meta),
        "ingressos_real_meta": int(ingressos_real_meta),
        "ingressos_organico": int(ingressos_organico),
        "ob_total": int(ob_total),
        "ob_gravacao": int(ob_gravacao),
        "ob_ebook": int(ob_ebook),
        "ob_planilha": int(ob_planilha),
        "ob_combo": int(ob_combo),
        "cpv_geral": format_brl(cpv_geral),
        "cpv_meta": format_brl(cpv_meta),
        "cpv_real_meta": format_brl(cpv_real_meta),
        "cpv_organico": "-",
        "ticket_geral": format_brl(ticket_geral),
        "ticket_meta": format_brl(ticket_meta),
        "ticket_real_meta": format_brl(ticket_real_meta),
        "ticket_organico": format_brl(ticket_organico),
        "roas_geral": format_roas(roas_geral),
        "roas_real_meta": format_roas(roas_real_meta),
        "roas_organico": "-",
        "raw_vendas": raw_vendas,
        "raw_traffic": raw_traffic,
        "last_update": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    return payload

def inject_to_html(payload):
    print("Injetando megadados no HTML...")
    if not os.path.exists(HTML_PATH):
        print(f"❌ Erro: Arquivo {HTML_PATH} não encontrado!")
        return

    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    script_tag = soup.find(id="python-metrics-payload")
    if script_tag:
        script_tag.string = json.dumps(payload, indent=4)
        
    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(str(soup))
        
    print(f"✅ DASHBOARD ATUALIZADO: {HTML_PATH}")

if __name__ == "__main__":
    try:
        dados = process_data()
        inject_to_html(dados)
    except Exception as e:
        import traceback
        print(f"❌ Erro Crítico: {str(e)}")
        traceback.print_exc()
