# Template de Relatório de Performance — Método REVO

> Template padrão para relatórios semanal, mensal e anual. O Data Analyst preenche os dados e gera HTML seguindo o Branding Book.

---

## Estrutura do Relatório

### 1. Header
- Logo REVO Advisory
- Título: "Relatório {Tipo} {Período}"
- Subtítulo: "{Nome do Cliente} — {Descrição curta}"
- Data de geração

### 2. Resumo Executivo
**Financeiro — 3 Camadas:**
- Faturamento (contratos fechados): R$ ___
- Recebimentos (entradas dos novos contratos): R$ ___
- Cash Collect Total (gateway financeiro): R$ ___
- Cash Collect de contratos anteriores: R$ ___

**Performance do Funil:**
- Total Leads | Reuniões Agendadas/Realizadas | Contratos Fechados
- CAC Global | Ticket Médio | LTV/CAC | ROAS
- Taxa de Agendamento | Taxa de Fechamento | Taxa de Conversão Global

### 3. Investimento por Plataforma e Mês
- Tabela: Mês | Google | Meta | Total | Fonte Ativa | Conversões Google | Mensagens Meta
- KPIs: Total Google, Total Meta, % de cada

### 4. Funil Completo por Origem
Para CADA origem (Tráfego, Meta, Google, Indicação, Orgânico, etc.):
- Leads | Taxa Agendamento | Taxa Realização | Contratos | Conv% | Close%
- Faturamento | Recebido | Ticket Médio | Ciclo Médio
- **CAC | CPL | LTV/CAC | ROAS** (atribuição corrigida por período)
- Top Problemas/Produtos
- Distribuição mensal

### 5. CAC / LTV / ROAS por Plataforma
- Tabela consolidada com atribuição corrigida
- Metodologia de atribuição explícita

### 6. Produtos / Tipos de Caso
- Tabela: Produto | Contratos | Faturamento | Ticket Médio | % do Total

### 7. Diagnóstico e Plano de Ação
- Gargalos Críticos (com severidade)
- Recomendações Estratégicas (com impacto esperado)
- Projeção para o próximo período

### 8. Footer
- Data de geração + agente responsável
- Fontes utilizadas
- Instrução para salvar como PDF

---

## Regras de Formatação HTML

```css
/* Cores REVO */
--revo-red: #E50915;
--revo-black: #111111;
--revo-cream: #F2D9C3;
--revo-white: #FFFFFF;
--revo-surface: #1A1A1A;
--revo-border: #2A2A2A;
--revo-font: 'Inter', sans-serif;

/* Alertas */
Crítico: border-left #E50915, background rgba(229,9,21,0.08)
Atenção: border-left #F2D9C3, background rgba(242,217,195,0.08)
Positivo: border-left #00b894, background rgba(0,184,148,0.08)
Info: border-left #FFFFFF, background rgba(255,255,255,0.05)
```

- KPIs: font-weight 900, font-size 28px
- Tags de origem: background com 15% de opacidade
- Tabelas: header em #1A1A1A com texto #F2D9C3
- Sem emojis no HTML (diferente do .md)
- Sem ícones decorativos — o dado é protagonista
- Espaçamento generoso entre seções

---

*Template atualizado em 04/Mar/2026. Método REVO Advisory.*
