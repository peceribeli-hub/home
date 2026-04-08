# Diretiva: Geração de Relatórios de Performance

> **Objetivo:** Gerar relatórios padronizados (semanal, mensal, anual) para qualquer cliente da REVO, seguindo o Branding Book e a metodologia de análise de dados.

---

## 1. Tipos de Relatório

| Tipo | Frequência | Conteúdo Principal | Fontes |
|---|---|---|---|
| **Semanal** | Toda segunda | Leads novos, reuniões, contratos, investimento Ads | Leads WhatsApp, Google Ads, Meta Ads |
| **Mensal** | Dia 1 do mês | Funil completo, CAC/LTV por origem, produtos, cash collect | Todos (Asaas, Ads, Leads) |
| **Anual** | Jan do ano seguinte | Consolidado completo com atribuição corrigida e projeções | Todos |

## 2. Fontes de Dados por Cliente

Cada cliente terá sua pasta `Financeiro e Metas/` contendo:
- Extrato financeiro (ex: `Extrato Asaas.csv`)
- Relatório gateway (ex: `relatorio.csv` InfinitePay)
- Dados Google Ads (ex: `Mozini Advocacia _ Daily - 📈 Dados _ Google.csv`)
- Dados Meta Ads (ex: `Mozini Advocacia _ Daily - 📈 Dados _ Meta Ads.csv`)
- Leads/CRM (ex: `Mozini Advocacia _ Daily - Leads _ Whatsapp.csv` ou export Kommo)

## 3. Pipeline de Execução

### 3.1 Coleta
1. Identificar a pasta do cliente em `2. Clientes/Ativos/{cliente}/Interno/Financeiro e Metas/`
2. Listar CSVs disponíveis e mapear colunas

### 3.2 Processamento
1. Executar `execution/gerar_relatorio.py` com os parâmetros do cliente
2. O script calcula: investimento por plataforma/mês, funil por origem, atribuição por período, CAC/LTV, produtos

### 3.3 Geração do Relatório
1. Aplicar o template `aurora/methodology/template_relatorio.md`
2. Gerar HTML seguindo o Branding Book (`05_Branding_Book.md`)
3. Salvar na pasta do cliente como `Relatorio_{tipo}_{periodo}.html`

## 4. Regras de Branding (Obrigatório)

- **Cores:** REVO Red (#E50915), REVO Black (#111111), REVO Cream (#F2D9C3), Surface (#1A1A1A)
- **Tipografia:** Inter (Google Fonts), pesos 300-900
- **Estilo:** Fundo escuro, sem ícones decorativos, dado é protagonista, glassmorphism sutil
- **KPIs:** Peso 900, tamanho 28px
- **Logo:** Incluir no header do relatório

## 5. Regras de Métricas

- Seguir metodologia documentada em `Mozini_Parametros_Financeiros.md` (ou equivalente por cliente)
- Cash Collect: fonte-mestre é o gateway financeiro (Asaas)
- Deduplicar InfinitePay (já está dentro do Asaas)
- Atribuição por período quando UTM não disponível
- Separar sempre: Faturamento (contratos) vs Recebimentos (entradas) vs Cash Collect (total)

## 6. Regras de Qualidade

- **Zero invenção**: se faltam dados, acionar `[🚨 Double-Check Necessário]`
- **Validação obrigatória**: rodar script de validação antes de gerar HTML
- **Feedback para Aurora**: todo relatório termina com diagnóstico + tarefas operacionais

---

*Diretiva criada em 04/Mar/2026. Documento vivo.*
