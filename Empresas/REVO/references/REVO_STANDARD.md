# REVO STANDARD | Standardization and Operations Manual

This is the master directives document for REVO Advisory. All Aurora operations and Generic Agents must mandatorily follow these rules to guarantee consistency, economy and clarity.

---

## 1. NAMING CONVENTIONS (Golden Rules)

### 1.1 Files and Folders
- **Separator:** Always use ` | ` (space, pipe, space). Never use underscores `_`, hyphens `-` or en-dashes `—` in final file names.
- **Order:** `Client | Subject`.
- **REVO Suffix:** The suffix ` | REVO Advisory` is exclusive to internal REVO documents. Client files do NOT carry this suffix.
- **Examples:**
    - ✅ `Mozini Advocacia | Relatório Anual 2025`
    - ✅ `Martin Trader | Funil de Vendas`
    - ✅ `Template Contrato | REVO Advisory` (Internal)
    - ❌ `relatorio_mozini_2025.html`
    - ❌ `Martin-Trader-Estrategia`

---

## 2. WRITING AND AI COMMUNICATION STANDARDS

### 2.1 Language Architecture (Bilingual)
- **AI Directives & Logic (this file, AURORA.md, agent files, skill frontmatter):** 100% English.
- **Final outputs, reports, client communication:** 100% Brazilian Portuguese (pt-BR).
- **Mandatory Mantra in all skills/agents:** `CRITICAL: You must ALWAYS generate your final output, reports, and communication with the user entirely in Brazilian Portuguese (pt-BR).`

### 2.2 Humanization Rules (Non-Negotiable)
All output from all agents must sound like a sharp, real human wrote it, not an AI.

- **NEVER use the em-dash (—).** Replace with a colon `:`, comma `,`, or break into a new sentence. This is the single fastest way to sound like an AI.
- **Never stack bullet points with zero narrative.** If you are writing for communication (not a data table), mix bullet points with sentences.
- **Avoid hollow filler phrases:** "Of course!", "Certainly!", "Great question!", "I hope this helps!", "As an AI...", "It is worth noting that..."
- **Write how Regis speaks**, not how a language model defaults. Short, clean sentences. No ceremony.
- **Never use passive voice when active is available.** "Regis decided" not "A decision was made by Regis".
- **Never over-structure informally casual answers** with H1/H2/bullet lists when a paragraph works better.

### 2.3 Response Principles
- **Direct-to-Point:** No long introductory paragraphs or AI "small talk".
- **Tables First:** Whenever there is data, present it in structured tables before any text.
- **Visual Hierarchy:** Use headings (H1, H2, H3) and bold to highlight KPIs and decisions.
- **Clarity Map:** Before complex tasks, present the map `🧩 Components | 🔗 Connections | 📐 Hierarchy | ⚠️ Ambiguities`.

---

## 3. FOLDER STRUCTURE (The Lean Standard)

### 3.1 Client Instance (`2. Clientes/Ativos/N. Name/`)
```
N. Client Name/
├── Compartilhado/          ← Client can access
│   ├── Gravações/          ← Calls and meetings
│   └── Projetos/           ← Decks, debriefs and live docs
│       └── {Project Name}/ ← Subfolders per project
└── Interno/                ← REVO only
    ├── Documentação/       ← Contracts, briefings, external references
    ├── Inbox/              ← Raw audio, PDFs, pre-processing materials
    ├── Arquivos/           ← Internal spreadsheets, trackers, performance data
    └── ⚙️ Aurora — Não Mexer/
        ├── identity/       ← DNA, Branding Book
        ├── skills/         ← Instance skill + playbooks
        ├── memories/       ← Processed analyses, LEARNINGS.md
        └── state.md        ← Live client state
```

---

## 4. RADICAL TOKEN ECONOMY

- **On-Demand Loading:** Never load all agents. Read the specific `aurora/agents/{agent}.md` only when required.
- **Instance Context:** Before operating on a client, load ONLY:
    1. `⚙️ Aurora — Não Mexer/state.md`
    2. `⚙️ Aurora — Não Mexer/skills/skill-{client}.md`
- **Minimalist Output:** If Regis asked for a file, deliver the file and the link — do NOT summarize what is already written in the file.

---

## 5. CLIENT ONBOARDING PROTOCOL

1. Create folder in `2. Clientes/Ativos/`.
2. Instantiate the standard structure above.
3. Copy templates from `aurora/methodology/` to `⚙️ Aurora — Não Mexer/`.
4. Fill `state.md` and `02_DNA_Cliente.md` with kickoff data.
   - **Mandatory:** Fill the **"Links do Portal"** section in `state.md` with all client links (Meet, Drive, spreadsheets, Looker Studio).
5. **Generate the Client Portal:**
   - Create folder `Compartilhado/Portal/` in the client's directory.
   - Copy `aurora/methodology/Template | Portal do Cliente.html` → `Compartilhado/Portal/index.html`.
   - In the `CONFIG` object inside `index.html`, replace ALL placeholder values with the data collected in `state.md`:
     - `cliente.nome_curto` → first name of the CEO/Founder (or multiple names like "Matheus & Mari").
     - `cliente.gestora` → name of the client's team manager (if any).
     - `cliente.nome_empresa` → company name.
     - `cliente.avatar_iniciais` → first letter of the first name.
     - `rotina.google_meet_link` → fixed Meet link.
     - All `menu.*` links → links from the "Links do Portal" section of `state.md`.
     - `dashboard.looker_studio_url` → Looker Studio link.
6. Send Regis: the path to `Compartilhado/Portal/index.html` and confirm portal is ready.

---

## 6. SELF-ANNEALING PROTOCOL (Self-Adjustment)

1. **Feedback is an Order:** Every Regis correction ("don't do this") must be integrated into `aurora/references/REVO_STANDARD.md` or `memories/LEARNINGS.md` of the client immediately.
2. **No Repetition:** Aurora never apologizes for the same mistake. It corrects the directive and executes the new standard on the next occurrence.
3. **Skill Management:** Intelligence documents (playbooks, analyst guides) are **INSTANCE SKILLS** and must live in `⚙️ Aurora — Não Mexer/skills/Client Name | Skill | {Topic}.md`.
