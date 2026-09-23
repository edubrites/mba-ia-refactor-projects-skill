# Playbook de Refatoração

Usado na **Fase 3**. Cada padrão abaixo corresponde a um ou mais itens do catálogo de anti-patterns (referenciado entre colchetes). Adapte a sintaxe para a linguagem real do projeto — o princípio da transformação é o que importa, não o exemplo literal.

## 1. Extrair God File em Models + Controllers por domínio
`[God Class / God File]`

**Antes** (`models.py`, um arquivo para tudo):
```python
def get_todos_produtos(): ...
def criar_produto(...): ...
def get_todos_usuarios(): ...
def criar_pedido(...): ...
```

**Depois:**
```python
# models/produto_model.py
def get_todos(): ...
def criar(nome, preco, ...): ...

# models/pedido_model.py
def criar(usuario_id, itens): ...
```
Um arquivo/módulo por domínio, tanto em Model quanto em Controller. Nenhum arquivo deve ter funções de mais de um domínio de negócio.

## 2. Extrair segredos para módulo de configuração
`[Credenciais Hardcoded]`

**Antes:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
```

**Depois:**
```python
# config/settings.py
import os
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não configurada (defina em .env)")

# app.py
from config.settings import SECRET_KEY
app.config["SECRET_KEY"] = SECRET_KEY
```
Adicionar `.env.example` documentando as variáveis esperadas (sem valores reais) e `.env` ao `.gitignore`.

## 3. Parametrizar queries SQL
`[SQL Injection]`

**Antes:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```

**Depois:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```
Em Node.js com `sqlite3`: `db.get("SELECT * FROM courses WHERE id = ?", [id], cb)` (o projeto 2 já faz isso corretamente nesse trecho — usar como referência ao corrigir os demais).

## 4. Remover/isolar endpoint de execução arbitrária
`[Execução de código/SQL arbitrário]`

**Antes:**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    query = request.get_json().get("sql", "")
    cursor.execute(query)   # SQL arbitrário do usuário
```

**Depois:** remover o endpoint. Se a necessidade real por trás dele for administrativa (ex.: reset de dados de teste), substituir por operações específicas e auditáveis:
```python
# controllers/admin_controller.py
def resetar_dados_de_teste():
    """Só chamado por rota protegida por auth de admin, sem SQL livre."""
    produto_model.limpar_tabela_teste()
```

## 5. Trocar hashing fraco/custom por biblioteca padrão
`[Criptografia fraca]`

**Antes (Python, MD5 sem salt):**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```

**Depois:**
```python
from werkzeug.security import generate_password_hash, check_password_hash
self.password = generate_password_hash(pwd)
# validação: check_password_hash(self.password, pwd_informada)
```

**Antes (Node.js, `badCrypto` caseiro):**
```js
function badCrypto(pwd) { /* base64 repetido */ }
```

**Depois:**
```js
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(pwd, 10);
```

## 6. Mover lógica de negócio do Controller para Service
`[Lógica de negócio no Controller]`

**Antes:**
```python
def criar_pedido():
    resultado = models.criar_pedido(usuario_id, itens)
    print("ENVIANDO EMAIL: ...")
    print("ENVIANDO SMS: ...")
    return jsonify(resultado), 201
```

**Depois:**
```python
# services/notificacao_service.py
def notificar_pedido_criado(pedido): ...

# controllers/pedido_controller.py
def criar_pedido():
    resultado = pedido_model.criar(usuario_id, itens)
    notificacao_service.notificar_pedido_criado(resultado)
    return jsonify(resultado), 201
```

## 7. Injetar dependências em vez de instanciar internamente
`[Acoplamento forte / sem DI]`

**Antes:**
```js
class AppManager {
    constructor() {
        this.db = new sqlite3.Database(':memory:');
    }
}
```

**Depois:**
```js
class CourseController {
    constructor(db) {   // recebido de fora, injeta o real ou um fake em teste
        this.db = db;
    }
}
// composition root:
const db = createDatabase(config.dbPath);
const controller = new CourseController(db);
```

## 8. Eliminar estado global mutável
`[Estado global mutável]`

**Antes:**
```js
let globalCache = {};
function logAndCache(key, data) { globalCache[key] = data; }
```

**Depois:** encapsular em uma classe/instância injetada (ex.: `CacheService`) criada uma vez no composition root e passada para quem precisa, em vez de módulo compartilhado mutado por qualquer handler.

## 9. Resolver N+1 com JOIN / eager loading
`[Queries N+1]`

**Antes:**
```python
for pedido in pedidos:
    itens = cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido["id"],))
```

**Depois (SQL puro):**
```sql
SELECT p.*, ip.produto_id, ip.quantidade
FROM pedidos p
LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
WHERE p.usuario_id = ?
```
**Depois (SQLAlchemy):** `Pedido.query.options(joinedload(Pedido.itens)).filter_by(usuario_id=usuario_id).all()`

## 10. Centralizar lógica duplicada em um único método de Model
`[Duplicação de lógica de negócio]`

**Antes:** `due_date < now and status not in (...)` reescrito em 4 arquivos.

**Depois:**
```python
class Task(db.Model):
    def is_overdue(self):
        return bool(self.due_date and self.due_date < datetime.utcnow()
                    and self.status not in ("done", "cancelled"))
```
Todas as rotas/relatórios passam a chamar `task.is_overdue()`.

## 11. Tratamento de erro centralizado
`[Exceção genérica engolindo erros]`

**Antes:** `try/except Exception: return jsonify({"erro": str(e)}), 500` repetido em toda função de controller.

**Depois:**
```python
# middlewares/error_handler.py
@app.errorhandler(Exception)
def handle_error(e):
    app.logger.exception("Erro não tratado")
    code = getattr(e, "code", 500)
    return jsonify({"erro": str(e)}), code
```
Controllers deixam exceções de negócio subirem (ou lançam exceções tipadas específicas) em vez de capturar tudo localmente.

## 12. Atualizar uso de API deprecated
`[Uso de API/biblioteca deprecated]`

**Antes (Flask-SQLAlchemy legado):**
```python
user = User.query.get(user_id)
```

**Depois:**
```python
user = db.session.get(User, user_id)
```

**Antes (Node, driver 100% callback):**
```js
db.get("SELECT ...", [id], (err, row) => { ... });
```

**Depois (wrapper com Promise, remove o callback hell junto):**
```js
const row = await dbGetAsync("SELECT ...", [id]);
```

---

Ao aplicar qualquer padrão acima, mantenha o comportamento observável do endpoint (mesma rota, mesmo formato de resposta) — a Fase 3 refatora estrutura interna, não a API pública, a menos que o finding da Fase 2 tenha identificado explicitamente um contrato quebrado (ex.: endpoint que nunca deveria ter existido, como o item 4).
