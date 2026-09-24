# Minha Solução

> O enunciado original do desafio está em [ENUNCIADO.md](ENUNCIADO.md).

## Análise Manual

Análise de código feita manualmente (sem a skill) nos três projetos-base, antes de qualquer decisão de design da skill. Achados ordenados por severidade, com arquivo:linha e justificativa de impacto.

### Projeto 1 — code-smells-project (Python/Flask, API de E-commerce)

| # | Severidade | Problema | Local |
|---|---|---|---|
| 1 | CRITICAL | SQL Injection generalizada — todas as queries em `models.py` são montadas por concatenação de string com dados do usuário | `models.py:28,48-50,58-60,68,92,110,127-128,140,148-166,174,188,192,196,206,220,224,239-296` |
| 2 | CRITICAL | Endpoint `/admin/query` executa SQL arbitrário vindo do corpo da requisição, sem autenticação | `app.py:59-78` |
| 3 | CRITICAL | Credenciais hardcoded — `SECRET_KEY` fixa e devolvida em texto claro por um endpoint público de health check | `app.py:7`, `app.py:289` |
| 4 | CRITICAL | God File — `models.py` (315 linhas) e `controllers.py` (293 linhas) concentram SQL, regra de negócio, validação e formatação para 4 domínios (produtos, usuários, pedidos, itens_pedido) | `models.py:1-315`, `controllers.py:1-293` |
| 5 | HIGH | Senhas armazenadas e comparadas em texto puro, sem hashing | `models.py:105-120,122-131` |
| 6 | HIGH | Lógica de negócio (simulação de envio de e-mail/SMS/push) presa dentro do Controller, sem camada de serviço | `controllers.py:188-220` |
| 7 | MEDIUM | Queries N+1 — cursores aninhados por pedido e por item de pedido em vez de JOIN | `models.py:171-201,203-233` |
| 8 | MEDIUM | `debug=True` e `DEBUG=True` hardcoded, sem módulo de configuração | `app.py:8,88` |
| 9 | LOW | `print()` como logging e concatenação de string em vez de f-strings | `controllers.py:8,11,57,61,106,161,179,182,208-210,219` |
| 10 | LOW | Lista de categorias válidas duplicada como "magic list" solta no controller | `controllers.py:52` |

**Justificativa:** os itens 1-4 comprometem segurança e integridade dos dados (SQLi + endpoint de SQL livre + segredo exposto), e a ausência total de camadas (item 4) é o exemplo mais puro de "God Class" citado no enunciado. Os itens 5-6 violam SRP/MVC ao misturar autenticação e orquestração de side-effects na camada errada. Os itens 7-10 são os problemas de padronização/performance/legibilidade que a Fase 2 também deve capturar.

### Projeto 2 — ecommerce-api-legacy (Node.js/Express, LMS com checkout)

| # | Severidade | Problema | Local |
|---|---|---|---|
| 1 | CRITICAL | Credenciais e chave de gateway de pagamento "live" hardcoded no código-fonte | `src/utils.js:2-7` |
| 2 | CRITICAL | Hashing de senha falso (`badCrypto`): apenas concatenações de base64, sem salt, sem algoritmo real | `src/utils.js:17-23` |
| 3 | CRITICAL | God Class `AppManager`: conexão de banco, schema, seed, todas as rotas e todo o fluxo de checkout/pagamento/matrícula/auditoria em uma única classe | `src/AppManager.js:1-142` |
| 4 | HIGH | Callback hell — 4-5 níveis de callbacks aninhados no checkout e no relatório financeiro, sem propagação consistente de erro | `src/AppManager.js:37-77,80-129` |
| 5 | HIGH | Deleção de usuário não remove matrículas/pagamentos associados (o próprio texto de resposta admite dado órfão) | `src/AppManager.js:131-137` |
| 6 | MEDIUM | Queries N+1 em cascata no relatório financeiro (curso → matrículas → usuário/pagamento, tudo em loop) | `src/AppManager.js:80-129` |
| 7 | MEDIUM | Estado global mutável (`globalCache`, `totalRevenue`) compartilhado entre todas as requisições | `src/utils.js:9-10` |
| 8 | MEDIUM / API deprecated | Driver `sqlite3` 100% callback-based (API legada) em vez de bindings com Promise/async-await, causa raiz do callback hell | `src/AppManager.js` (todo o arquivo) |
| 9 | LOW | Nomes de variáveis não descritivos no fluxo mais crítico do sistema (pagamento) | `src/AppManager.js:29-33` |
| 10 | LOW | "Magic strings" de status de pagamento (`"PAID"`/`"DENIED"`) sem enum/constante | `src/AppManager.js:46,54` |

**Justificativa:** itens 1-3 são falhas de segurança/arquitetura que comprometem todo o sistema de pagamento (o domínio mais sensível do projeto). Item 5 quebra integridade referencial silenciosamente. Itens 6-8 são gargalos de performance e uso de API obsoleta que a skill precisa nomear explicitamente (requisito de detecção de APIs deprecated). Itens 9-10 são ruído de legibilidade que não impede funcionamento, mas dificulta manutenção.

### Projeto 3 — task-manager-api (Python/Flask, Task Manager parcialmente organizado)

| # | Severidade | Problema | Local |
|---|---|---|---|
| 1 | CRITICAL | Credenciais hardcoded — `SECRET_KEY` da aplicação e credenciais reais de SMTP | `app.py:13`, `services/notification_service.py:9-10` |
| 2 | HIGH | Hashing de senha com MD5 (quebrado, sem salt) | `models/user.py:27-32` |
| 3 | HIGH | "Token" de autenticação falso (`'fake-jwt-token-' + id`), sem verificação de token em nenhuma rota | `routes/user_routes.py:207-211` |
| 4 | MEDIUM | Queries N+1 repetidas em múltiplos endpoints (`get_tasks`, `summary_report`) | `routes/task_routes.py:41-57`, `routes/report_routes.py:53-68` |
| 5 | MEDIUM | Lógica de "tarefa atrasada" duplicada manualmente em 4 lugares em vez de reusar `Task.is_overdue()` | `models/task.py:50-60`, `routes/task_routes.py:30-39,71-80`, `routes/user_routes.py:171-180`, `routes/report_routes.py:33-37` |
| 6 | MEDIUM | Separação em camadas é só de nome: rotas fazem validação + orquestração + serialização diretamente, e `NotificationService` existe mas não é chamado por nenhuma rota (código morto) | `routes/task_routes.py`, `routes/user_routes.py`, `services/notification_service.py` |
| 7 | LOW | `except:` genérico engolindo qualquer erro, sem log | `routes/task_routes.py:62-63` (e outros) |
| 8 | LOW | Condicionais booleanos verbosos (`if cond: return True else: return False`) em vez de `return cond` | `models/task.py:38-48`, `models/user.py:34-38` |
| 9 | LOW / API deprecated | Uso do padrão legado `Model.query.get(id)` do SQLAlchemy em quase todas as rotas, em vez de `db.session.get(Model, id)` (recomendado desde SQLAlchemy 1.4/2.0) | `routes/task_routes.py:67,158,227`, `routes/user_routes.py:29,94,136` |

**Justificativa:** mesmo com pastas `models/routes/services/utils` já separadas, a organização é superficial — os problemas 1-3 são de segurança grave (equivalentes a CRITICAL/HIGH mesmo num projeto "arrumado"), e o item 6 mostra que ter uma pasta `services/` não significa que a camada de serviço é realmente usada. Este projeto valida que a skill precisa auditar responsabilidade real das camadas, não só a existência de pastas com nomes de MVC.

## Construção da Skill

### Decisões de design

- **`SKILL.md` enxuto (~700 palavras) + 5 arquivos de referência carregados sob demanda.** Cada fase só lê os arquivos de que precisa (Fase 1 → `01-project-analysis.md`; Fase 2 → `02-antipattern-catalog.md` + `03-report-template.md`; Fase 3 → `04-architecture-guidelines.md` + `05-refactoring-playbook.md`). Isso mapeia 1:1 com as 5 áreas de conhecimento obrigatórias do enunciado e mantém o prompt principal fácil de auditar.
- **`03-report-template.md` tem uma seção só para o gate de confirmação**, com uma frase fixa (`Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`) e a regra explícita "nunca leia/edite arquivo com intenção de refatorar antes desta pergunta". Isso era o requisito não-negociável do desafio, então virou a parte mais repetida/reforçada da skill (aparece no SKILL.md e na referência).
- **`04-architecture-guidelines.md` distingue duas estratégias de Fase 3**: recriar a árvore do zero (projeto monolítico) vs. mover só o que está na camada errada preservando nomes de arquivo/função (projeto já parcialmente organizado). Essa distinção foi essencial no Projeto 3: a skill não recriou `models/routes/services/utils`, só corrigiu quem fazia o quê dentro deles.
- **`01-project-analysis.md` inclui uma heurística anti-"pasta bonita"**: uma `services/` ou `utils/` que existe mas nunca é importada por nenhuma rota não conta como camada real. Essa regra geral (não um anti-pattern fixo no catálogo) foi o suficiente para a skill, sozinha, identificar "código morto disfarçado de camada" no Projeto 3 sem eu ter escrito esse finding explicitamente no catálogo.

### Anti-patterns no catálogo e por quê

O catálogo (`02-antipattern-catalog.md`) tem 16 anti-patterns cobrindo as 4 severidades, escolhidos a partir da análise manual dos 3 projetos-base (para garantir que a skill realmente detectaria o que eu já tinha achado manualmente) mais os itens que o próprio enunciado exige nominalmente:

- **Segurança/CRITICAL:** God Class, credenciais hardcoded, SQL Injection, execução de código/SQL arbitrário, criptografia fraca/caseira.
- **SOLID/HIGH:** lógica de negócio no Controller, acoplamento forte sem DI, estado global mutável.
- **Performance/padronização (MEDIUM):** N+1, validação ausente/duplicada, duplicação de lógica (DRY), configuração misturada com código.
- **Legibilidade (LOW):** exceção genérica, magic numbers/strings, condicional booleano redundante.
- **Transversal (obrigatório pelo enunciado):** uso de API/biblioteca deprecated — com sinais específicos por stack (`hashlib.md5`/`Model.query.get()`/`datetime.utcnow()` em Python; driver `sqlite3` 100% callback/`new Buffer()` em Node), sempre exigindo citar o equivalente moderno na recomendação.

### Como garanti que a skill é agnóstica de tecnologia

- As heurísticas de detecção (`01-project-analysis.md`) nunca assumem uma linguagem: elas descrevem *onde procurar* (manifestos de dependência, padrões de import/require, strings de conexão) e uma tabela de mapeamento por linguagem, não um caminho de arquivo fixo.
- O playbook de refatoração (`05-refactoring-playbook.md`) documenta o *princípio* da transformação (ex.: "parametrizar SQL") e só então mostra um exemplo de código concreto — a instrução explícita é "adapte a sintaxe para a linguagem real do projeto".
- A prova real é empírica: a mesma skill, copiada sem alterações, rodou em Python/Flask monolítico (Projeto 1), Node.js/Express com callback hell (Projeto 2) e Python/Flask parcialmente organizado (Projeto 3) — nos três casos detectando a stack certa na Fase 1 e produzindo relatórios com qualidade equivalente na Fase 2 (ver seção Resultados).

### Desafios encontrados

1. **Evitar findings inventados.** Adicionei a regra explícita no template do relatório para *omitir silenciosamente* a categoria de API deprecated quando não houver nenhuma detectável, em vez de forçar um finding só para preencher a categoria.
2. **Validação de boot sem comando fixo.** A Fase 3 não podia assumir `python app.py` nem `npm start` — a instrução manda a skill descobrir o comando real (manifest/README) e até lidar com imprevistos de ambiente (ex.: porta 5000 ocupada pelo AirPlay do macOS nos 3 projetos, contornado subindo em outra porta só para o teste).
3. **Não deixar a Fase 3 sair do escopo de MVC.** Adicionei a regra "preserve o comportamento observável de cada endpoint, a menos que o próprio finding exija mudar o contrato" — usada explicitamente pela skill para justificar remoções de endpoint (ex.: `/admin/query`) e para **não** inventar regra de negócio nova onde o achado era só estrutural (ex.: manter "cancelar pedido não devolve estoque de fato" no Projeto 1, por ser comportamento original preservado, não um anti-pattern).
4. **Achados que só aparecem refatorando.** Em todos os três projetos a skill encontrou pelo menos um problema novo só na Fase 3 (não previsto no relatório da Fase 2) — race condition de estoque, checkout sem transação e escalada de privilégio via troca de senha sem autenticação. A regra "se achar algo novo na Fase 3, corrija e declare explicitamente no resumo final" (já presente no SKILL.md) foi o que evitou que esses achados fossem corrigidos silenciosamente sem registro.

## Resultados

### Resumo dos relatórios de auditoria (Fase 2)

| Projeto | Stack detectada | Arquitetura inicial (Fase 1) | Total findings | CRITICAL | HIGH | MEDIUM | LOW |
|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python + Flask 3.1.1 | Monolítica (4 arquivos soltos) | 14 | 5 | 3 | 4 | 2 |
| 2 — ecommerce-api-legacy | Node.js + Express 4.22 / sqlite3 | Monolítica (God Class `AppManager`) | 12 | 3 | 3 | 4 | 2 |
| 3 — task-manager-api | Python + Flask 3.0 | Parcialmente organizada (camadas nomeadas, mas violadas) | 19 | 4 | 4 | 6 | 5 |

Relatórios completos em `reports/audit-project-{1,2,3}.md`. Os três batem os critérios de aceite obrigatórios: stack detectada corretamente, ≥5 findings, pelo menos 1 CRITICAL/HIGH, e a skill parou pedindo confirmação `[y/n]` antes de tocar em qualquer arquivo.

### Antes / depois da estrutura

**Projeto 1 — code-smells-project**
```
Antes                          Depois
app.py                         app.py                  (composition root)
controllers.py                 config/settings.py
models.py                      controllers/{produto,usuario,pedido,relatorio,sistema}_controller.py
database.py                    models/{produto,usuario,pedido,admin}_model.py + constants.py + errors.py + database.py
                                services/{pedido,notificacao,relatorio}_service.py
                                routes/routes.py
                                middlewares/error_handler.py
```

**Projeto 2 — ecommerce-api-legacy**
```
Antes                          Depois
src/app.js                     src/app.js              (composition root)
src/AppManager.js              src/config/{index,database,logger}.js
src/utils.js                   src/database/schema.js
                                src/models/{user,course,enrollment,payment,auditLog}Model.js
                                src/services/{checkout,report,user,payment,password}Service.js
                                src/controllers/{checkout,report,user}Controller.js
                                src/validators/requestValidators.js
                                src/routes/index.js
                                src/middlewares/{errorHandler,asyncHandler}.js
                                src/errors/AppError.js
```

**Projeto 3 — task-manager-api** (já tinha camadas nomeadas — a Fase 3 corrigiu responsabilidade, não recriou a árvore)
```
Antes                          Depois
app.py                         app.py                  (composition root)
database.py                    config/settings.py
seed.py                        database.py, seed.py    (mantidos)
models/{task,user,category}.py models/{task,user,category}.py (mantidos) + constants.py + errors.py + validators.py
routes/{task,user,report}_     controllers/{task,user,category,report}_controller.py  (novo)
  routes.py                    routes/{task,user,report,category,system}_routes.py (2 novas, 3 mantidas/emagrecidas)
services/notification_service.py (código morto) services/{notification,auth,report}_service.py (notification agora é usado de fato)
utils/helpers.py               utils/helpers.py (limpo: só o que é usado)
```

### Checklist de validação

Preenchido para os 3 projetos (validação independente feita nesta sessão: boot real em venv/`npm install` isolado, `curl` em pelo menos um endpoint de cada domínio, checagem de log).

| Item | Projeto 1 | Projeto 2 | Projeto 3 |
|---|---|---|---|
| Linguagem detectada corretamente | ✅ Python | ✅ JavaScript (Node.js) | ✅ Python |
| Framework detectado corretamente | ✅ Flask 3.1.1 | ✅ Express 4.22.1 | ✅ Flask 3.0.0 |
| Domínio da aplicação descrito corretamente | ✅ E-commerce | ✅ LMS + checkout | ✅ Task Manager |
| Nº de arquivos analisados condiz com a realidade | ✅ 4 | ✅ 3 | ✅ 15 |
| Relatório segue o template definido | ✅ | ✅ | ✅ |
| Cada finding tem arquivo e linhas exatos | ✅ | ✅ | ✅ |
| Findings ordenados por severidade | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 14 | ✅ 12 | ✅ 19 |
| Detecção de API deprecated incluída | ✅ (config/debug mode) | ✅ (driver sqlite3 callback, Express 4) | ✅ (`Model.query.get`, `datetime.utcnow`, MD5) |
| Pausa e pede confirmação antes da Fase 3 | ✅ | ✅ | ✅ |
| Estrutura de diretórios segue padrão MVC | ✅ | ✅ | ✅ |
| Config extraída, sem hardcoded | ✅ `.env.example` + `config/` | ✅ `.env.example` + `src/config/` | ✅ `.env.example` + `config/` |
| Models abstraem dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ `middlewares/error_handler.py` | ✅ `errorHandler.js` + `AppError` | ✅ `middlewares/error_handler.py` |
| Entry point claro | ✅ `app.py` (`create_app`) | ✅ `src/app.js` | ✅ `app.py` (`create_app`) |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem corretamente | ✅ | ✅ | ✅ |

### Evidência de execução (validação independente, fora da própria skill)

Trechos reais dos testes rodados nesta sessão após cada Fase 3, antes de commitar:

```
# Projeto 1 (porta 5050)
GET /produtos            → 200, lista de 10 produtos
POST /login (SQLi ' OR 1=1 --) → {"erro":"Email ou senha inválidos","sucesso":false}
POST /admin/query        → 404 (endpoint removido)
GET /usuarios            → sem campo "senha" na resposta

# Projeto 2 (porta 3050)
POST /api/checkout (cartão 4111...) → {"msg":"Sucesso","enrollment_id":2}
POST /api/checkout (cartão 5111...) → 400 (pagamento recusado, antes não validava)
GET  /api/admin/financial-report    → 200, revenue agregado via JOIN (sem N+1)
DELETE /api/users/999                → 404 (antes sempre respondia 200)
log do processo: "card":"****4444"   → cartão mascarado, chave de gateway não aparece no log

# Projeto 3 (porta 5060)
POST /login (joao@email.com / 1234, hash MD5 legado do seed) → 200, token assinado
GET  /users/1             → sem campo "password" na resposta
PUT  /users/2 sem token   → 401
POST /users role=admin sem token de admin → bloqueado ("Autenticação de administrador necessária")
POST /tasks description inválido (objeto) → 400 (antes derrubava com 500)
```

### Observações sobre o comportamento em stacks diferentes

- A qualidade dos relatórios foi equivalente nas duas linguagens (Python e JavaScript): mesma disciplina de arquivo:linha exato, mesma ordenação por severidade, mesmo gate de confirmação.
- No Projeto 2 (Node.js) a skill escreveu o relatório em inglês espontaneamente — a skill não fixa o idioma da saída, ela segue o contexto da sessão em que roda, e isso não afetou a estrutura nem a qualidade do relatório.
- O Projeto 3 foi o teste real da heurística "pasta com nome de camada ≠ camada de fato usada": a skill identificou que `services/notification_service.py` e boa parte de `utils/helpers.py` eram código morto, mesmo com a árvore de diretórios já parecendo MVC à primeira vista — e a Fase 3 corrigiu isso reaproveitando os arquivos existentes em vez de recriá-los.
- Nos três projetos a skill relatou explicitamente pelo menos um achado adicional só descoberto durante a própria refatoração (Fase 3), nunca escondendo essas mudanças de contrato dentro do diff sem explicação.

## Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado.
- Python 3.10+ para `code-smells-project` e `task-manager-api`.
- Node.js 18+ para `ecommerce-api-legacy`.

### Rodar a skill (Fases 1 → 2 → 3)

```bash
# Projeto 1 — Python/Flask (monolito)
cd code-smells-project
claude "/refactor-arch"
# revise o relatório da Fase 2 → responda "y" para prosseguir com a Fase 3

# Projeto 2 — Node.js/Express
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3 — Python/Flask (parcialmente organizado)
cd ../task-manager-api
claude "/refactor-arch"
```

A skill já está copiada dentro dos três projetos em `.claude/skills/refactor-arch/`. A Fase 2 sempre pausa e pede confirmação `[y/n]` antes de alterar qualquer arquivo; a Fase 3 só roda depois disso.

### Como validar que a refatoração funcionou

Depois da Fase 3, subir cada projeto isoladamente e testar os endpoints (é o mesmo processo usado para validar os 3 projetos nesta sessão):

```bash
# Projeto 1
cd code-smells-project
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
SECRET_KEY=dev-test PORT=5050 python app.py &
curl http://localhost:5050/produtos

# Projeto 2
cd ecommerce-api-legacy
npm install
PORT=3050 PAYMENT_GATEWAY_KEY=pk_test_dummy npm start &
curl http://localhost:3050/api/admin/financial-report

# Projeto 3
cd task-manager-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
SECRET_KEY=dev-test PORT=5060 python seed.py
SECRET_KEY=dev-test PORT=5060 python app.py &
curl http://localhost:5060/tasks
```

Se a porta `5000`/`3000` padrão estiver ocupada (comum no macOS por causa do AirPlay Receiver), use outra porta via variável de ambiente `PORT`, como acima.
