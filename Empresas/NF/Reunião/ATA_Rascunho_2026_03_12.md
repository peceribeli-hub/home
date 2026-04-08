# Reunião NaFazendaPontoCom — Pós-Reunião
**Data:** 12 de março de 2026 · 14h00
**Duração:** 89 minutos
**Participantes:** Mariane Ferro · Matheus Moretti · Paola Peduzzi · Regis Povolati (REVO Advisory)

---

## P1 · Plano de Ação

| #   | Prioridade      | Ação                                                                                | Responsável       | Prazo               | Entregável                                                    |
| --- | --------------- | ----------------------------------------------------------------------------------- | ----------------- | ------------------- | ------------------------------------------------------------- |
| 01  | 🔴 Crítico      | Configurar disparos via API para Dia do Consumidor (domingo 15/03 + segunda 16/03)  | **Kayque (REVO)** | **Sáb 14/03**       | Automações programadas e agendadas                            |
| 02  | 🟡 Importante   | Enviar planilha de pontos de contato com cópias sugeridas para o Gerente de Pasto   | Regis             | **Seg 16/03**       | Planilha com datas, tipo de mensagem e narrativa sugerida     |
| 03  | 🟡 Importante   | Testar hospedagem de página HTML no Vercel (alternativa à Hostinger)                | Matheus           | **Próxima semana**  | Comparativo de taxa de carregamento Hostinger vs Vercel       |
| 04  | 🟢 Complementar | Configurar e-mail marketing na plataforma (market@nafazenda.com) e criar automações | Mariane + Regis   | **Até 17/03**       | Automação configurada com as 3 mensagens (cadastro, D+5, D-1) |
| 05  | 🟢 Complementar | Portal do cliente pronto e organizado                                               | Regis             | **Até 17/03 (seg)** | Link funcional com reuniões, planilhas e criativos            |

---

## P2 · Cronograma do Gerente de Pasto

```
MARÇO 2026

14/03 (sáb)   → Captação começa. Primeiros criativos estáticos no ar.
               → Campanha Dia do Consumidor: disparo via API (domingo/segunda)

16/03 (seg)   → Planilha de pontos de contato disponível para Mariane

17/03 (seg)   → Portal do cliente pronto (Regis)

19/03 (qua)   → REUNIÃO DE PLANEJAMENTO da próxima Imersão — 14h (Regis + Matheus)

23/03 (dom)   → GRUPOS DE AQUECIMENTO
               → Abertura + boas-vindas + envio do formulário de dúvidas

24/03 (seg)   → Reenvio do formulário

25/03 (ter)   → Último reenvio do formulário

27/03 (sex)   → Grupos em standby — "estamos processando suas dúvidas"

28/03 (sáb)   → Resposta às dúvidas do formulário nos grupos (D-2)

29/03 (dom)   → ABERTURA DOS GRUPOS (manhã cedo, ~2h de duração)
               → Josmar e Edmar disponíveis para responder (confirmar até 26/03)
               → Clientes ocultos com perguntas preparadas para quebrar o gelo
               → Revelação da oferta (domingo à noite)

30/03 (seg)   → CARRINHO ABERTO — 7h da manhã
               → Monitorar suporte/comercial durante o dia
               → Promoção para grupo de alunos quem enviar comprovante
               → Carrinho fecha às 23h59

31/03 (ter)   → DIA DE DESCANSO (avaliar feeling do suporte)
               → Se houver demanda reprimida: reabertura-relâmpago de 2h a 24h
```

---

## P3 · Recomendações Estratégicas

### 3.1 Mudar métrica de otimização de tráfego no próximo lançamento
**Situação:** Atualmente otimiza por custo de ingresso (CAC).
**Recomendação:** Otimizar por **"custo de ingresso com order bump"** — aceitar pagar até 2x mais caro por um lead se ele estiver comprando o combo, pois a taxa de conversão para o produto principal é 2x maior.
- Isso é exatamente o que está sendo feito no lançamento LATAM referenciado por Regis
- Requer criativos segmentados por perfil (pecuarista vs. outros) para poder otimizar a audiência certa

### 3.2 Migrar hospedagem de páginas para Vercel + HTML gerado por Antigravity
**Situação:** Turbo Cloud oscila, Lovable não melhora a taxa de carregamento.
**Recomendação:** Testar Vercel (gratuito) com páginas HTML geradas pelo Antigravity (IA local do Regis).
- Referência com US$30K de investimento usando esse stack tem taxa de carregamento linear a ~75%+
- Processo: Antigravity gera HTML → salva arquivo → sobe no Vercel → domínio próprio gratuitamente
- Acesso ao Antigravity já enviado para o Matheus

### 3.3 Implementar estrutura de e-mail marketing antes do próximo lançamento maior
**Situação:** E-mail nunca foi prioridade e foi abandonado. A plataforma atual tem módulo de e-mail disponível.
**Recomendação:** Configurar o e-mail marketing@ com 3 automações básicas e testar aquecimento da base antes de lançamentos de R$50K+.
- Risco: primeiro disparo em domínio virgem tende a ir para spam — fazer disparo de aquecimento antes
- Mesmo conteúdo do WhatsApp pode ser adaptado

### 3.4 Sistematizar o processo de aquecimento de grupos com planos de contingência
**Situação:** Aquecimento de grupos de WhatsApp feito de forma informal, sem plano B documentado.
**Recomendação:** Formalizar três níveis de resposta:
- **Plano A (termômetro):** Formulário de dúvidas (D-7 a D-5) — se resposta for boa, segue
- **Plano B (engajamento real):** Abertura de grupo com especialistas respondendo ao vivo por ~1h (D-1)
- **Plano C (último recurso):** Live no Instagram dos quatro (Regis + Mariane + Matheus + especialista)
- Em qualquer cenário: usar clientes ocultos com lista de perguntas preparadas para quebrar o gelo

### 3.5 Regravar sistematicamente os criativos que já funcionaram
**Situação:** Os criativos de melhor performance do Perpétuo estão documentados mas não foram replicados.
**Recomendação:** Antes de qualquer novo lançamento, listar os top 3–5 criativos do lançamento anterior e criar versões novas com o mesmo formato/gancho.
- Paola destacou isso na reunião
- O portal do cliente (previsto para segunda) vai centralizar esse histórico

---

## P4 · Próximas Reuniões

| Reunião | Data | Tipo | Pauta |
|---|---|---|---|
| Planejamento Imersão 2.0 | **Quarta, 19/03 — 14h** | Estratégia + Criação | Nome, narrativa, gancho ("sobreviveria da sua fazenda?"), pacotes, datas. Matheus traz sugestões. Regis alinha e facilita |
| Review Gerente de Pasto | **~31/03 ou 01/04** | Debriefing | Resultados do lançamento, ajustes para escalar, comparativo com Imersão anterior |

---

## P5 · Documento de Alinhamento

**Para:** Mariane Ferro, Matheus Moretti, Paola Peduzzi
**De:** Regis Povolati — REVO Advisory
**Reunião de:** 12/03/2026 · 89 min

---

### O que discutimos

Revisamos o debriefing completo da Imersão NaFazenda: o principal aprendizado é que **os order bumps foram o que salvou o resultado financeiro** — representaram quase o dobro do faturamento dos ingressos. Quem comprou o combo especial converteu para o XR Pack a 12%, contra 5,6% de quem comprou só o ingresso. Isso muda a forma de otimizar o tráfego no próximo lançamento.

Alinhamos a estratégia completa de aquecimento do Gerente de Pasto com três planos de contingência: formulário de dúvidas (Plano A), abertura de grupo com especialistas (Plano B) e live no Instagram (Plano C).

Decidimos aproveitar o Dia do Consumidor (15/03) para uma ação de renovação de base com 70% de desconto + SimulaPec, disparada via API no domingo e segunda.

Também discutimos a migração de hospedagem de páginas para Vercel + HTML gerado por Antigravity, que deve resolver a oscilação de carregamento que ainda persiste com a Turbo Cloud.

---

### O que ficou acordado

**Regis:**
- [x] ~~Configurar disparos via API da campanha Dia do Consumidor~~ — lista + copy da Mariane recebidas · execução com **Kayque (REVO)** ✅
- [ ] Enviar planilha de pontos de contato do Gerente de Pasto com narrativa sugerida (seg 16/03)
- [ ] Portal do cliente pronto até segunda 17/03
- [ ] Confirmar stack Antigravity + Vercel com Matheus

**Mariane:**
- [ ] Configurar e-mail marketing na plataforma (até 17/03)

**Matheus:**
- [ ] Testar hospedagem no Vercel usando HTML da Trava do Boi como base
- [x] ~~Explorar Antigravity para geração de páginas~~ — acesso já enviado pelo Regis
- [ ] Trazer sugestões de narrativa/gancho para reunião de concepção da Imersão 2.0 (19/03)

**Paola:**
- [x] ~~Validar dimensões dos criativos do Matheus e subir nos anúncios~~ — validado ✅
- [x] ~~Confirmar se API de conversões está registrando eventos adequadamente~~ — validado ✅

---

### Próxima reunião confirmada

**Quarta-feira, 19/03/2026 — 14h**
Planejamento da Imersão 2.0: narrativa, gancho, nome, estrutura e datas.
