================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask==3.1.1, flask-cors==5.0.1, sqlite3 (stdlib)
Domain:        E-commerce API (produtos, usuários, pedidos, relatórios de vendas)
Architecture:  Monolítica — 4 arquivos soltos na raiz, sem pastas de camada; models.py (314 linhas) mistura acesso a dados e regra de negócio de 4 domínios, e app.py tem rotas que acessam o banco direto
Source files:  4 files analyzed (app.py, controllers.py, database.py, models.py)
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 5 | HIGH: 3 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] Credenciais / Segredos Hardcoded
File: app.py:7, controllers.py:287-289, database.py:76-78
Description: O `SECRET_KEY` está escrito direto no código. O `/health` devolve esse segredo, o `db_path` e `debug` na resposta JSON. As senhas iniciais (`admin123`, `123456`, `senha123`) também estão fixas no código.
Impact: Qualquer um que chame `GET /health`, sem login, obtém a chave usada para assinar sessões. A conta admin tem uma senha conhecida em todo ambiente que for criado.
Recommendation: Mover o segredo para variável de ambiente lida por um módulo `config`, tirar dados de config/segredo da resposta do health e gerar as senhas iniciais a partir do ambiente (padrão "Extrair configuração para módulo config/env" do playbook).

### [CRITICAL] Execução de código/SQL arbitrário vindo do request
File: app.py:59-78, app.py:47-57
Description: `POST /admin/query` pega o campo `sql` do body e passa direto para `cursor.execute()`, sem autenticação nem allowlist. `POST /admin/reset-db`, também sem autenticação, apaga todas as tabelas.
Impact: Qualquer cliente HTTP pode ler a tabela `usuarios` inteira (com senhas), mudar preços/pedidos ou dropar o banco. Na prática, é tomada total do banco.
Recommendation: Remover o endpoint `/admin/query` (aqui o contrato muda de propósito). Tirar `/admin/reset-db` da API pública ou exigir auth + flag de ambiente dev (padrão "Remover endpoint de execução arbitrária" do playbook).

### [CRITICAL] God Class / God File
File: controllers.py:1-292, models.py:1-314
Description: models.py junta acesso a dados e regras de negócio de produtos, usuários, pedidos e relatórios: validação de estoque/cálculo de total em 133-169 e faixas de desconto em 256-262. controllers.py cuida de HTTP, validação, notificações e health para os 4 domínios.
Impact: Não dá para testar a regra de pedido/desconto sem um SQLite real. Qualquer mudança em um domínio mexe num arquivo compartilhado por todos, com alto risco de regressão.
Recommendation: Separar por domínio em `models/` (só acesso a dados), `services/` (regras), `controllers/` e `routes/` (ex.: `produto_model.py`, `pedido_service.py`), seguindo o padrão "Split de God File por domínio" do playbook.

### [CRITICAL] Criptografia fraca ou "caseira" (senha em texto puro)
File: database.py:76-78, models.py:83, models.py:99, models.py:109-111, models.py:126-129
Description: As senhas são gravadas e comparadas em texto puro, sem hash. `GET /usuarios` e `GET /usuarios/<id>` devolvem o campo `senha` na resposta.
Impact: Qualquer consulta a `/usuarios` ou vazamento do `loja.db` expõe as senhas reais de todos os usuários, que costumam ser reaproveitadas em outros serviços.
Recommendation: Gerar hash com `werkzeug.security.generate_password_hash` e checar com `check_password_hash` no service de auth. Nunca serializar `senha` em respostas (padrão "Hash de senha com biblioteca padrão" do playbook).

### [CRITICAL] SQL Injection (concatenação de string em query)
File: models.py:28, models.py:47-50, models.py:57-61, models.py:68, models.py:92, models.py:109-111, models.py:126-129, models.py:140, models.py:148-151, models.py:155, models.py:157-161, models.py:163-166, models.py:174, models.py:188, models.py:192, models.py:220, models.py:224, models.py:279-281, models.py:289-297
Description: Quase todas as queries são montadas com `+` a partir de dados do usuário (`nome`, `email`, `senha`, `termo`, `categoria`, `novo_status`, ...), sem placeholders `?`.
Impact: Um login com `email = "' OR 1=1 --"` passa sem senha e entra como o primeiro usuário (o admin). A busca `/produtos/busca?q=` permite `UNION SELECT` para extrair senhas.
Recommendation: Trocar tudo por queries parametrizadas (`cursor.execute("... WHERE id = ?", (id,))`). Na busca dinâmica, montar a cláusula com placeholders e uma lista de parâmetros (padrão "Queries parametrizadas" do playbook).

### [HIGH] Lógica de negócio pesada dentro do Controller/Route
File: app.py:47-78, controllers.py:24-62, controllers.py:188-220, controllers.py:237-255, controllers.py:264-292
Description: Os controllers orquestram efeitos colaterais: e-mail/SMS/push em 208-210 e notificação por status em 247-250. health_check e as rotas de admin em app.py rodam SQL direto. Regras de domínio, como a lista de categorias válidas e os limites de nome, ficam dentro do handler.
Impact: Não dá para reaproveitar a criação de pedido fora do HTTP (ex.: job ou fila) nem testá-la sem subir o Flask. A regra "cancelado → devolver estoque" está só num `print` e nunca é aplicada.
Recommendation: Controllers só traduzem request↔response. Criar `PedidoService.criar()` e `PedidoService.atualizar_status()` com um `NotificationService` separado, e passar o SQL do health para o model (padrão "Extrair para camada de Service" do playbook).

### [HIGH] Acoplamento forte / sem Injeção de Dependência
File: app.py:4, controllers.py:2-3, models.py:1, models.py:5 (e todas as funções de models.py que chamam get_db())
Description: Cada função de model chama `get_db()`, um singleton global importado direto. Os controllers importam o módulo `models` e também `get_db`.
Impact: Não dá para injetar um banco em memória ou um fake nos testes. Trocar SQLite por Postgres obriga a mexer em todas as funções.
Recommendation: Usar uma fábrica de conexão por requisição (`flask.g` + `teardown_appcontext`) e deixar models/services receberem a conexão ou repositório, com uma app factory `create_app()` (padrão "App factory + DI de conexão" do playbook).

### [HIGH] Estado global mutável
File: database.py:4-11
Description: Uma única `sqlite3.Connection` no nível do módulo, com `check_same_thread=False`, é compartilhada por todas as requisições e threads sem lock nem escopo de transação.
Impact: Requisições concorrentes dividem o mesmo cursor e a mesma transação. Se `criar_pedido` falhar no meio (models.py:148-166), os INSERTs parciais não sofrem rollback e são gravados pelo próximo `commit()` de outra requisição, gerando pedidos órfãos e estoque inconsistente.
Recommendation: Conexão por requisição guardada em `flask.g`, fechada no teardown, com transação explícita (`with conn:`) na criação de pedido (padrão "Conexão por request / transação explícita" do playbook).

### [MEDIUM] Queries N+1
File: models.py:187-199, models.py:219-231
Description: Para cada pedido é feita uma query de `itens_pedido`, e para cada item mais uma query em `produtos` para pegar o nome.
Impact: `GET /pedidos` com 100 pedidos de 5 itens roda cerca de 601 queries. O tempo de resposta cresce linearmente com o volume.
Recommendation: Uma query com `JOIN itens_pedido ... JOIN produtos` (ou `WHERE pedido_id IN (...)`) e agrupamento em Python (padrão "Eliminar N+1 com JOIN/batch" do playbook).

### [MEDIUM] Validação ausente ou duplicada inconsistente
File: controllers.py:28-54, controllers.py:72-90, controllers.py:150-158, controllers.py:169-171, controllers.py:239-240
Description: As validações de produto em create e update são copiadas, e o update esquece o tamanho do nome e a categoria válida. Não há checagem de tipo: `preco: "abc"` gera `TypeError` e resposta 500. O `email` não tem validação de formato. `login` e `atualizar_status_pedido` quebram com body vazio (`None.get`), devolvendo 500 em vez de 400.
Impact: Dá para gravar um produto com categoria inválida via PUT. Um input ruim vira erro 500 em vez de 400, e as regras divergem quando só um dos lados é alterado.
Recommendation: Extrair um validador/schema compartilhado (ex.: `validators/produto.py` com `validar_produto(dados, parcial=False)`) usado por create e update (padrão "Validação centralizada" do playbook).

### [MEDIUM] Duplicação de lógica de negócio (viola DRY)
File: models.py:12-21, models.py:31-40, models.py:304-313, models.py:79-86, models.py:96-102, models.py:171-201, models.py:203-233
Description: O mapeamento row→dict de produto aparece 3 vezes e o de usuário 2 vezes. `get_pedidos_usuario` e `get_todos_pedidos` são praticamente idênticas, mudando só o `WHERE`.
Impact: Adicionar um campo (ex.: `imagem_url`) exige editar 3 lugares. Esquecer um deixa o formato de resposta diferente entre endpoints.
Recommendation: Funções `_row_to_produto`, `_row_to_usuario` e uma `_listar_pedidos(where, params)` compartilhada (padrão "Extrair serializer/helper comum" do playbook).

### [MEDIUM] Configuração misturada com código
File: app.py:7-8, app.py:88, database.py:5, controllers.py:285-289
Description: `DEBUG=True`, host/porta, `db_path` e `"ambiente": "producao"` estão escritos direto em vários arquivos.
Impact: Não dá para separar dev de prod. `debug=True` com `host="0.0.0.0"` expõe o debugger do Werkzeug na rede, o que abre caminho para execução de código remoto. O health diz "producao" enquanto roda em debug.
Recommendation: Um módulo `config.py` lendo `SECRET_KEY`, `DEBUG`, `DB_PATH`, `PORT` e `APP_ENV` de variáveis de ambiente com defaults seguros (padrão "Extrair configuração para módulo config/env" do playbook).

### [LOW] Exceção genérica engolindo erros
File: controllers.py:10-12, controllers.py:21-22, controllers.py:60-62, controllers.py:95-96, controllers.py:108-109, controllers.py:125-126, controllers.py:133-134, controllers.py:143-144, controllers.py:164-165, controllers.py:185-186, controllers.py:218-220, controllers.py:226-227, controllers.py:234-235, controllers.py:254-255, controllers.py:261-262, controllers.py:291-292, app.py:77-78
Description: Todo handler faz `except Exception as e` e devolve `str(e)` ao cliente com status 500. O único "log" é um `print`, que ainda grava e-mails de usuários no stdout (controllers.py:161, 179, 182).
Impact: Mensagens internas do SQLite e da stack vazam para o cliente, erros de validação viram 500 e não há log estruturado para investigar em produção.
Recommendation: Error handler central (`@app.errorhandler`) com exceções de domínio (ex.: `ValidationError`→400, `NotFoundError`→404), `logging` no lugar de `print` e mensagem genérica no 500 (padrão "Tratamento de erro centralizado" do playbook).

### [LOW] Magic numbers/strings e nomenclatura ruim
File: models.py:256-262, models.py:150, models.py:247-253, controllers.py:52, controllers.py:242, controllers.py:56, controllers.py:160, models.py:2, database.py:2
Description: As faixas de desconto (10000/5000/1000 → 0.1/0.05/0.02), os status (`'pendente'`, `'aprovado'`, ...) e as categorias são literais soltos. A variável `id` sobrescreve o builtin. Há imports sem uso (`sqlite3` em models.py e `os` em database.py).
Impact: Um erro de digitação num status (`'aprovad'`) passa sem aviso e quebra o relatório. Mudar uma faixa de desconto exige achar números sem nome no meio do código.
Recommendation: Constantes/enum em `models/constants.py` (`StatusPedido`, `CATEGORIAS_VALIDAS`, `FAIXAS_DESCONTO`), renomear `id` para `produto_id`/`usuario_id` e remover os imports sem uso (padrão "Constantes nomeadas" do playbook).

================================
Total: 14 findings
================================
