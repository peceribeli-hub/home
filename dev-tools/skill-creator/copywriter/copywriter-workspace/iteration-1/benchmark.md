# Benchmark — Skill Copywriter | Iteration 1

## Resultado Geral

| Config | Eval 1 (Formulário) | Eval 2 (VSL) | Taxa Geral |
|---|---|---|---|
| **with_skill** | 4/4 (100%) | 4/4 (100%) | **100%** |
| **without_skill** | 1/4 (25%) | 1/4 (25%) | **25%** |

**Delta:** +75 p.p. de melhoria com a skill ativa.

---

## Detalhes por Assertion

### Eval 1: Formulário de Aplicação Advisory

| Assertion | with_skill | without_skill |
|---|---|---|
| Sem em-dash | ✅ PASS | ✅ PASS (coincidência) |
| Sem linguagem prescritiva | ✅ PASS | ❌ FAIL |
| Tom data-driven (CPL/ROAS/Kommo) | ✅ PASS | ❌ FAIL |
| Repulsão Anti-Alvo presente | ✅ PASS | ❌ FAIL |

### Eval 2: Script de VSL

| Assertion | with_skill | without_skill |
|---|---|---|
| Sem em-dash | ✅ PASS | ✅ PASS (coincidência) |
| Mecanismo Único presente | ✅ PASS | ❌ FAIL |
| Destruição da Ponte ativa | ✅ PASS | ❌ FAIL |
| Sem jargões proibidos | ✅ PASS | ❌ FAIL |

---

## Análise do Analista

**Pontos fortes da skill:**
- A skill elimina completamente os erros de linguagem prescritiva e jargões proibidos.
- O Mecanismo Único (Kommo CRM + 3 dashboards + Advisory) aparece organicamente nos outputs, sem necessidade de prompt específico.
- A "Destruição da Ponte" foi aplicada com estrutura narrativa correta (crença antiga → dado → alternativa).
- O formulário construiu filtros reais de Anti-Alvo que funcionam como qualificação automática.

**Pontos de atenção:**
- O "Sem em-dash" passou nas duas configs — pode ser que essa assertion não seja discriminante o suficiente. Considerar adicionar uma assertion de "tom de voz — sem 'você deve' e sem 'Olá tudo bem'" para ser mais específica.
- Ambos outputs with_skill dependem dos assets terem sido carregados antes. Sem os arquivos de IDP, o comportamento pode degradar. Considerar adicionar um mecanismo de verificação no início da skill que impede a geração sem os arquivos.

**Recomendação para Iteration 2:**
- Adicionar assertion explícita de "Frase Âncora" ("Só acredito em Deus, de resto me traga os dados") nos outputs.
- Testar um eval sem os arquivos IDP para validar que a skill recusa a gerar output (comportamento de bloqueio).

---

*Iteration 1 concluída. Outputs disponíveis em `copywriter-workspace/iteration-1/`*
