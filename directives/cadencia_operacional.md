# Cadência Operacional

> **Regra Principal:** Este documento dita QUANDO e COMO gerar relatórios para nossos clientes. Os relatórios semanais são a pulsação do nosso negócio. 

---

## 📅 Relatório Semanal — O Ritual das Segundas

**Quem recebe:** Todos os clientes em contrato ativo  
**Escopo:** Semana anterior completa (segunda-feira a domingo)  
**Template Base:** `directives/template_relatorio_semanal.md`

**Fluxo da Automação AI:**
1. O agente de IA (eu) identifica os clientes na pasta `Empresas/` (ex: Martin Trader, Mozini).
2. O agente olha as tabelas unificadas CSV.
3. Processa cálculos, ROAS, leads gerados, comissão, e extrai as Top Campanhas do Meta.
4. Preenche os *placeholders* no relatórios semanais HTML ou Markdown.
5. O gerente humano apenas revisita o insight final ("Análise Qualitativa") e dispara no WhatsApp do cliente.

**Clientes em Foco Atualmente:**
- Martin Trader (Lançamento e Perpétuo)
- Mozini Advocacia (Funil de Reunião/Agenda WhatsApp)
- Ibiti/Jhovas
- NF / Método Gerente de Pasto

## 📋 Regras de Entrega do Relatório
*   **Seja Frio e Analítico:** O cliente nos paga pela verdade. Não mascara números ruins. "O custo triplicou por falha criativa" é muito melhor do que "tivemos um leve aumento pontual".
*   **Traduza R$ / US$ sempre:** Cuidado com o símbolo de moeda do país do lançamento.
*   **Sempre indique Próximo Passo:** Todo relatório termina com a linha de "Ações da Semana" para o Time/Estrategista e Ações para o Cliente gravar ou editar.
