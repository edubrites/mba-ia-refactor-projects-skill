# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo.

## Configuração

Toda configuração vem de variáveis de ambiente (veja `.env.example`):

| Variável | Default | Observação |
|---|---|---|
| `APP_ENV` | `development` | Em `production`, `SECRET_KEY` é obrigatória |
| `SECRET_KEY` | aleatória (só dev) | |
| `DEBUG` | `false` | |
| `HOST` / `PORT` | `0.0.0.0` / `5000` | |
| `DB_PATH` | `loja.db` | |
| `SEED_USER_PASSWORD` | gerada e exibida no log | Senha dos usuários de exemplo criados no primeiro boot |
| `ADMIN_RESET_ENABLED` / `ADMIN_TOKEN` | `false` / — | Habilita `POST /admin/reset-db` (header `X-Admin-Token`) |

## Estrutura

```
app.py            # composition root (create_app)
config/           # settings lidos do ambiente
models/           # acesso a dados + validação/invariantes de domínio
controllers/      # orquestração dos casos de uso, um por domínio
services/         # regras com side-effects (pedido, notificação, relatório)
routes/           # blueprints: rota -> controller, parsing/serialização
middlewares/      # error handler central
```
