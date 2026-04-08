# Diretiva: Relatório de Performance - Mozini Advocacia

> **Objetivo:** Estabelecer o padrão imutável de estrutura, dados e design para o relatório de WhatsApp da Mozini Advocacia, garantindo que a automação siga a inteligência do modelo original.

---

## 1. Regras de Cronologia (Ciclos)

- **Padrão:** O relatório segue o ciclo de **Quarta-feira a Terça-feira**. 
- **Exceção (Início):** A primeira semana útil de coleta (Semana 2) foi de 09/03 a 17/03.
- **Fechamento:** O report deve ser gerado toda **terça-feira à noite**.

## 2. Hierarquia de Visualização (Ordem dos Cards)

A ordem dos blocos dentro de cada semana é **obrigatória**:
1.  **Report Comercial (CRM):** Visão geral do funil (prioridade máxima, `grid-column: 1 / -1`).
2.  **Report Meta Ads:** Dados de tráfego pago (Instagram/Facebook).
3.  **Report Google Ads:** Dados de tráfego pago (Busca).

## 3. Regras de Dados (Inteligência do Automação)

### 3.1 Limpeza de Stages (Pipeline)
- **Regra:** Remover prefixos numéricos dos nomes das etapas do CRM (ex: "0. Contato Inicial" vira "Contato Inicial").
- **Ação:** O script deve usar Regex para limpar nomes que começam com "X. ".

### 3.2 Distribuição de SQL e Reuniões
- **Regra:** Nunca mostrar apenas o número. Sempre especificar a origem do lead que atingiu aquela etapa.
- **Exemplos:** 
  - `SQL: 1 Indicação`
  - `Reunião Agendada: 5 Indicação`
- **Motivo:** A maioria das oportunidades qualificadas da Mozini vem de Indicações, e o Ads serve como topo de funil (MQL).

## 4. Design System (Cores e Identidade)

- **Meta Ads:** #3B82F6 (Azul)
- **Google Ads:** #22C55E (Verde)
- **Indicação:** #F97316 (Laranja)
- **Canal Desconhecido:** #A855F7 (Roxo)
- **Contratos:** #4ADE80 (Verde Brilhante)

---

## 5. Estrutura Manual vs Automação

- A automação em `automate_whatsapp_report.py` deve conter estas cores e regras de agrupamento em seu template HTML interno para evitar retrocessos estéticos.

*Documento criado em 07/Abr/2026. Comandos travados.*
