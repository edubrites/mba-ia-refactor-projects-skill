================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python (3.13.2 no ambiente local)
Framework:     Flask 3.0.0
Dependencies:  flask-sqlalchemy 3.1.1, flask-cors 4.0.0, marshmallow 3.20.1 (declarada, não usada), requests 2.31.0 (declarada, não usada), python-dotenv 1.0.0 (declarada, não usada)
Domain:        Task Manager API (tasks, users, categories, reports de produtividade)
Architecture:  Parcialmente organizada — já existem models/, routes/, services/, utils/, mas as rotas fazem acesso direto ao ORM e contêm a regra de negócio e a validação; services/ e boa parte de utils/ são código morto (nunca importados)
Source files:  15 files analyzed
DB tables:     users, tasks, categories (SQLite, sqlite:///tasks.db via SQLAlchemy)
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0 (Flask-SQLAlchemy 3.1.1, SQLite)
Files:   15 analyzed | ~1158 lines of code

## Summary
CRITICAL: 4 | HIGH: 4 | MEDIUM: 6 | LOW: 5

## Findings

### [CRITICAL] Credenciais / Segredos Hardcoded
File: app.py:13, services/notification_service.py:7-10
Description: O SECRET_KEY do Flask ('super-secret-key-123') e as credenciais SMTP (host, porta, usuário 'taskmanager@gmail.com', senha 'senha123') estão escritos direto no código-fonte.
Impact: Quem tem acesso ao repositório consegue forjar cookies de sessão assinados e enviar e-mails pela conta SMTP. Trocar o segredo exige um novo deploy de código.
Recommendation: Mover para um módulo config/ central que lê de variáveis de ambiente (python-dotenv já está no requirements), sem fallback de segredo real (Playbook: Externalizar configuração).

### [CRITICAL] Criptografia fraca ou "caseira" (hash de senha)
File: models/user.py:29, models/user.py:32
Description: set_password/check_password guardam a senha como MD5 sem salt; a comparação usa `==` comum, que não é de tempo constante.
Impact: Se o banco vazar, as senhas (mínimo de 4 caracteres, como as do seed: '1234', 'abcd', 'pass') caem por rainbow table em segundos.
Recommendation: Trocar por werkzeug.security.generate_password_hash/check_password_hash (PBKDF2/scrypt com salt; o Werkzeug já vem com o Flask). Aceitar hashes MD5 antigos no login e regravar com o novo algoritmo (Playbook: Hash de senha seguro).

### [CRITICAL] Exposição de dado sensível (hash de senha na resposta)
File: models/user.py:21, routes/user_routes.py:33, routes/user_routes.py:85, routes/user_routes.py:129, routes/user_routes.py:209
Description: User.to_dict() inclui o campo 'password', e esse dicionário é devolvido em GET /users/<id>, POST /users, PUT /users/<id> e POST /login.
Impact: Qualquer cliente da API recebe o hash MD5 de qualquer usuário, o que junto com o finding anterior equivale a expor a própria senha.
Recommendation: Tirar 'password' da serialização do model/view. Nenhum cliente legítimo depende desse campo (Playbook: Serializer/View sem campos sensíveis).

### [CRITICAL] God Class / God File
File: routes/report_routes.py:1-223
Description: Um único blueprint de 223 linhas junta roteamento, queries ORM e regra de negócio de dois domínios diferentes: relatórios (linhas 12-155) e CRUD completo de categorias (linhas 157-223).
Impact: Mudar categorias exige mexer no módulo de relatórios. Não dá para testar nenhum dos dois domínios sem subir o Flask, e o nome do arquivo engana quem procura o CRUD de categorias.
Recommendation: Separar em category_routes.py + CategoryController e report_routes.py + ReportService, com as rotas só roteando (Playbook: Quebrar God File por domínio).

### [HIGH] Lógica de negócio pesada dentro do Controller/Route
File: routes/task_routes.py:11-63, routes/task_routes.py:85-154, routes/task_routes.py:156-223, routes/task_routes.py:273-299, routes/user_routes.py:42-90, routes/user_routes.py:92-132, routes/user_routes.py:134-151, routes/report_routes.py:12-101, routes/report_routes.py:103-155
Description: Os handlers validam campos, conferem se as entidades existem, fazem parse de datas e tags, calculam estatísticas e atraso, montam as respostas à mão e fazem a exclusão em cascata das tasks do usuário (user_routes.py:140-142), tudo usando db.session direto.
Impact: A regra fica presa ao HTTP e não dá para reaproveitar nem testar sem request. Qualquer mudança de regra obriga a editar vários handlers.
Recommendation: Extrair para controllers/ (request ↔ response) e services/ (task_service, user_service, report_service, category_service), deixando as rotas só com a declaração do endpoint (Playbook: Extrair camada de Service/Controller).

### [HIGH] Escalada de privilégio via atribuição em massa de role
File: routes/user_routes.py:52, routes/user_routes.py:71-72, routes/user_routes.py:119-122
Description: POST /users (cadastro público, sem autenticação) aceita 'role' do body, inclusive 'admin'. PUT /users/<id> deixa qualquer um trocar role e active de qualquer usuário.
Impact: Um atacante se cadastra como admin com uma única requisição, ou reativa e promove qualquer conta.
Recommendation: No cadastro, gravar sempre o role padrão 'user' ou uma allowlist explícita no service. Documentar que a troca de role/active precisa de autorização (Playbook: Allowlist de campos no Service).

### [HIGH] Token de autenticação falso/previsível
File: routes/user_routes.py:210
Description: O login devolve 'fake-jwt-token-' + user.id, um valor que qualquer pessoa adivinha sem saber a senha.
Impact: Qualquer consumidor que confie nesse token para autenticar pode ser enganado por um token forjado para outro usuário.
Recommendation: Gerar um token assinado com SECRET_KEY (itsdangerous.URLSafeTimedSerializer, que já vem com o Flask), mantendo o campo 'token' como string na resposta (Playbook: Token assinado).

### [HIGH] Acoplamento forte / sem Injeção de Dependência
File: services/notification_service.py:5-10, services/notification_service.py:15
Description: NotificationService fixa a configuração SMTP no construtor e cria smtplib.SMTP dentro de send_email.
Impact: Não dá para testar sem conexão real com o smtp.gmail.com nem trocar o transporte (fila, provider) sem editar a classe.
Recommendation: Receber a configuração e um sender/factory SMTP pelo construtor, com a configuração vinda de config/ (Playbook: Injeção de dependência via construtor).

### [MEDIUM] Camada declarada e nunca usada (código morto)
File: services/notification_service.py:1-48, utils/helpers.py:19-116, routes/report_routes.py:7
Description: NotificationService nunca é importado. validate_email, sanitize_string, generate_id, log_action, parse_date, is_valid_color, process_task_data e as constantes VALID_STATUSES/VALID_ROLES/etc. nunca são usados. format_date/calculate_percentage são importados e não chamados.
Impact: A estrutura de pastas passa a impressão de uma separação em camadas que não existe, e as regras duplicadas em helpers vão se afastando das regras reais das rotas.
Recommendation: Aproveitar as constantes e validações reais nos novos services/validators e apagar o que continuar sem uso. Deixar o NotificationService injetável e ainda sem integração (Playbook: Consolidar ou remover camada morta).

### [MEDIUM] Queries N+1
File: routes/task_routes.py:41-57, routes/report_routes.py:55-56, routes/report_routes.py:161-163, routes/user_routes.py:22, routes/task_routes.py:275-287, routes/report_routes.py:15-30
Description: GET /tasks faz User.query.get e Category.query.get para cada task. O relatório faz uma query de tasks por usuário, GET /categories uma contagem por categoria e GET /users um lazy-load de u.tasks por usuário. As estatísticas disparam de 9 a 12 COUNTs separados e ainda carregam todas as tasks na memória para contar as atrasadas.
Impact: O número de queries cresce linearmente com tasks/usuários/categorias. Com volume real, a listagem e os relatórios ficam lentos.
Recommendation: Usar eager loading (joinedload/selectinload) nas relações, GROUP BY para as contagens por status/prioridade/usuário/categoria e filtro SQL para as atrasadas (Playbook: Eliminar N+1 com eager loading/agregação).

### [MEDIUM] Validação ausente ou duplicada inconsistente
File: routes/task_routes.py:92-114, routes/task_routes.py:166-184, routes/task_routes.py:113, routes/task_routes.py:182, routes/task_routes.py:261, routes/task_routes.py:264, routes/user_routes.py:54-72, routes/user_routes.py:102-125, routes/report_routes.py:196-202
Description: A validação de task/user é reescrita no create e no update. priority não tem checagem de tipo (se vier "abc", `<` levanta TypeError e retorna 500). int() na busca estoura ValueError. update_category não verifica body nulo nem nada. O nome no update de user pode ficar vazio. Enquanto isso, utils.process_task_data existe e ninguém usa.
Impact: Entrada inválida vira 500 em vez de 400, e as regras de create e update já não batem (título sem strip no update de task, nome vazio aceito no PUT de user).
Recommendation: Centralizar em validators/ com uma função por entidade e modo create/update (partial), usada pelos services (Playbook: Validação centralizada).

### [MEDIUM] Duplicação de lógica de negócio (viola DRY)
File: routes/task_routes.py:30-39, routes/task_routes.py:71-80, routes/task_routes.py:283-287, routes/user_routes.py:171-180, routes/report_routes.py:33-36, routes/report_routes.py:132-135, models/task.py:50-60, routes/task_routes.py:17-28, routes/task_routes.py:276-279, routes/report_routes.py:19-22
Description: A regra de "task atrasada" está copiada em 6 lugares, embora Task.is_overdue() já exista. A serialização de task é refeita à mão em vez de usar to_dict(). As contagens por status aparecem em /tasks/stats e em /reports/summary.
Impact: Se a regra de atraso mudar (por exemplo, incluir um novo status final), algum dos 6 lugares fica para trás sem ninguém perceber e os endpoints passam a responder coisas diferentes.
Recommendation: Usar Task.is_overdue() e to_dict() como fonte única e centralizar as contagens no service (Playbook: Centralizar regra de domínio no Model/Service).

### [MEDIUM] Configuração misturada com código
File: app.py:11-13, app.py:34, services/notification_service.py:7-8
Description: URI do banco, SECRET_KEY, debug=True, host 0.0.0.0 e porta 5000 ficam inline no app.py, e o host/porta SMTP dentro do service.
Impact: Não há diferença entre dev e prod. O debug=True com o debugger do Werkzeug exposto em 0.0.0.0 permite execução remota de código na rede.
Recommendation: Criar config.py lendo de variáveis de ambiente, com defaults seguros (debug desligado), e um app factory create_app() (Playbook: Externalizar configuração / App factory).

### [MEDIUM] Uso de API/biblioteca deprecated
File: routes/task_routes.py:42, routes/task_routes.py:51, routes/task_routes.py:67, routes/task_routes.py:117, routes/task_routes.py:122, routes/task_routes.py:158, routes/task_routes.py:188, routes/task_routes.py:195, routes/task_routes.py:227, routes/user_routes.py:29, routes/user_routes.py:94, routes/user_routes.py:136, routes/user_routes.py:155, routes/report_routes.py:105, routes/report_routes.py:192, routes/report_routes.py:213, models/task.py:15-16, models/task.py:52, models/category.py:11, models/user.py:14, routes/task_routes.py:31, routes/task_routes.py:72, routes/task_routes.py:215, routes/task_routes.py:285, routes/user_routes.py:172, routes/report_routes.py:35, routes/report_routes.py:42, routes/report_routes.py:45, routes/report_routes.py:71, routes/report_routes.py:133, models/user.py:29
Description: Model.query.get(id) é legado desde o SQLAlchemy 2.0 (emite LegacyAPIWarning). datetime.utcnow() está deprecated desde o Python 3.12, e o ambiente é 3.13. hashlib.md5 é usado para senha.
Impact: Warnings a cada request e quebra quando as APIs forem removidas.
Recommendation: Trocar por db.session.get(Model, id), por datetime.now(timezone.utc) através de um helper utcnow() central (mantendo naive UTC para não mudar o formato gravado no SQLite) e por werkzeug.security para senha (Playbook: Migrar APIs deprecated).

### [LOW] Exceção genérica engolindo erros
File: routes/task_routes.py:62, routes/task_routes.py:137, routes/task_routes.py:151, routes/task_routes.py:204, routes/task_routes.py:221, routes/task_routes.py:236, routes/user_routes.py:87, routes/user_routes.py:130, routes/user_routes.py:150, routes/report_routes.py:186, routes/report_routes.py:208, routes/report_routes.py:222, utils/helpers.py:46, utils/helpers.py:48, utils/helpers.py:88
Description: Há `except:` sem tipo (que captura até KeyboardInterrupt/SystemExit) e `except Exception` que só devolve uma mensagem genérica, sem log estruturado.
Impact: A causa real de um 500 se perde, e erros de programação ficam escondidos atrás de "Erro interno".
Recommendation: Capturar exceções específicas (ValueError, SQLAlchemyError), registrar com logging.exception e ter um errorhandler central no app (Playbook: Tratamento de erros centralizado).

### [LOW] Logging via print
File: routes/task_routes.py:149, routes/task_routes.py:153, routes/task_routes.py:219, routes/task_routes.py:234, routes/user_routes.py:83, routes/user_routes.py:89, routes/user_routes.py:147, services/notification_service.py:21, services/notification_service.py:24, utils/helpers.py:39-41
Description: Eventos e erros saem com print(), sem nível, logger ou contexto.
Impact: Não dá para filtrar ou desligar por ambiente nem mandar para um agregador de logs.
Recommendation: Trocar por logging.getLogger(__name__) com níveis info/error (Playbook: Tratamento de erros centralizado).

### [LOW] Imports não utilizados
File: app.py:7, routes/task_routes.py:7, routes/user_routes.py:6, routes/report_routes.py:7-8, models/task.py:3, utils/helpers.py:3-7
Description: os, sys, json, time, hashlib, re e math são importados e nunca usados. Em user_routes, hashlib e json sobram.
Impact: É ruído que esconde as dependências reais de cada módulo e confunde a análise de acoplamento.
Recommendation: Remover durante a reorganização dos módulos.

### [LOW] Magic numbers/strings e nomenclatura ruim
File: routes/task_routes.py:96-100, routes/task_routes.py:110, routes/task_routes.py:113, routes/task_routes.py:177, routes/task_routes.py:182, routes/user_routes.py:64, routes/user_routes.py:71, routes/user_routes.py:115, routes/user_routes.py:120, routes/report_routes.py:24-28, routes/report_routes.py:129, models/task.py:39, models/task.py:46
Description: A lista de status, a de roles, os limites de título (3/200), de senha (4), de prioridade (1-5, "alta" = <=2) e o mapa prioridade→rótulo aparecem como literais repetidos. Variáveis têm uma letra só (t, u, c, p, p1..p5). As constantes certas já existem em utils/helpers.py:110-116 e ninguém usa.
Impact: Um erro de digitação em um status passa despercebido, e mudar um limite obriga a caçar literais.
Recommendation: Centralizar em um módulo de constantes de domínio (models/constants) usado por models/validators/services (Playbook: Constantes de domínio).

### [LOW] Condicional booleano redundante
File: models/task.py:38-43, models/task.py:45-48, models/task.py:50-60, models/user.py:34-38, utils/helpers.py:21-23, utils/helpers.py:53-55
Description: Aparece o padrão `if cond: return True else: return False`, e is_overdue usa três níveis de if aninhados para uma única expressão booleana.
Impact: É ruído que torna a regra de atraso, justamente a mais duplicada, mais difícil de ler e de conferir.
Recommendation: Trocar por `return <expressão>` (ex.: `return bool(self.due_date) and self.due_date < utcnow() and self.status not in FINAL_STATUSES`).

================================
Total: 19 findings
================================
