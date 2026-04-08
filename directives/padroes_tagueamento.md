# Padrões de Tagueamento e Infraestrutura

> **Regra Mestra de Engenharia de Dados:** Nossa operação **proíbe a duplicação descontrolada de formulários e páginas**. A inteligência vive no código, não na criação de infinitos ativos inúteis.

## 1. Formulários Centralizados
Se um cliente tem uma Isca Escassa (e-book, minicurso), nós NÃO criamos um formulário no WordPress para "Facebook", outro para "Google", outro para "Orgânico".

- **O Padrão:** **UM (1)** único formulário inteligente.
- **A Captação:** O Tracking (via GTM ou script nativo) deve capturar os parâmetros de URL (`utm_source`, `utm_medium`, `utm_campaign`) via JavaScript (ou campos ocultos) e jogar essa informação no Payload do Webhook (Make/n8n).
- **A Rota:** Nossa automação recebe o post único do formulário, lê as UTMs no JSON e roteia para o funil correto dentro do CRM de Vendas.

## 2. Nomenclatura de Eventos (Slugs)
Os disparos do DataLayer do GTM e Conversões Personalizadas devem seguir este padrão em minúsculo, sem espaços (usar underscores):
- `lead_capturado` — Disparado quando o GTM lê sucesso no envio do formulário.
- `checkout_iniciado` — Disparado no clique do botão "ir para o checkout".
- `compra_aprovada` — Disparado pelo webhook da plataforma de pagamento.

## 3. Prioridade de Atuação
A infraestrutura (tags, n8n, make) atua **antes** de as campanhas irem pro ar. Se a infraestrutura for chamada no meio do lançamento porque "o pixel parou de disparar", a resolução é de SLA de 2 Horas (Crise Máxima). Qualquer outro desenvolvimento (criar fluxo novo) vai para a esteira da sexta-feira.

CRITICAL: Toda a comunicação e output final de relatórios deve ser gerada em Português do Brasil (pt-BR).
