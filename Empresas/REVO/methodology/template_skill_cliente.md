---
name: template-skill-cliente
description: Skill de instância de cliente. Carrega o DNA, estado atual e playbooks de um cliente específico para contextualizar qualquer agente da Plataforma REVO. Copie este template para ⚙️ Aurora — Não Mexer/skills/skill-{nome-cliente}.md ao abrir um novo cliente.
---

# Skill: [Nome do Cliente]

> **Instrução Aurora:** Esta skill é o "óculos" que você coloca antes de operar sobre este cliente. Sempre carregue-a antes de qualquer agente especialista quando a tarefa for sobre este cliente.

---

## 1. Contexto do Cliente

- **DNA:** Leia `../identity/02_DNA_Cliente.md`
- **Estado atual:** Leia `../state.md`

## 2. Regras Específicas deste Cliente

- [Ex: Nunca usar a palavra "curso" — o produto é "método"]
- [Ex: O cliente prefere relatórios mensais, não semanais]
- [Ex: Comunicação sempre via WhatsApp, nunca e-mail]

## 3. Playbooks Disponíveis

| Playbook | Descrição | Arquivo |
|---|---|---|
| [Nome] | [O que faz] | [caminho relativo] |

## 4. Agentes Utilizados

| Agente | Quando usar |
|---|---|
| `data-analyst` | Relatórios de performance, análise de métricas |
| `strategic-clone` | Posicionamento, funis, planejamento |
| `copywriter` | Scripts, roteiros, copys de anúncios |
| `project-manager` | Gestão de entregas, SLAs |

## 5. Estado de Onboarding

- [ ] DNA preenchido
- [ ] state.md preenchido  
- [ ] Estrutura de pastas criada
- [ ] Primeira reunião realizada
- [ ] Dashboard configurado
- [ ] Rastreio (Pixel/UTM) validado
