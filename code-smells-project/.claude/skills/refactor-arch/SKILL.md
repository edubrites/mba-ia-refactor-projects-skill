---
name: refactor-arch
description: Use when asked to audit or refactor a backend codebase to the MVC pattern, when the user runs /refactor-arch, or when a project shows architecture/security smells (God classes, hardcoded secrets, SQL built by string concatenation, business logic in routes) and needs a structured audit report before any file is changed. Technology-agnostic — works on any backend language/framework.
---

# refactor-arch

Audita e refatora qualquer projeto de backend para o padrão **MVC**, em 3 fases sequenciais. Funciona em qualquer linguagem/framework — a análise é sempre feita a partir do código real do projeto atual, nunca assumida.

Carregue os arquivos de `references/` sob demanda, um por fase (não carregue todos de uma vez):

- Fase 1 → `references/01-project-analysis.md`
- Fase 2 → `references/02-antipattern-catalog.md` e `references/03-report-template.md`
- Fase 3 → `references/04-architecture-guidelines.md` e `references/05-refactoring-playbook.md`

## Fase 1 — Análise

1. Leia `references/01-project-analysis.md` e aplique as heurísticas para detectar: linguagem, framework (+ versão), dependências relevantes, banco de dados/tabelas, domínio da aplicação, e classificação da arquitetura atual.
2. Conte os arquivos-fonte reais analisados (não conte `node_modules`, `venv`, migrations geradas, cache).
3. Imprima o resumo no formato fixo definido na referência.
4. Sem parar para confirmação, siga direto para a Fase 2.

## Fase 2 — Auditoria

1. Leia `references/02-antipattern-catalog.md`.
2. Percorra cada arquivo-fonte do projeto (não pule nenhum arquivo de código de aplicação) e cruze o conteúdo contra o catálogo. Para cada ocorrência, anote: anti-pattern, severidade, arquivo, linha(s) exata(s).
3. Verifique explicitamente o item "Uso de API/biblioteca deprecated" do catálogo para o stack detectado na Fase 1.
4. Leia `references/03-report-template.md` e gere o relatório de auditoria completo nesse formato exato, ordenado por severidade.
5. **Pare imediatamente após imprimir o relatório** e pergunte:
   ```
   Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
   ```
6. **Não leia nem edite nenhum arquivo de código com intenção de refatorar antes desta pergunta ser respondida afirmativamente.** Se a resposta for negativa, pare aqui — não há Fase 3 nesta execução.

## Fase 3 — Refatoração

Só execute esta fase após confirmação explícita do usuário na Fase 2.

1. Leia `references/04-architecture-guidelines.md` para decidir a estrutura de pastas alvo (adapte ao nível de organização já existente: projeto monolítico vs. parcialmente organizado — a referência explica a diferença de abordagem).
2. Leia `references/05-refactoring-playbook.md` e aplique o padrão de transformação correspondente a cada finding do relatório da Fase 2, na ordem de severidade (CRITICAL primeiro).
3. Preserve o comportamento observável de cada endpoint (mesma rota, mesmo formato de resposta), a menos que o próprio finding exija remover/alterar o contrato (ex.: endpoint de execução de SQL arbitrário).
4. Depois de mover o código, **valide que a aplicação continua funcionando**:
   - Identifique o comando de start real do projeto (script em `package.json`, `if __name__ == "__main__"` + `app.run(...)`, `Procfile`, README do projeto, etc.) — não assuma um comando genérico.
   - Suba a aplicação em background, aguarde o processo abrir a porta (com timeout razoável, ex. alguns segundos), e cheque o log/stdout por erro de boot.
   - Faça pelo menos uma requisição real (`curl`/equivalente) contra um endpoint de cada domínio afetado (idealmente reaproveitando exemplos de `api.http`/coleção de requests do projeto, se existir) e confira que a resposta é coerente (status code e formato esperados).
   - Encerre o processo de teste ao final.
   - Se o boot ou algum endpoint falhar, corrija antes de declarar a Fase 3 concluída — não reporte sucesso sem essa verificação.
5. Imprima o resumo final:
   ```
   ================================
   PHASE 3: REFACTORING COMPLETE
   ================================
   ## New Project Structure
   <árvore de diretórios resultante>

   ## Validation
     ✓/✗ Application boots without errors
     ✓/✗ All endpoints respond correctly
     ✓/✗ Zero anti-patterns remaining (ou lista o que ficou pendente e por quê)
   ================================
   ```

## Regras gerais (valem para as 3 fases)

- Nunca pule a pergunta de confirmação da Fase 2, mesmo em projetos pequenos ou "óbvios".
- Nunca assuma stack/domínio por nome de pasta — sempre confirme pelas heurísticas da Fase 1.
- Em projeto já parcialmente organizado (models/routes/services existentes), não recrie a árvore do zero: mova apenas o que está na camada errada, preservando nomes de arquivo/função quando possível.
- Se durante a Fase 3 você encontrar um anti-pattern novo não listado no relatório da Fase 2, corrija-o também, mas mencione explicitamente no resumo final que foi um achado adicional.