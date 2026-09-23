# Análise de Projeto — Heurísticas de Detecção

Usado na **Fase 1**. O objetivo é preencher o resumo sem perguntar nada ao usuário — tudo deve ser inferível do próprio código.

## 1. Linguagem

Conte arquivos-fonte por extensão (ignore `node_modules/`, `venv/`, `.git/`, `dist/`, `build/`, `__pycache__/`):

| Extensão | Linguagem |
|---|---|
| `.py` | Python |
| `.js`, `.mjs`, `.cjs` | JavaScript |
| `.ts` | TypeScript |
| `.java` | Java |
| `.go` | Go |
| `.rb` | Ruby |
| `.php` | PHP |

A linguagem dominante é a de maior contagem de arquivos-fonte (excluindo testes/config).

## 2. Gerenciador de pacotes e Framework

Leia o arquivo de manifesto correspondente e liste as dependências relevantes:

| Manifesto | Linguagem | O que olhar |
|---|---|---|
| `requirements.txt`, `pyproject.toml`, `Pipfile` | Python | `flask`, `django`, `fastapi`, `flask-sqlalchemy`, `flask-cors` + versão pinada |
| `package.json` | Node.js | `dependencies`/`devDependencies`: `express`, `fastify`, `@nestjs/core`, `koa` + versão |
| `pom.xml`, `build.gradle` | Java | `spring-boot-starter-*` |
| `go.mod` | Go | módulos `gin-gonic`, `echo`, `fiber` |

Se nenhum framework web aparecer, confirme por padrões de código (`app.get(...)`, `@app.route(...)`, `router.Handle(...)`).

**Framework = biblioteca + versão exata do manifesto** (ex.: "Flask 3.1.1"), nunca só o nome.

## 3. Banco de dados

Procure, em ordem:
1. Import/require de driver ou ORM: `sqlite3`, `psycopg2`, `pymongo`, `sqlalchemy`, `mongoose`, `pg`, `mysql2`, `prisma`
2. Strings de conexão (`sqlite:///`, `postgresql://`, `mongodb://`)
3. Statements `CREATE TABLE` / `db.Schema` / classes de `Model` de ORM — cada uma vira uma "tabela" no resumo
4. Pastas `migrations/`, arquivos `schema.prisma`, `models.py`/`models/*.py`

Liste as tabelas/coleções pelo nome usado no schema, não pelo nome da classe se forem diferentes.

## 4. Domínio da aplicação

Não pergunte ao usuário — infira pelo vocabulário dominante em nomes de rotas, tabelas e classes:

- `produtos`, `pedidos`, `carrinho`, `estoque`, `checkout` → **E-commerce**
- `cursos`, `matriculas`/`enrollments`, `pagamentos`/`payments`, `alunos` → **LMS / plataforma de cursos**
- `tasks`, `categories`, `usuarios`/`users` com prioridade/status → **Task Manager / produtividade**
- `pacientes`, `consultas` → **Saúde**; `pedidos`+`mesas` → **Food service**; etc.

Descreva em uma linha curta (ex.: "E-commerce API (produtos, pedidos, usuários)").

## 5. Mapeamento de arquitetura atual

Classifique em uma das três categorias abaixo — isso guia o quão agressiva a Fase 3 precisa ser:

| Categoria | Sinal |
|---|---|
| **Monolítica** | Tudo em 1-5 arquivos soltos na raiz, sem pastas de camada, ou uma única classe "gerenciadora" com >100 linhas fazendo rota+dados+regra |
| **Parcialmente organizada** | Já existem pastas como `models/`, `routes/`, `services/`, mas as rotas/controllers ainda fazem acesso a dados direto, validação inline e/ou há camadas declaradas e nunca usadas (código morto) |
| **MVC aderente** | Separação real: rotas só roteiam, controllers/services concentram regra, models só acesso a dados — normalmente não é o caso dos projetos-alvo deste desafio |

Para chegar à classificação, verifique se cada pasta com nome de camada **realmente** tem responsabilidade única (ex.: uma `services/` que nunca é importada por nenhuma rota não conta como camada real).

## 6. Imprimir o resumo (fim da Fase 1)

Formato fixo (não pule nenhum campo, mesmo que "N/A"):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework + versão>
Dependencies:  <libs relevantes, separadas por vírgula>
Domain:        <domínio em 1 linha>
Architecture:  <Monolítica|Parcialmente organizada|MVC aderente> — <justificativa curta>
Source files:  <N> files analyzed
DB tables:     <lista de tabelas/coleções>
================================
```

Depois de imprimir, avance direto para a Fase 2 (não pare aqui pedindo confirmação — a Fase 2 é o primeiro ponto de parada obrigatório).
