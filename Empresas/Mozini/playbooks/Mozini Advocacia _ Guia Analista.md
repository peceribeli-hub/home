# Guia do Analista — Mozini Advocacia · Funil de Reunião

> **Cliente:** Mozini Advocacia  
> **Responsável comercial:** Rodrigo Pia  
> **Funil:** Reunião / Agendamento  
> **Produto:** Serviços jurídicos — principalmente planos de saúde  
> **CRM:** Kommo (funil "[Vendas] Mozini Advocacia")  
> **Última atualização do pipeline:** 04.03.2026

---

## 1. Pipeline Real (Etapas da Kommo)

```
Lead entra no WA
    ↓
[0. Contato inicial] ← lead criado, aguardando resposta
    ↓
[1. Resposta Inicial] ← lead respondeu
    ↓
[2. Qualificação] ← MQL: qualificado pelo time
    ↓
[3. Reunião Agendada] ← AGENDAMENTO (consulta jurídica)
    ↓
[4. Negociação] ← SQL: proposta de honorários apresentada
    ↓
[Contrato Fechado] ← VENDA ✅ (campo: [MA] Valor Contrato)
```

**Perdas rastreadas (com motivo):**
- Lead sem legitimidade jurídica ← caso não tem respaldo legal
- Queria apenas tirar dúvidas
- Falta de urgência/prioridade
- Problema resolvido ← resolveu sem advogado
- Ausência de resposta pós follow-up
- Desconfiança do modelo digital/jurídico
- Fechou com outro advogado
- Objeção de preço/honorários

---

## 2. Mapeamento de Métricas → Etapas Kommo

| Métrica do Relatório | Como calcular na Kommo |
|---|---|
| Leads Gerados | Total de leads criados no período |
| Leads Qualificados (SQL) | Leads que chegaram ao status SQL ou à etapa "4. Negociação" |
| Reuniões Agendadas | Leads na etapa "3. Reunião Agendada" |
| Show-up Rate | Leads em Negociação ÷ Reuniões Agendadas |
| Taxa de Qualificação | SQL ÷ Total Leads |
| Contratos Fechados | Leads em "Contrato Fechado" |
| Faturamento (Valor Contrato) | Soma do campo `[MA] Valor Contrato` dos fechados |
| Taxa de Fechamento | Contratos Fechados ÷ Reuniões Agendadas |
| Taxa de Perda por Motivo | Leads perdidos por motivo ÷ Total de perdas |

---

## 3. Origens dos Leads (campo: [MA] Origem / Fonte de Origem)

| Origem Kommo | O que é na prática | CPL |
|---|---|---|
| **Meta / Meta Ads** | Anúncio Meta Ads (≈70–80% do volume total) | Calcular: Investimento ÷ Leads Meta |
| **Instagram** | Instagram orgânico ou misto | R$ 0 ou baixo |
| **Google** | Busca Google ou Google Ads | Calcular separado |
| **Indicação** | Indicação de cliente ou parceiro | R$ 0 |
| **Defensoria** | Lead via Defensoria Pública | R$ 0 |
| **Desconhecido** | Origem não rastreada | — |

> **Atenção:** Leads de Indicação e Defensoria tendem a ter **maior taxa de fechamento** que Meta Ads, pois chegam mais qualificados. Sempre comparar conversão por origem, não só volume.

---

## 4. Tipos de Problema Jurídico (campo: Dores/Desafios)

| Problema | Volume relativo | Observação |
|---|---|---|
| **Reajuste Abusivo** | ≈70%+ | Principal criativo — se saturar, CPL sobe |
| Cancelamento de Plano | Médio | Demanda urgência — fecha mais rápido |
| Erro Médico | Baixo | Ticket maior — mais complexo |
| Tratamento negado | Baixo | Alta urgência — fechamento rápido |
| Procedimento negado | Baixo | Similar ao tratamento negado |
| Medicamento negado | Baixo | Menor ticket, processo mais simples |

> **Para análise:** distribuição por tipo revela quais criativos/anúncios estão convertendo. Se "Reajuste Abusivo" dominar muito, explorar outros temas para diversificar.

---

## 5. Qualificação dos Leads (campo: [MA] Qualificação)

| Status | Significado | Ação esperada |
|---|---|---|
| **Lead** | Entrou, sem qualificação | Resposta inicial + qualificação |
| **MQL** | Marketing Qualified — respondeu, mínima qualificação | Agendar reunião |
| **SQL** | Sales Qualified — qualificado, pronto para proposta | Fechar contrato |

---

## 6. Árvore de Diagnóstico

```
Contratos abaixo da meta?
│
├── Taxa de qualificação baixa (Lead → MQL → SQL)?
│   ├── Muitos "Lead sem legitimidade jurídica" → público errado nos anúncios
│   ├── Muitos "Queria apenas tirar dúvidas" → copy do anúncio gera expectativa errada
│   └── Muita desqualificação em Meta → segmentação ou interesse precisa ajuste
│
├── Qualificados mas poucos agendamentos?
│   └── Gargalo no follow-up → CRM com leads estagnados em "2. Qualificação"
│
├── Reuniões agendadas mas não aparecem?
│   └── Confirmar presença 24h antes + lembrete no dia da reunião
│
├── Reuniões OK mas fechamento baixo?
│   ├── Objeção de preço → Revisar tabela de honorários / condições de parcelamento
│   ├── Desconfiança do modelo digital → Trabalhar prova social e credibilidade
│   └── Fechou com outro advogado → Entender diferenciais vs. concorrência
│
└── Volume de leads baixo?
    ├── Meta Ads com entrega ruim → Revisar orçamento, aprovação de anúncios
    ├── CPL crescendo → Saturação de criativo → Renovar ângulo ou problema abordado
    └── Indicações secando → Criar programa de parceria com clientes satisfeitos
```

---

## 7. Sinais de Atenção Específicos

| Sinal | Ação |
|---|---|
| CPL Meta Ads crescendo >20% m/m | Renovar criativos — ângulo saturou |
| "Lead sem legitimidade" > 30% das perdas | Público-alvo errado — revisar segmentação |
| Contratos fechados com valor < R$1.500 | Mix de casos simples — avaliar ticket mínimo |
| Leads em "2. Qualificação" há +7 dias sem move | Follow-up automatizado falhou — checar CRM |
| Indicação + Defensoria > 30% das vendas | Canal orgânico forte — formalizar parceria |

---

## 8. Aprendizados Acumulados

> *Preencher com o que funcionar ou não ao longo do tempo. Este documento evolui junto com o cliente.*

| Data | Aprendizado | Impacto |
|---|---|---|
| — | — | — |

---

*Referência de pipeline: [`kommo_pipeline_mapeamento.md`](file:///Users/regisprado/Downloads/New/aurora/references/kommo_pipeline_mapeamento.md)*  
*Template macro: [`guia_analista_dados.md`](file:///Users/regisprado/Downloads/New/aurora/references/guia_analista_dados.md)*  
*State do cliente: [`state.md`](file:///Users/regisprado/Downloads/New/clients/mozini-advocacia/state.md)*
