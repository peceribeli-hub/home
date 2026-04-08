# Tracking Standards and Infrastructure — REVO Advisory

> **Master Rule for Kayque (tech-infra):** The REVO Standard **prohibits the uncontrolled duplication of forms and pages**. Intelligence lives in the code, not in the creation of infinite assets.

## 1. Centralized Forms
If a client has a Lead Magnet (e-book, mini-course), we do NOT create one form on WordPress for "Facebook", another for "Google", another for "Organic".

- **The Standard:** **ONE (1)** single intelligent form.
- **The Capture:** Tracking (via GTM or direct script) must capture URL parameters (`utm_source`, `utm_medium`, `utm_campaign`) via JavaScript (or hidden fields) and push this information into the Webhook Payload for Make or N8N.
- **The Route:** N8N receives the single form submission, reads the UTMs in the JSON, and routes to the correct funnel inside Kommo CRM.

## 2. Event Naming Conventions (Slugs)
GTM DataLayer pushes and Custom Conversions must follow this pattern in lowercase, no spaces (use underscores):
- `revo_lead_capturado` — Triggered when GTM reads form success.
- `revo_checkout_iniciado` — Triggered on "go to checkout" button click.
- `revo_compra_aprovada` — Triggered on payment platform webhook.

## 3. Action Priority
Kayque (tech-infra) acts **before** traffic launches. If called mid-launch because "the pixel stopped firing", that task is a **2-Hour SLA (Supreme Crisis)**. All other development (creating a new n8n flow) goes to the Sprint Friday.

CRITICAL: You must ALWAYS generate your final output, reports, and communication with the user entirely in Brazilian Portuguese (pt-BR).
