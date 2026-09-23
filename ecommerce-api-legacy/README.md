# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Configuração

Variáveis de ambiente (ver `.env.example`):

| Variável | Default | Descrição |
|---|---|---|
| `PORT` | `3000` | Porta HTTP |
| `DB_PATH` | `:memory:` | Caminho do arquivo SQLite |
| `PAYMENT_GATEWAY_KEY` | — | Chave do gateway de pagamento (obrigatória com `NODE_ENV=production`) |
| `SEED_USER_PASSWORD` | `change-me` | Senha do usuário de demonstração do seed |

`npm start` carrega automaticamente um `.env` local, se existir (`--env-file-if-exists`, Node ≥ 22.9).

## Estrutura

```
src/
├── app.js            # composition root: conecta config, DB, models, services, controllers e rotas
├── config/           # config via env, logger, adaptador Promise do sqlite3
├── database/         # schema e seed
├── models/           # acesso a dados por tabela (users, courses, enrollments, payments, audit_logs)
├── services/         # checkout (transação), relatório financeiro, pagamento, hashing de senha, usuários
├── controllers/      # tradução request ↔ response
├── validators/       # parsing/validação de entrada
├── routes/           # mapeamento rota → controller
├── middlewares/      # error handler central e wrapper async
└── errors/           # erros tipados (400/404)
```
