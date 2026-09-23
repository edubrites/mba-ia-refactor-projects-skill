# Catálogo de Anti-patterns

Usado na **Fase 2**. Para cada arquivo-fonte relevante, cruze contra esta lista. Cada finding no relatório deve citar o anti-pattern pelo nome usado aqui, mais arquivo:linha exatos.

Regra geral de severidade (alinhada ao `README.md` raiz):
- **CRITICAL**: quebra segurança/dados ou é um God Class/God Method completo
- **HIGH**: viola MVC/SOLID fortemente, dificulta muito teste/manutenção
- **MEDIUM**: padronização, duplicação, performance moderada
- **LOW**: legibilidade, nomenclatura, magic numbers

## 1. God Class / God File — CRITICAL
**Sinal:** um único arquivo/classe concentra roteamento HTTP + acesso a banco + regra de negócio para 2+ domínios distintos; ou arquivo >150-200 linhas misturando essas responsabilidades.
**Por quê:** impossível testar em isolamento, qualquer mudança afeta tudo.

## 2. Credenciais / Segredos Hardcoded — CRITICAL
**Sinal:** literal de string atribuído a variável/campo com nome contendo `secret`, `key`, `password`, `pass`, `token`, `apikey`, ou connection string com usuário:senha embutidos no código-fonte (não em `.env`/variável de ambiente).
**Por quê:** qualquer pessoa com acesso ao repositório compromete produção.

## 3. SQL Injection (concatenação de string em query) — CRITICAL
**Sinal:** string de SQL construída com `+`, f-string, template literal ou `%` interpolando diretamente uma variável vinda de request/input do usuário, em vez de placeholder parametrizado (`?`, `%s`, `$1`, ORM query builder).
**Por quê:** permite manipulação arbitrária do banco por quem controla o input.

## 4. Execução de código/SQL arbitrário vindo do request — CRITICAL
**Sinal:** endpoint que recebe uma string do body/query e passa direto para `execute()`, `eval()`, `exec()`, `child_process.exec`, sem allowlist nem validação estrutural.
**Por quê:** é uma porta de takeover completo do processo/banco.

## 5. Criptografia fraca ou "caseira" — CRITICAL (senha) / HIGH (outros dados sensíveis)
**Sinal:** hash de senha feito com MD5/SHA1 sem salt, ou função de "hash" própria (concatenação/encoding disfarçado de criptografia, ex. só `base64`).
**Por quê:** senhas praticamente reversíveis; qualquer vazamento de banco expõe credenciais reais dos usuários.

## 6. Lógica de negócio pesada dentro do Controller/Route — HIGH
**Sinal:** handler de rota com múltiplos passos de regra de negócio, orquestração de side-effects (envio de e-mail/SMS/pagamento) ou cálculos de domínio, em vez de delegar a um Model/Service e só traduzir request↔response.
**Por quê:** impede reuso e testes unitários sem subir um servidor HTTP.

## 7. Acoplamento forte / sem Injeção de Dependência — HIGH
**Sinal:** uma classe/módulo instancia suas próprias dependências (`new Database()`, conexão global, singleton importado direto) em vez de recebê-las via construtor/parâmetro/factory.
**Por quê:** impossível trocar a dependência por um mock/fake em teste; mudança em uma classe se propaga em cascata.

## 8. Estado global mutável — HIGH
**Sinal:** variável/objeto no nível de módulo que é mutado por handlers de requisição e lido por outras requisições (cache manual, contador, flag).
**Por quê:** quebra isolamento entre requisições concorrentes; bugs difíceis de reproduzir.

## 9. Queries N+1 — MEDIUM
**Sinal:** dentro de um loop `for` sobre o resultado de uma query, é disparada uma nova query por iteração (para buscar relação/detalhe), em vez de `JOIN`, eager loading (`joinedload`, `include`), ou batch fetch com `WHERE id IN (...)`.
**Por quê:** tempo de resposta cresce linearmente (ou pior) com o volume de dados.

## 10. Validação ausente ou duplicada inconsistente — MEDIUM
**Sinal:** algumas rotas validam tipo/tamanho/obrigatoriedade de campos e outras não; ou a mesma validação é reescrita em `create` e `update` em vez de extraída para uma função/schema compartilhado.
**Por quê:** abre brechas de dado inválido e gera divergência quando a regra muda em só um lugar.

## 11. Duplicação de lógica de negócio (viola DRY) — MEDIUM
**Sinal:** o mesmo cálculo/condicional de domínio (ex.: "está atrasado?", "desconto aplicável") é copiado e colado em 3+ lugares em vez de centralizado em um Model/Service reutilizado.
**Por quê:** correção de regra exige lembrar de todos os lugares — alto risco de divergência silenciosa.

## 12. Configuração misturada com código — MEDIUM
**Sinal:** flags como `debug=True`, porta, caminho de banco, chaves de terceiros escritos inline no arquivo principal em vez de um módulo `config` central lendo de variáveis de ambiente.
**Por quê:** impede diferenciar ambiente dev/prod e é a porta de entrada para o item 2 (segredo hardcoded).

## 13. Uso de API/biblioteca deprecated — MEDIUM (avaliar impacto real caso a caso)
**Sinal — sempre verificar para o stack detectado na Fase 1:**
- Python: `hashlib.md5`/`sha1` para senha; `Model.query.get(id)` do Flask-SQLAlchemy (legado desde SQLAlchemy 1.4/2.0, prefira `db.session.get(Model, id)`); `datetime.utcnow()` (deprecated desde Python 3.12, prefira `datetime.now(timezone.utc)`).
- Node.js: driver `sqlite3` 100% callback-based quando existe alternativa com Promise/async nativo; `new Buffer()` (deprecated, use `Buffer.from`); middlewares/body-parsers antigos quando o framework já inclui um nativo.
- Geral: versão de dependência no manifesto com major desatualizado e changelog indicando API removida/substituída.
**Recomendação:** sempre citar o equivalente moderno explicitamente no finding (não basta dizer "está deprecated").

## 14. Exceção genérica engolindo erros — LOW
**Sinal:** `except:`/`except Exception:` (Python) ou `catch (e) {}` (JS) vazio ou só retornando erro genérico, sem log nem diferenciar tipos de falha.
**Por quê:** esconde a causa raiz de bugs reais, dificultando debug em produção.

## 15. Magic numbers/strings e nomenclatura ruim — LOW
**Sinal:** literais de status (`"PAID"`, `"pendente"`), thresholds numéricos ou nomes de variável de 1 letra (`u`, `e`, `p`) espalhados pelo código sem constante/enum nomeado.
**Por quê:** reduz legibilidade e facilita erro de digitação silencioso.

## 16. Condicional booleano redundante — LOW
**Sinal:** `if cond: return True else: return False` (ou equivalente) em vez de `return cond`.
**Por quê:** ruído puro, sem ganho de clareza ou performance.

---

**Mínimo por projeto:** ao aplicar este catálogo, espere encontrar pelo menos 5 findings, incluindo no mínimo 1 CRITICAL ou HIGH, 2 MEDIUM e 2 LOW — isso é o piso de aceite da skill, não o teto. Se o projeto já tiver alguma organização (ex.: pastas `models/routes/services`), ainda assim verifique os itens 6, 9, 10, 11 e 13: nome de pasta não é garantia de responsabilidade real.
