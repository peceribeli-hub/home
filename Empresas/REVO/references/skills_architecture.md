# Estrutura e Planejamento para as Skills `data-analyst` e `tech-infra`

## Racional de Economia (Tokens e Tempo)
Para economizar tokens e tempo de criação, não construiremos as skills "no escuro". O processo mais inteligente e barato é **centralizar o conhecimento na Aurora** (pois ela é a maestrina) e criar as outras duas skills **apenas focadas em executar a parte técnica**, sem que elas precisem ler todas as transcrições gigantes ou regras de cultura da empresa.
1. A **Aurora** lê o `Guia_Operacional_REVO`, decide o que fazer e manda comandos prontos para a Paola e Kayque.
2. O **`data-analyst` (Paola)** só vai ter os templates de planilhas. Ex: "Pegue esse CSV e calcule Lucro Líquido baseado na fórmula X".
3. O **`tech-infra` (Kayque)** só vai ter os JSONs das automações e blocos de código GTM, pronto para colar nas plataformas.

Esse modelo de **Progressive Disclosure descentralizado** impede que todas as skills tenham que ler a cultura da empresa toda vez, cortando o uso de tokens pela metade.

## Política de Idiomas (Bilingual Architecture)
Para garantir que as instruções complexas sejam entendidas com máxima precisão (Instruction Following) pelos modelos (como Claude/Gemini) e para usar de forma nativa a ferramenta `skillcreator.md`, **todo o desenvolvimento estrutural das skills será feito em Inglês.**
*   **Frontmatter, Regras lógicas e Diretrizes Técnicas:** 100% em Inglês.
*   **Resultados Finais, Comunicação e Documentos Gerados:** 100% em Português-BR.
*   **Mantra Obrigatório em cada Skill:** `CRITICAL: You must ALWAYS generate your final output, reports, and communication with the user entirely in Brazilian Portuguese (pt-BR). Under no circumstances should you reply in English.`

---

## Passo a Passo para Executar

### Fase 1: Criar Módulo `data-analyst` (Paola)
**Status:** Preparando

1.  **Deduplicação de Inteligência:** A Paola vai ter uma base de conhecimento enxuta, mas **extremamente densa em métricas**. Ela precisa conhecer as divisões exatas (Custo por Lead, Conversão de Página, Taxa de Carregamento, CPM) separadas por três caixas: *Perpétuo*, *Crescimento* e *Lançamento*, exatamente como o Regis prega no REVO.
2.  **O Repositório Central de Funis:** Para não gastar tokens ensinando a Paola do zero, **vamos apontar a Paola para ler a MESMA matriz de inteligência do Regis (`strategic-clone/references/arquitetura_de_funis.md`)**. Assim, se o Regis altera um funil lá, a Paola e o Regis sempre estarão olhando para a mesma regra.
3.  **O Loop de Comunicação (Paola ↔ Aurora):** A skill da Paola terá uma diretriz em seu `.md`: *"Sempre que gerar um relatório, adicione uma meta-análise no final chamada `[Para a Aurora]` apontando quais gargalos operacionais causaram a flutuação nas métricas."* Isso faz a Paola alimentar a Aurora de volta com as tarefas de correção necessárias.
4.  **Avaliação (Eval):** Simular que o usuário entregou uma planilha suja para a Paola, e ela entrega um relatório de Funil formatado e um apontamento de tarefa para a Aurora delegar.

> **Prompt Inicial (em Inglês) para o Skill Creator gerar a Paola:**
> *"Create a new skill named 'data-analyst'. Description: 'Advanced data analysis skill for REVO Advisory. Triggers whenever the user uploads CSVs/spreadsheets with marketing metrics, asks to calculate funnel conversion rates, or build dashboards. This skill processes raw tracking data and maps it against REVO funnel architectures.' Rules: Read REVO's 'arquitetura_de_funis.md' as reference. Always generate a meta-analysis tag '[Para a Aurora]' at the end of every report. CRITICAL: Output must always be in Brazilian Portuguese (pt-BR)."*

### Fase 2: Criar Módulo `tech-infra` (Kayque)
**Status:** Aguardando conclusão da Paola

1.  **Prompt Otimizado para o Skill Creator:** Mesmo processo de prompt enxuto.
2.  **A Base de Conhecimento Necessária:** Pasta de referências focada apenas em **Protocolos de Rastreio**. Ex: Quais são os nomes exatos (Slugs) que os eventos da REVO precisam ter.
3.  **Avaliação (Eval):** Simular a criação de um webhook para a Yampi que avise a Aurora quando tiver um erro 404.

### Fase 3: Fechar o Ciclo da Aurora
**Status:** Aguardando

1.  Quando `data` e `tech` estiverem prontos, dar a instrução final para a Aurora: "Quando acionar a Paola, chame a skill `data-analyst`. Quando acionar o Kayque, chame a skill `tech-infra`". (A Aurora vira um supervisor real chamando agentes reais).

---

> Se este modelo descentralizado faz sentido e parece econômico para você, me dê um "Ok" e eu já gero o arquivo de prompt para você rodar no Skill Creator e criar a Paola (data-analyst).
