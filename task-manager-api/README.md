# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`, já refatorada para MVC.

## Como rodar

```bash
pip install -r requirements.txt
cp .env.example .env   # opcional: ajuste SECRET_KEY, PORT, SMTP etc.
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000` (ou na porta de `PORT`). O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo; **rode-o antes do primeiro boot**, senão os endpoints retornam listas vazias. Os usuários de exemplo têm senhas fixas só para desenvolvimento (`joao@email.com` / `1234` é admin).

## Estrutura

```
app.py              # composition root (create_app): config, DB, services, controllers, rotas
config/settings.py  # lê variáveis de ambiente (.env)
database.py         # instância SQLAlchemy + CRUDMixin
models/             # entidades ORM, queries, constantes, validators, erros de domínio
controllers/        # casos de uso por domínio (tasks, users, categories, reports)
services/           # auth (token assinado), notificação (SMTP injetável), relatórios agregados
routes/             # blueprints: só request -> controller -> JSON
middlewares/        # error handler central
```

## Autenticação

`POST /login` devolve um token assinado (`itsdangerous`, validade `TOKEN_MAX_AGE`; invalidado quando a senha muda).
Envie-o como `Authorization: Bearer <token>`:

- `PUT /users/<id>` e `DELETE /users/<id>`: o próprio usuário ou um admin.
- Criar usuário com role `admin`/`manager`, ou alterar `role`/`active`: só admin.
