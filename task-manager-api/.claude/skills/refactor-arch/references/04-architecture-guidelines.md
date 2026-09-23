# Guidelines de Arquitetura — Padrão MVC Alvo

Usado na **Fase 3** para decidir a estrutura final. As regras abaixo são agnósticas de linguagem; os exemplos de layout mostram como aplicá-las em Python/Flask e Node.js/Express — adapte o mesmo princípio para qualquer outra stack detectada na Fase 1.

## Camadas e responsabilidades

### Models
- Único ponto de acesso a dados (queries, ORM, schema).
- Contém validação **de dado** (formato, obrigatoriedade, invariantes do domínio: ex. `is_overdue()`, `validate_status()`).
- **Não conhece** HTTP: sem `request`/`response`, sem status code, sem rota.
- Sem SQL concatenado com input externo — sempre parametrizado ou via ORM.

### Views / Routes
- Só define rota → handler e faz o parsing de request / serialização de response.
- Delega toda decisão de negócio ao Controller (ou direto ao Service, se o Controller for fino).
- Não faz query direta ao banco, não contém `if`/`else` de regra de negócio além de "esse campo obrigatório veio no request?".

### Controllers
- Orquestram o caso de uso: recebem dados já parseados da View, chamam Model(s)/Service(s) na ordem certa, decidem o resultado (sucesso/erro) e devolvem um objeto de resposta para a View serializar.
- Não fazem SQL direto — sempre through Model.
- Concentram a regra de "o que fazer quando", não "como acessar o banco".

### Services (quando a regra de negócio tem side-effects ou cruza múltiplos models)
- Usado para lógica que não é puramente "buscar/salvar um registro": notificações, pagamento, cálculos que combinam vários Models.
- Injetado no Controller (via construtor/parâmetro), nunca instanciado silenciosamente dentro dele.

### Config
- Módulo único que lê segredos/portas/URLs de variável de ambiente (`os.environ`, `process.env`) com um default seguro só para dev local.
- Nenhum outro arquivo do projeto deve ter uma credencial ou flag de ambiente literal.

### Middlewares / Error Handling
- Tratamento de erro centralizado (um error handler global), não um `try/except`/`try/catch` repetido em cada handler de rota.
- Logging estruturado (nível + contexto), nunca `print`/`console.log` solto como única forma de log.

### Entry point (composition root)
- Único arquivo que importa e conecta tudo (config, DB, rotas, middlewares) e sobe o servidor.
- Não define lógica de negócio nem rotas inline.

## Regra de decisão: o que gerar em cada camada

| Se o código atual... | ...então na Fase 3 vira |
|---|---|
| Acessa banco (SQL/ORM) | Model |
| Só define rota HTTP e traduz request/response | View / Route |
| Decide o que fazer com os dados (orquestra models) | Controller |
| Tem side-effect (email, pagamento, notificação) ou cruza domínios | Service |
| É segredo/porta/flag de ambiente | Config |
| É tratamento de erro repetido | Middleware/error handler central |

## Layout de referência — Python/Flask

```
src/
├── config/
│   └── settings.py        # lê env vars, expõe SECRET_KEY, DB_PATH, DEBUG etc.
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── services/
│   └── notificacao_service.py
├── routes/
│   └── routes.py           # registra blueprints, sem lógica
├── middlewares/
│   └── error_handler.py
└── app.py                  # composition root
```

## Layout de referência — Node.js/Express

```
src/
├── config/
│   └── index.js            # lê process.env
├── models/
│   ├── userModel.js
│   └── courseModel.js
├── controllers/
│   ├── checkoutController.js
│   └── userController.js
├── services/
│   └── paymentService.js
├── routes/
│   └── index.js             # app.use('/api', ...), sem lógica
├── middlewares/
│   └── errorHandler.js
└── app.js                   # composition root (require + listen)
```

## Adaptação por nível de organização (Fase 1 → Fase 3)

- **Projeto Monolítico** (1-5 arquivos soltos): criar a estrutura de camadas do zero, movendo cada função para o arquivo correto por domínio.
- **Projeto Parcialmente organizado** (já tem `models/routes/services`, mas violado): **não recriar a árvore de pastas do zero** — mover apenas o código que está na camada errada (ex.: query direta dentro de uma rota vira chamada a um Model; validação duplicada vira uma função só chamada dos dois lugares; `Service` que existe mas não é usado passa a ser efetivamente chamado pelo Controller/Route). Preservar nomes de arquivo/função existentes sempre que possível para minimizar o diff.
- Nos dois casos, ao final, cada domínio (ex.: "produtos", "cursos", "tasks") deve ter seu próprio Model e Controller — nunca um arquivo único cobrindo todos os domínios.
