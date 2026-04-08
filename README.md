# Painel REVO - Relatórios Automatizados

Sistema de painéis de relatórios para clientes, com login e dados extraídos automaticamente do Google Sheets.

## Estrutura

```
├── api/
│   └── index.py          # API principal (login + relatórios)
├── generate_hash.py      # Utilitário para gerar hash de senha
├── requirements.txt       # Dependências Python
├── .env.example          # Exemplo de configuração
└── README.md             # Este arquivo
```

## Como Configurar um Novo Cliente

### 1. Gere o hash da senha

```bash
python generate_hash.py sua_senha
```

Copie o hash gerado.

### 2. Configure no Vercel

No Vercel, vá em **Settings → Environment Variables** e adicione:

```
GOOGLE_CREDENTIALS      = (cole todo conteúdo do credentials.json)
CLIENT_1_EMAIL          = cliente1@email.com
CLIENT_1_PASSWORD_HASH = (cole o hash gerado)
CLIENT_1_NAME          = Nome do Cliente
CLIENT_1_SHEET_ID      = ID da planilha do cliente

CLIENT_2_EMAIL          = cliente2@email.com
CLIENT_2_PASSWORD_HASH  = (hash da senha do cliente 2)
CLIENT_2_NAME           = Nome do Cliente 2
CLIENT_2_SHEET_ID       = ID da planilha do cliente 2
```

### 3. Deploy

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/SEU_USUARIO/repo.git
git push -u origin main
```

Depois conecte o repo no Vercel e faça deploy.

## Como Funciona

1. Cliente acessa a URL → vê página de login
2. Faz login com e-mail e senha
3. Vê os dados da planilha vinculada
4. Pode clicar em "Atualizar" para buscar dados novos

## Estrutura das Planilhas

Cada cliente precisa ter 3 abas com IDs específicos:

1. **Kommo (CRM)** - ID: `899775580`
2. **Meta Ads** - ID: `1936428443`
3. **Google Ads** - ID: `677341941`

## Regras do Relatório

- **Semanas:** Quarta a Terça
- **Ordem dos cards:** Comercial → Meta Ads → Google Ads
- **Canal:** "Desconhecido" (sem prefixo "Canal")
- **Pipeline:** `<div>` com `<strong>` (não `<ul><li>`)
