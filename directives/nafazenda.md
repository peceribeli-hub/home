# Diretiva de Análise: NaFazenda

**Objetivo:** Comparar os resultados das campanhas dos produtos NaFazenda entre o "Período Anterior" (antes da Revo) e o "Período Atual" (com a Revo), gerando um diagnóstico de melhorias e pioras baseado em regras fixas.

## Produtos Alvo
1. Formulando na Prática
2. Recria na Prática
3. Gestão de Risco na Prática (também chamado de Trava do Boi na Prática)

## Métricas Principais e Benchmarks (Guia de Tráfego)
As seguintes regras ditam se o resultado é "Bom" ou "Ruim":
* **CTR (Taxa de Clique):**
  * Meta ideal: 0.50% a 1.00%
  * Ruim: Menor que 0.35% a 0.60% (Fadiga de criativo se cair bruscamente)
* **CPM (Custo por Mil Impressões):**
  * Meta ideal: Em torno de R$ 8.00 a R$ 9.00
  * Ruim: CPMs muito altos indicam público saturado ou alta competição.
* **Connect Rate (Visualizações / Cliques no link):**
  * Meta ideal: 70% a 75%
  * Ruim: Menor que 60% (alerta de problema grave na página de destino)

## Entradas de Dados
* **Período Anterior:** Extraído da Meta (Arquivos `.csv`). Devem ser lidos calculando as médias de CPM, CTR e Connect Rate ponderadas pelo volume de impressões e cliques.
* **Período Atual:** Arquivos `.pdf` do dashboard da Revo. A extração deve localizar textualmente as métricas resumidas nestes PDFs.

## Dinâmica de Vendas ("Hora vende, hora não vende")
* Verificar se a oscilação nas conversões está atrelada à queda de CTR (criativo não atrai mais) ou ao Connect Rate (a página parou de carregar rápido em dias específicos ou lida mal com picos de tráfego).

## Saídas (Outputs)
O script de execução deverá gerar um relatório Markdown/Texto detalhando a comparação das métricas supracitadas, apontando claramente "O que estava bom/ruim no passado" e "O que melhorou/piorou agora", incluindo sugestões de decisões (ex: Trocar criativos, Melhorar velocidade da página) sem uso de jargões robóticos, tudo em Português do Brasil.
