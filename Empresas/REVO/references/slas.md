# REVO SLAs and Priority Rules

> This document defines the exact Service Level Agreements (SLAs) used by REVO Advisory. The `project-manager` skill must strictly enforce these when assigning due dates to tasks.

## The Reality of Prioritization
1. **Not everything is a crisis.** Clients will label every request as urgent because they lack visibility ("ansiedade do cliente"). Our job is to categorize accurately.
2. **Weekends are for rest.** We do not respond or work on weekends unless a critical system is actively losing money (e.g., payment gateway is down during an open cart). Delay non-critical Friday requests to Monday.

## Standard SLAs

| Categoria da Tarefa | Descrição | SLA Oficial (Prazo Máximo) | Responsável Típico |
| :--- | :--- | :--- | :--- |
| **Crise Suprema** | Campanha principal saiu do ar, links de pagamento quebrados durante lançamento, servidor caiu. | **2 Horas Úteis** | Paola (Tráfego) ou Kayque (Infra) |
| **Dúvidas Operacionais** | Cliente esqueceu como usar o CRM, não sabe ler a planilha, ou não achou o link do evento. | **Até 24 Horas Úteis** | Priscila (Suporte/Gestão) |
| **Implementação Nova (Tráfego)** | Subir uma nova landing page, configurar um novo Pixel, ou rodar uma nova campanha. | **3 Dias Úteis** (após recebimento de *todos* os ativos) | Paola (Tráfego) |
| **Desenvolvimento de Automação** | Criar um novo fluxo no Make/n8n, integrar uma nova ferramenta, configurar banco de dados. | **Até a próxima Sexta-feira** da sprint semanal. | Kayque (Infra) |

## The Push-Back Protocol
If an input transcript shows a client demanding "Subir a campanha hoje" (Upload campaign today) and they just sent the creatives, the `project-manager` MUST flag this.

**Flag Example:**
`⚠️ ALERTA DE GERENTE: Cliente solicitou subida imediata. O SLA padrão da REVO é de 3 dias úteis para garantir qualidade no rastreio. Recomendo negociar o prazo para [Inserir Data].`

## Daily Cadence
*   Sprints run from Monday to Friday.
*   Prioritize unblocking the "Funil de Lançamento" leading up to event dates.
*   Always ensure "Automações" (like GTM/n8n) are scheduled BEFORE "Tráfego" is scheduled to go live. Traffic cannot run without tracking.
