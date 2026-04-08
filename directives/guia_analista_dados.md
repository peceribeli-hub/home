# Guia do Analista de Dados — Diagnóstico de Funil

> **Objetivo:** Este documento traduz os números dos relatórios em perguntas de diagnóstico. Quando um indicador estiver fora da meta, use este guia para encontrar a causa raiz antes de recomendar qualquer ação.
> **Isso NÃO** vai para o cliente final na íntegra — é o bastidor da inteligência.

---

## 1. Funil Perpétuo — Árvore de Diagnóstico

```
Baixo ROAS?
│
├── Alto CPL?
│   ├── Alto CPM?      → Público saturado ou criativo fraco → Renovar criativos
│   ├── Baixo CTR?     → Gancho ruim / Criativo não clica → Testar novos ângulos
│   └── CPL ok + CTR baixo → Segmentação errada → Revisar público alvo
│
├── CPL ok mas Baixa Taxa de Conversão?
│   ├── Page Load Rate baixo? → Problema técnico na Landing Page → TI/Design
│   └── Página abre mas o lide não compra → Oferta/Copy fraca → Revisar VSL
│
└── CPL ok + Conversão ok mas Baixo ROAS?
    ├── Ticket Médio caiu? → Revisar mix de produtos (upsell, order bump)
    └── Taxa/Comissão alta? → Revisar plataforma e checkout
```

### Benchmarks de Referência (Perpétuo)
| Métrica | Sinal de Alerta | Referência Saudável |
|---|---|---|
| ROAS Bruto | < 2x | ≥ 3x |
| ROAS Líquido | < 1.5x | ≥ 2.5x |
| CTR | < 1% | ≥ 2% |
| CPM | Crescimento > 30% no mês | Estável ou diminuindo |
| Taxa Conversão Página | < 1% | ≥ 2–3% |

---

## 2. Lançamentos — Atenção por Fase

### Fase 1 — Captação
| Sinal | Diagnóstico |
|---|---|
| CPL > 2× métrica normal | Criativo/Público ruim — pausar e testar. |
| Ritmo de lead baixo | Ajustar orçamento diário ou expansão. |
| CTR < 1% | Gancho do anúncio do evento não converte. |

### Fase 2 — Aquecimento / CPL
| Sinal | Diagnóstico |
|---|---|
| Comparecimento < 30% | E-mails e lembretes de WA fracos. |
| Saídas do grupo WA > 20% | Conteúdo de engajamento do grupo não retém. |

### Fase 3 — Carrinho Aberto
| Sinal | Diagnóstico |
|---|---|
| Vendas nas primeiras 2h baixas | Urgência não foi bem ancorada no final do Webnário. |
| ROI < 3× | Avaliar custo extra de plataformas vs faturamento real. |

---

## 3. Regras Gerais de Análise

1. **Compare sempre com a meta primeiramente**, e então com o YoM. Crescimento mês a mês sem a meta não diz a verdade absoluta.
2. **Nunca tome ação drástica de reestruturação por 1 semana ruim.** Busque a tendência (3-4 semanas) antes de parar campanhas que convertiam.
3. **Sempre separe tráfego pago de tráfego orgânico.** 
4. **LTV baixo → problema de produto/CS.** Não é problema do gestor de tráfego, comunicar cliente para rever entrega.
5. **Dado sujo invalida diagnóstico.** Se o pixel disparou 2x ou o CRM está desatualizado, conserte os dados primeiro.
