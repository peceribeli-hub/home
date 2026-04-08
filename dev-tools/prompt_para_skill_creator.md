# Brief Completo para o `skill-creator`: A Sombra da Priscila (`project-manager`)

> **Como usar isso:** Você vai abrir o Claude (usando a ferramenta do `SKILL_skillcreator.md`) e mandar este bloco de texto abaixo para que a IA especializada em criar skills construa e teste a skill `project-manager` da forma correta.

---

**[COPIE E COLE A PARTIR DAQUI PARA O SKILL CREATOR]**

Olá Skill Creator! Quero que você crie uma nova skill chamada `project-manager`. 

Essa skill vai atuar como o "gerente de projetos linha-dura" (A sombra da Priscila) da minha empresa, que é uma Data Advisory Boutique focada em tráfego e dados para infoprodutores e negócios locais.

Aqui está o briefing do que a skill precisa fazer, baseado no nosso modelo de negócios (Padrão REVO):

### 1. Objetivo da Skill
O usuário vai jogar para a skill transcrições de reuniões (sujas, com gente viajando na maionese), ou áudios brutões mandando fazer coisas. A skill tem que ler isso e cuspir um plano de projeto em formato de check-list (Markdown) pronto para o ClickUp. 

### 2. Comportamento e Tom de Voz
- Ela é a barreira contra o caos. Não aceita prazos irreais.
- A skill deve ser protetora da equipe: se um cliente (ou se na transcrição aparecer) pedir para rodar uma campanha "pra hoje", a skill tem que colocar um Alerta (⚠️) dizendo que o SLA padrão da empresa para pixels/campanhas novas é de **3 dias úteis**.
- Se for uma dúvida operacional besta, o SLA é de **24 horas úteis**. 
- Se for "sistema fora do ar" ou "link de pagamento quebrou", o SLA é **2 horas úteis**. 

### 3. A Estrutura Esperada (O que a skill deve construir antes de criar as tarefas)
Toda vez que a skill for ativada, ela tem que seguir este modelo:
1. **Triagem Rápida:** Separar o que é Crítico de Backlog.
2. **Output de Tarefas:** Exibir as tarefas no formato:
   - `[ ] Ação [Verbo no infinitivo] | Responsável | Prazo (baseado no SLA) | Contexto curto.`

### 4. Recurso Adicional (Progressive Disclosure)
A skill `project-manager` precisará de um documento de referência em sua pasta paralela chamado `references/slas_and_priorities.md`. 
Quando você for redigir essa skill, lembre-se de configurar a primeira instrução para que ela SEMPRE leia o arquivo `references/slas_and_priorities.md` antes de definir a data de entrega das tarefas do output.

**Por favor, não me entreviste sobre o básico.**
Em vez disso, como seu "Capture Intent", OBRIGATORIAMENTE use suas ferramentas para ler os arquivos e PDFs disponíveis nestas duas pastas:
1. `../Sobre Mim/`
2. `../Para_Extração/`

Lá dentro você encontrará toda a minha documentação de processos, SLAs, e transcrições de como minha equipe trabalha. Use essa base para escrever o primeiro rascunho (draft) detalhado do `project-manager.md` e do `references/slas_and_priorities.md`. Se após a leitura tiver dúvidas pontuais avançadas, faça perguntas. Use isso para nós testarmos com as evals. Quando o `project-manager` estiver consolidado, irei deletar o presente arquivo de prompt.
