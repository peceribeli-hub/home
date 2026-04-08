# 📊 Modelo de Relatório Contínuo (Painel)
> Este modelo utiliza blocos expansíveis (`<details>`). Quando o cliente abrir o painel, a tela estará limpa. Ele clica no Mês, depois na Semana e expande os dois relatórios. O visual é corporativo (tabelas minimalistas e cartões HTML).

---

<details open>
  <summary><h2 style="display:inline-block; margin:0; cursor:pointer;" title="Clique para expandir o mês!">MÊS DE MARÇO 2026</h2></summary>
  <br>
  
  <details open>
    <summary><h3 style="display:inline-block; margin:0; cursor:pointer;" title="Clique para expandir a semana!">Semana 3 (16/03 a 20/03)</h3></summary>
    
    <!-- CARD 1: REPORT COMERCIAL -->
    <details open style="border: 1px solid #E2E8F0; border-left: 4px solid #F59E0B; margin-top: 15px; border-radius: 4px; background-color: #fafafa;">
      <summary style="cursor:pointer; font-size:16px; font-weight:bold; color:#333; outline:none; padding:15px; border-bottom:1px solid #ddd;">1. Report Comercial (CRM)</summary>
      <div style="padding: 15px;">
      <p style="color:#666; font-size:14px; margin-top:0;"><em>Visão executiva do pipeline e eficiência de vendas.</em></p>
      
      <ul>
        <li><b>Leads Recebidos (Total):</b> 29 Leads</li>
        <li><b>Lead MQL (Qualificados):</b>
            <br>&nbsp;&nbsp;&nbsp;9 Meta Ads
            <br>&nbsp;&nbsp;&nbsp;1 Google Ads
            <br>&nbsp;&nbsp;&nbsp;1 Indicação
        </li>
        <li><b>Lead SQL (Oportunidade):</b> 1 Indicação</li>
        <li><b>Reunião Agendada:</b> 1 Indicação</li>
        <li><b>Reunião Realizada:</b> 1 Indicação</li>
        <li><b>Leads Perdidos:</b>
            <br>&nbsp;&nbsp;&nbsp;3 Meta Ads
            <br>&nbsp;&nbsp;&nbsp;1 Google Ads
        </li>
        <li><b>Contratos Fechados:</b> <span style="color:#DE350B; font-weight:bold;">0</span></li>
      </ul>

      <details open style="margin-bottom: 20px;">
        <summary style="color: #CCC; font-weight: 500; font-size: 12px; text-transform: uppercase; cursor: pointer;">▶ Pipeline do Comercial (Etapas do CRM):</summary>
        <ul style="margin-top: 10px;">
          <li><b style="color: #3B82F6;">🔵 Meta Ads (20 Leads):</b><br>
            - <b>Reajuste Abusivo (10):</b> 1 Contato Inicial | 1 Resposta Inicial | 8 Qualificação<br>
            - <b>Procedimento (2):</b> 1 Qualificação | 1 Perdida (Problema resolvido)<br>
            - <b>Desconhecido (8):</b> 5 Cont. Inicial | 1 Resp. Inicial | 2 Perdidas (1 Tirar dúvidas, 1 Sem resposta)
          </li>
          <li><b style="color: #22C55E;">🟢 Google Ads (5 Leads):</b><br>
            - <b>Desconhecido (2):</b> 1 Contato Inicial | 1 Qualificação<br>
            - <b>Procedimento (1):</b> 1 Qualificação<br>
            - <b>Erro Médico (1):</b> 1 Qualificação<br>
            - <b>Sem Informação (1):</b> 1 Perdida (Tirar dúvidas)
          </li>
          <li><b style="color: #F97316;">🟠 Indicação (3 Leads):</b><br>
            - <b>Desconhecido (2):</b> 1 Qualificação | 1 Negociação<br>
            - <b>Desconhecido (1):</b> 1 Qualificação
          </li>
          <li><b style="color: #A855F7;">🟣 Canal Desconhecido (1 Lead):</b><br>
            - <b>Desconhecido (1):</b> 1 Qualificação
          </li>
        </ul>
      </details>

      <div style="background-color: #FFEBE6; border-left: 3px solid #DE350B; padding: 10px; margin-top: 15px; font-size: 14px; border-radius: 0 4px 4px 0;">
        <b style="color: #DE350B;">⚠️ Alertas de CRM:</b><br>
        Temos 1 lead da Meta do dia 18/03 (Paulo - 11986007397) que está sem atualização de status na planilha. Favor verificar para não esfriar.
      </div>
      </div>
    </details>

    <!-- CARD 2: REPORT META -->
    <details open style="border: 1px solid #E2E8F0; border-left: 4px solid #3B82F6; margin-top: 15px; border-radius: 4px; background-color: #fcfcfc;">
      <summary style="cursor:pointer; font-size:16px; font-weight:bold; color:#333; outline:none; padding:15px; border-bottom:1px solid #ddd;">2. Report Meta Ads</summary>
      <div style="padding: 15px;">
      <p style="color:#666; font-size:14px; margin-top:0;"><em>Performance das campanhas de captação, eficiência de custo e volume.</em></p>
      
      <ul>
        <li><b>Investimento total:</b> R$ 218,11</li>
        <li><b>Leads Gerados:</b>
            <br>&nbsp;&nbsp;&nbsp;20 Real
            <br>&nbsp;&nbsp;&nbsp;21 Alvo
        </li>
        <li><b>Custo por Lead (CPL):</b>
            <br>&nbsp;&nbsp;&nbsp;R$ 10,90 Real
            <br>&nbsp;&nbsp;&nbsp;R$ 10,39 Alvo
        </li>
        <li><b>Lead MQL:</b> 9 Meta Ads</li>
        <li><b>Custo Lead MQL:</b> <span style="color:#DE350B">R$ 24,23 Meta Ads</span></li>
        <li><b>Contrato Fechado:</b> <span style="color:#DE350B; font-weight:bold;">0</span></li>
      </ul>
      
      <h5 style="margin-bottom:5px;">Resumo por Demanda / Problema do Lead:</h5>
      <ul style="margin-top:0;">
        <li><b>Reajuste Abusivo:</b> 10 Leads | CPL: R$ 21,81</li>
        <li><b>Procedimento:</b> 2 Leads | CPL: R$ 109,05</li>
        <li><b>Desconhecido:</b> 8 Leads | CPL: R$ 27,26</li>
      </ul>

      <h5 style="margin-bottom:5px;">Top Criativos:</h5>
      <ul style="margin-top:0; margin-bottom: 5px;">
        <li><a href="https://www.instagram.com/p/DVwdF_XAGdi/#advertiser" target="_blank">AD012</a>: 13 Leads | Custo: R$ 2,51</li>
        <li><a href="https://www.instagram.com/p/DVqqY-UgMSA/#advertiser" target="_blank">VD027</a>: <span style="color:#DE350B">2 Leads* | Custo: R$ 40,10*</span></li>
        <li><a href="https://www.instagram.com/p/DVqqYVKAMwu/#advertiser" target="_blank">VD019</a>: 2 Leads | Custo: R$ 8,26</li>
        <li><a href="https://www.instagram.com/p/DVwwtMTAG2Q/#advertiser" target="_blank">VD022</a>: 2 Leads | Custo: R$ 24,27</li>
        <li><a href="https://www.instagram.com/p/DVqqZ3ZgIBB/#advertiser" target="_blank">VD025</a>: 2 Leads | Custo: R$ 4,22</li>
      </ul>
      <p style="font-size: 12px; color: #DE350B; margin-top: 0; margin-bottom: 15px;"><em>* Criativo Pausado</em></p>
      
      <p style="margin-bottom:0;"><b>💡 Ação do Tráfego:</b> [Pausados criativos VD022 por baixo CTR e escalado AD012 para captar mais demanda A.]</p>
      </div>
    </details>

    <!-- CARD 3: REPORT GOOGLE -->
    <details style="border: 1px solid #E2E8F0; border-left: 4px solid #34A853; margin-top: 15px; border-radius: 4px; background-color: #fafafa;">
      <summary style="cursor:pointer; font-size:16px; font-weight:bold; color:#333; outline:none; padding:15px; border-bottom:1px solid #ddd;">3. Report Google Ads</summary>
      <div style="padding: 15px;">
      <p style="color:#666; font-size:14px; margin-top:0;"><em>Performance das campanhas de rede de pesquisa.</em></p>
      
      <ul>
        <li><b>Investimento total:</b> R$ 81,42</li>
        <li><b>Leads Gerados:</b> 5 Leads</li>
        <li><b>Custo por Lead (CPL):</b> R$ 16,28</li>
        <li><b>Lead MQL:</b> 1 Lead</li>
        <li><b>Custo Lead MQL:</b> <span style="color:#DE350B">R$ 81,42</span></li>
      </ul>
      
      <h5 style="margin-bottom:5px;">Resumo por Demanda:</h5>
      <ul style="margin-top:0;">
        <li><b>Desconhecido:</b> 2 Leads | CPL: R$ 40,71</li>
        <li><b>Procedimento:</b> 1 Lead | CPL: R$ 81,42</li>
        <li><b>Erro Médico:</b> 1 Lead | CPL: R$ 81,42</li>
        <li><b>Sem Informação:</b> 1 Lead | CPL: R$ 81,42</li>
      </ul>
      </div>
    </details>
    <br>
  </details>

  <details>
    <summary><h3 style="display:inline-block; margin:0; cursor:pointer; color:#7A869A;" title="Clique para expandir a semana!">Semana 4 (23/03 a 27/03)</h3></summary>
    <div style="padding: 10px; color: #666; font-style: italic;">
     Os dados desta semana ainda não foram compilados.
    </div>
  </details>

</details>

---

<details>
  <summary><h2 style="display:inline-block; margin:0; cursor:pointer; color:#7A869A;" title="Clique para expandir o mês!">MÊS DE ABRIL 2026</h2></summary>
  <br>
  <p style="color:#888;"><em>Será iniciado ao término de Março.</em></p>
</details>

<!-- Fim do Template -->
