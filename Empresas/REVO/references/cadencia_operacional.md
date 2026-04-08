# Operational Cadence — REVO Advisory

> **For Aurora:** This document defines WHEN and HOW to generate reports for each client. Always consult the client's `state.md` to pull goals and YoY history before generating any report.

---

## 1. Weekly and Monthly Rituals

### 📅 Weekly Report — Every Monday

**Who receives it:** All clients with Active Advisory status (see client `state.md`)  
**Scope:** Previous week (Monday to Sunday)  
**Template:** `aurora/methodology/template_relatorio_semanal.md`

**Generation flow:**
1. Aurora identifies all active clients with priority 🟡 High or 🔴 Maximum
2. For each client, reads `state.md` → pulls active funnels and weekly goals
3. Requests from Regis (or Paola) the realized data for the week
4. Fills weekly template with data and generates written analysis
5. Delivers the formatted report

**Current cadence clients (Mar/2026):**

| Client | Funnels in Report | Slug |
|---|---|---|
| NaFazendaPontoCom | Growth + Perpetual + Launch (MGP) | `nafazenda` |
| Martin Trader | Growth + Standard Launch | `martin-trader` |
| Teacher Marcos | To confirm with Regis | — |
| Mozini Advocacia | Meeting Funnel | — |
| REVO Advisory | Growth (Instagram) | `revo` |

---

### 📋 Monthly Report — 1st Friday of the Month

**Who receives it:** All Active Advisory clients  
**Scope:** Full previous month  
**Template:** `aurora/methodology/template_relatorio_mensal.md`

**2026 Schedule:**

| Reference Month | Report Date |
|---|---|
| February/2026 | 06/Mar/2026 (Friday) ← **next** |
| March/2026 | 03/Apr/2026 (Friday) |
| April/2026 | 08/May/2026 (Friday) |
| May/2026 | 05/Jun/2026 (Friday) |
| June/2026 | 03/Jul/2026 (Friday) |

**Generation flow:**
1. Aurora identifies all active clients
2. For each client, reads `state.md` → pulls active funnels, monthly goals and YoY history
3. Requests from Regis / Paola the consolidated data for the month
4. Fills monthly template, calculates % attainment and ∆ YoY
5. Generates strategic analysis and guidelines for the next month
6. **Mandatory action at the end:** Updates client `state.md` with the closed month's YoY history

---

## 2. Mandatory Fields in Every Report

Regardless of type (weekly or monthly), every report must contain:

| Field | How to calculate | Source |
|---|---|---|
| **Goal** | Defined in client `state.md` (section: KPIs and Active Goals) | `state.md` |
| **Realized** | Provided by Regis or Paola (real data for the period) | Manual input |
| **% Attainment** | `(Realized / Goal) × 100` | Calculated |
| **YoY** | Same metric, same period in the previous year | `state.md` (YoY History table) |
| **∆ YoY** | `((Realized − YoY) / YoY) × 100` | Calculated |

> ⚠️ If the YoY field is `—` in `state.md`, indicate "History to be built (first cycle)" in the report. Never invent or estimate YoY without real data.

---

## 3. When Aurora Acts vs. When Input is Needed

| Situation | Aurora acts alone? | What is needed |
|---|---|---|
| Calculate % attainment and ∆ YoY | ✅ Yes | Goals and realized figures provided |
| Generate written analysis | ✅ Yes | Context of the numbers |
| Pull goals for the period | ✅ Yes | Updated `state.md` |
| Get realized data for the period | ❌ No | Paola sends data (Ads Manager, sales platform) |
| Define new goals | ❌ No | Regis defines, Aurora records in `state.md` |
| YoY for 1st cycle | ❌ No | No history = field `—`, progressive construction |

---

## 4. References

- **Metrics by funnel:** `aurora/references/arquitetura_funis.md`
- **Weekly template:** `aurora/methodology/template_relatorio_semanal.md`
- **Monthly template:** `aurora/methodology/template_relatorio_mensal.md`
- **State per client:** `2. Clientes/Ativos/{client}/Interno/⚙️ Aurora — Não Mexer/state.md`

CRITICAL: You must ALWAYS generate your final output, reports, and communication with the user entirely in Brazilian Portuguese (pt-BR).
