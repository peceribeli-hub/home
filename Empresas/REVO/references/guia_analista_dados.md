# Data Analyst Guide — Funnel Diagnosis

> **Audience:** Paola (Data Analyst) and REVO data team
> **Purpose:** This document translates report numbers into diagnostic questions. When an indicator is off-target, use this guide to identify the root cause before recommending action.
> **This is NOT** for the client report — it is the backstage of the analysis.

---

## 1. Perpetual Funnel — Diagnostic Tree

```
Low ROAS?
│
├── High CPL?
│   ├── High CPM?      → Saturated audience or weak creative → Refresh creatives
│   ├── Low CTR?       → Hook/Creative not converting → Test new angles
│   └── CPL ok but low CTR → Wrong targeting → Review audience
│
├── CPL ok but low Conversion Rate?
│   ├── Low Page Load Rate? → Technical issue on the page → Escalate to Tech-Infra
│   └── Page loading but not converting → Weak offer or copy → Review VSL/Sales Letter
│
└── CPL ok + Conversion ok but low ROAS?
    ├── Average Ticket dropped? → Review product mix (upsell, order bump)
    └── Commission/Fees increased? → Review platform and payment methods
```

### Reference Benchmarks (Perpetual Funnel)

| Metric | Warning Signal | Healthy Reference |
|---|---|---|
| Gross ROAS | < 2x | ≥ 3x |
| Net ROAS | < 1.5x | ≥ 2.5x |
| CTR | < 1% | ≥ 2% |
| CPM | Growth > 30% m/m | Stable or decreasing |
| Page Conversion Rate | < 1% | ≥ 2–3% |
| LTV / CAC | < 2x | ≥ 3x |

---

## 2. Meeting Funnel — Diagnostic Tree

```
Closed Sales below goal?
│
├── Low Close Rate?
│   ├── Unqualified leads arriving → See Tier 3: lead source
│   └── Closer underperforming → Review sales script / training
│
├── Low Show-up Rate?
│   ├── Appointments not showing → Problem in confirmation process (WABot, reminder)
│   └── Cold leads being scheduled → Review WA qualification before scheduling
│
├── Low Scheduling Rate?
│   └── Leads arriving but not scheduling → Review WA copy and follow-up
│
└── Low Lead Volume?
    ├── Organic dropped? → See which organic channel declined (Feed? Stories? DM?)
    └── Paid died?       → Review campaigns and creatives
```

### Reading the Lead Origin Table

| Signal | What to do |
|---|---|
| Organic > 60% of total | Strong authority signal — maintain content rhythm |
| Referral > 20% | Create formal referral program — it's working naturally |
| Paid with CPL much above CAC/10 | Review creative and targeting |
| One origin with 2× Conversion Rate vs others | Double down on that origin |

---

## 3. Launch Funnel — Key Attention Points by Phase

### Phase 1 — Acquisition

| Signal | Diagnosis |
|---|---|
| CPL > 2× benchmark | Bad creative or targeting — pause and test variations |
| Lead pace below target in week 1 | Adjust budget or expand audience |
| CTR < 1% | Ad hook is not working |

### Phase 2 — Event / Warm-up

| Signal | Diagnosis |
|---|---|
| Attendance < 30% of leads | Weak warm-up sequence or bad time slot |
| WA group exits > 20% | Warm-up content is not engaging |

### Phase 3 — Cart Open

| Signal | Diagnosis |
|---|---|
| Sales in first 2h < 20% of total cart *(Meteoric)* | Urgency was not well built in the event |
| CPA much above CPL × expected factor | Review offer and installment conditions |
| ROI < 3× | Assess whether operation cost is compatible with revenue |

---

## 4. General Analysis Rules

1. **Always compare against the established goal first**, then YoY. YoY without goal context is not a diagnosis.
2. **Never take action based on 1 bad week.** Look at the 3–4 week trend before any structural change.
3. **Always separate paid from organic traffic.** A bad paid week does not mean the entire funnel is broken.
4. **LTV/CAC below 2x → trigger immediate alert to Regis.** This is a model problem, not a campaign problem.
5. **Dirty data invalidates the diagnosis.** If Pixel is duplicated, UTM is wrong, or Kommo is outdated — fix it before analyzing.

---

*Metric reference: `aurora/references/arquitetura_funis.md`*
*Templates: `aurora/methodology/template_relatorio_semanal.md` · `aurora/methodology/template_relatorio_mensal.md`*

CRITICAL: You must ALWAYS generate your final output, reports, and communication with the user entirely in Brazilian Portuguese (pt-BR).
