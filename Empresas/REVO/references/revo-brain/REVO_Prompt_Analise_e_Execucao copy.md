# Prompt: Mapa de Clareza → Análise → Confirmação → Execução

> Cole este prompt no início de qualquer mensagem com transcrição, texto longo ou notas brutas.
> Substitua [TIPO] e [OBJETIVO] conforme o contexto. O conteúdo vai no final.

---

## TEMPLATE DO PROMPT

```
MODO: Mapa de Clareza → Análise → Confirmação → Execução

Tipo de entrada: [transcrição de reunião / notas brutas / documento / texto longo]
Objetivo final: [ex: redistribuir tarefas / criar KPIs / montar plano de ação / outro]

---

ETAPA 0 — MAPA DE CLAREZA (antes de qualquer tarefa ou arquivo)

Leia tudo. Antes de listar tarefas, me mostre como as peças se encaixam.

Produza um mapa com este formato:

🧩 COMPONENTES IDENTIFICADOS
Liste cada "peça" do sistema mencionada no conteúdo (funis, processos, papéis, etapas, documentos).

🔗 COMO SE CONECTAM
Para cada conexão, escreva uma linha:
→ [Peça A] alimenta [Peça B] porque [motivo simples]
→ [Peça B] depende de [Peça A] para funcionar

📐 HIERARQUIA
Monte uma estrutura visual em texto mostrando o que vem antes e o que vem depois:

[Nível 1 — base / origem]
  └── [Nível 2 — alimentado pelo nível 1]
        └── [Nível 3 — resultado final]

⚠️ ONDE A LÓGICA AINDA NÃO ESTÁ CLARA
Liste qualquer ponto onde a conexão entre peças ficou vaga ou contraditória no conteúdo.

Regra: use linguagem simples. Escreva como se fosse explicar para alguém que nunca viu este projeto.

---

ETAPA 1 — EXTRAÇÃO (não crie nenhum arquivo ainda)

Após o mapa, extraia e apresente como tabelas estruturadas:

| Categoria       | O que extrair                                      |
|-----------------|----------------------------------------------------|
| Decisões        | O que foi decidido, por quem                       |
| Tarefas         | Quem | O quê | Até quando | Prioridade             |
| Números / metas | Valores, datas, percentuais mencionados            |
| Pessoas         | Nomes, papéis, responsabilidades citadas           |
| Contexto-chave  | Problemas identificados, riscos, oportunidades     |
| Ambiguidades    | O que ficou vago, contraditório ou incompleto      |

Seja direto. Sem parágrafos explicativos — só tabelas e listas.

---

ETAPA 2 — CONFIRMAÇÃO

Após as tabelas, faça no máximo 5 perguntas. Apenas sobre:
- Pontos do mapa de clareza que precisam de validação
- Ambiguidades que bloqueiam a execução
- Decisões que dependem da minha preferência (não assuma)

Formato das perguntas: numeradas, uma linha cada, sem contexto longo.

Encerre com:
"Confirme o mapa e responda as perguntas. Só depois vou executar."

---

ETAPA 3 — EXECUÇÃO

Aguardar confirmação. Após minha resposta:
- Atualize o mapa se necessário
- Execute tudo de uma vez
- Sem novas perguntas durante a execução
- Para cada ação, escreva:
  ✅ O que fazer (uma frase)
  📍 Onde fazer (ex: "Abra o ClickUp → clique em 'Tarefas' → selecione o projeto X")
  👆 Passo a passo numerado com cliques exatos
  ✔️ Como saber que deu certo (o que vai aparecer na tela)
- Entregue os arquivos ao final

---

[COLE SEU CONTEÚDO AQUI]
```

---

## EXEMPLOS DE USO

**Reunião com estrutura complexa (funnels, processos encadeados):**
```
Tipo de entrada: transcrição de reunião
Objetivo final: entender como os funis se conectam e redistribuir tarefas no ClickUp

[transcrição]
```

**Planejamento estratégico:**
```
Tipo de entrada: notas brutas de sessão de planejamento
Objetivo final: criar documento de metas e KPIs por cliente

[notas]
```

**Briefing de cliente:**
```
Tipo de entrada: texto longo de briefing recebido
Objetivo final: montar plano de ação e lista de próximos passos

[briefing]
```

---

## POR QUE FUNCIONA

| Problema comum                          | Como este prompt resolve                                      |
|-----------------------------------------|---------------------------------------------------------------|
| "Como essa peça se encaixa na outra?"   | Etapa 0 mapeia dependências e hierarquia antes de tudo       |
| Equipe não entende o raciocínio do Regis| Mapa de clareza traduz o modelo mental em estrutura visual   |
| Execução errada → retrabalho            | Confirma o mapa antes de criar qualquer arquivo              |
| Perguntas demais no meio                | Todas as dúvidas são concentradas na Etapa 2                 |
| Contexto longo = tokens altos           | Extração compacta em tabelas reduz o que carrega             |
| Informação ambígua                      | Ambiguidades são identificadas explicitamente                |
| Sessão longa e cara                     | Uma sessão = mapa + análise + confirmação + entrega          |

---

## ESTRUTURA DE FUNIS PADRÃO

Os funis abaixo são o conjunto padrão da REVO. Quais funis um cliente usa depende do tipo de negócio dele. O conjunto ativo de funis é o que gera o resultado final.

```
FUNIS DISPONÍVEIS (por tipo de negócio)

Todos os clientes:
  └── Funil de Crescimento no Instagram
        ├── Engrenagens: Posts + Tráfego Pago
        └── Resultado: novos seguidores qualificados

Clientes de serviço:
  └── Funil de Agendamento de Reuniões
        ├── Engrenagens: Posts + Tráfego Pago + Página de captura
        └── Resultado: reuniões agendadas

Infoprodutores:
  ├── Funil Perpétuo
  │     ├── Engrenagens: Posts + Tráfego Pago + Página de vendas sempre ativa
  │     └── Resultado: vendas contínuas
  └── Funil de Lançamento
        ├── Modalidades:
        │     ├── Lançamento Pago
        │     ├── Lançamento Gratuito
        │     └── Lançamento Meteórico
        ├── Engrenagens: Posts + Tráfego Pago + Sequência de aquecimento
        └── Resultado: vendas em janela de tempo
```

Cada funil ativo tem:
- Métricas próprias
- Meta própria
- Responsável próprio
- Relatório semanal próprio
- Relatório mensal próprio

---

## O QUE A ETAPA 0 PRODUZ (exemplo)

Para uma reunião sobre os funis de um cliente infoprodutor, a saída seria:

```
🧩 COMPONENTES IDENTIFICADOS
- Meta geral do cliente (resultado esperado no período)
- Funil de Crescimento no Instagram
- Funil Perpétuo
- Funil de Lançamento (modalidade: Lançamento Gratuito)
- Posts (Funil de Crescimento)
- Tráfego pago (engrenagem de cada funil, gerenciada separadamente)
- Relatório semanal por funil
- Relatório mensal por funil

🔗 COMO SE CONECTAM
→ Meta geral define o número-alvo de cada funil separadamente
→ Posts são a engrenagem orgânica do Funil de Crescimento
   porque é o conteúdo que atrai novos seguidores
→ Tráfego pago é a engrenagem paga de cada funil
   porque cada funil tem sua própria verba e objetivo de tráfego
→ Funil de Crescimento, Funil Perpétuo e Funil de Lançamento operam em paralelo
   porque cada um tem objetivo, métricas e responsável próprios
→ Cada funil gera seus próprios relatórios semanais e mensais
   para que o desempenho de um não misture com o dos outros

📐 HIERARQUIA
[Meta Geral do Cliente]
  ├── [Funil de Crescimento no Instagram]
  │     ├── Posts
  │     ├── Tráfego Pago
  │     └── Relatório semanal + Relatório mensal
  ├── [Funil Perpétuo]
  │     ├── Tráfego Pago
  │     └── Relatório semanal + Relatório mensal
  └── [Funil de Lançamento — Lançamento Gratuito]
        ├── Posts
        ├── Tráfego Pago
        └── Relatório semanal + Relatório mensal

⚠️ ONDE A LÓGICA AINDA NÃO ESTÁ CLARA
- Não ficou claro se cada funil tem meta numérica própria ou se dividem a meta geral
- Não foi definido quem é o responsável por cada funil neste cliente
```

---

## VARIAÇÃO RÁPIDA (quando a estrutura já é conhecida)

Se você já entende como as peças se conectam e só precisa das tarefas:

```
Leia o conteúdo abaixo. Extraia em tabelas: decisões, tarefas (quem/o quê/quando) e pontos ambíguos.
Faça no máximo 3 perguntas. Aguarde minha confirmação para executar.
Objetivo: [descreva aqui]

[CONTEÚDO]
```
