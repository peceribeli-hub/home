# Content Analysis Protocol — REVO Advisory

> **Usage:** Follow this protocol whenever Regis places files in `aurora/inbox/content/`. The goal is to ensure each piece of content is vetted by all Aurora specialists sequentially and in a controlled manner.

## 🔄 The Processing Loop (Queue of 1)

Process **one file at a time**. Do not batch-analyze. Only move to the next when the current one is archived.

### Step 1: Diagnosis (Clarity + Specialist Feedback)
1. **Aurora:** Apply the `Clarity Map` (Step 0 of AURORA.md pipeline).
2. **Regis²:** Analyze if the content is aligned with the "Nerd da Roça" vision and competitive intelligence.
3. **Brand:** Check if language and identity conform to brand guidelines.
4. **Project-Manager:** Assess if this content causes new tasks or impacts on launches/SLAs.

### Step 2: The Adjustment Report
Present Regis with a single consolidated report containing:
- **✅ What's good:** Strengths.
- **🛠️ Adjustment Suggestions:** Specific improvements suggested by the specialist review.
- **🚀 Execution Potential:** What happens if we authorize (e.g., becomes a script, a post, an automation).

### Step 3: Wait for Authorization
Always end with:
`"Aguardando autorização para executar os ajustes neste arquivo. Responda [AUTORIZADO] para seguir."`

## 🛠️ Execution and Archiving
After `[AUTORIZADO]`:
1. Execute the suggested changes to the file.
2. Generate output files (if any).
3. Move the original file to `aurora/inbox/content/archive/`.
4. Ask: `"Ajustes concluídos. Podemos ir para o próximo arquivo?"`

CRITICAL: You must ALWAYS generate your final output, reports, and communication with the user entirely in Brazilian Portuguese (pt-BR).
