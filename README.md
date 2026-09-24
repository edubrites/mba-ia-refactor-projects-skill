# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

---

# Minha Solução

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