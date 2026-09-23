# Template do Relatório de Auditoria

Usado no fim da **Fase 2**. Preencha exatamente esta estrutura — o texto entre `<>` é o único ponto de variação.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome da pasta do projeto>
Stack:   <linguagem + framework>
Files:   <N> analyzed | ~<N> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [<SEVERIDADE>] <Nome do anti-pattern>
File: <arquivo>:<linha ou intervalo de linhas>
Description: <o que está errado, em 1-2 frases objetivas>
Impact: <consequência concreta — não genérica>
Recommendation: <ação de refatoração, referenciando o padrão do playbook>

### [<SEVERIDADE>] <próximo finding...>
...

================================
Total: <N> findings
================================
```

## Regras de preenchimento

1. **Ordene os findings por severidade** (CRITICAL → HIGH → MEDIUM → LOW); dentro da mesma severidade, ordene pela ordem em que o arquivo aparece na árvore do projeto.
2. **`File:` deve ter arquivo e linha exatos** — nunca "vários lugares" sem listar onde; se o mesmo anti-pattern aparece em múltiplos locais, liste todos os locais separados por vírgula na mesma entrada.
3. **`Description` é sobre o código**, `Impact` é sobre a consequência (segurança, manutenção, performance) — não repita a mesma frase nos dois campos.
4. **`Recommendation` deve ser acionável**, citando o padrão de transformação correspondente do playbook de refatoração (ex.: "Extrair para camada de Service, ver Playbook #5").
5. Inclua pelo menos um finding de **API deprecated** quando aplicável ao stack detectado (ver catálogo item 13); se não houver nenhum uso de API obsoleta identificável, omita silenciosamente — não invente um finding falso só para preencher a categoria.
6. **Nunca modifique nenhum arquivo antes deste relatório ser exibido por completo.**

## Ponto de parada obrigatório

Depois de imprimir o relatório completo, pare e pergunte literalmente:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

- Só avance para a Fase 3 se a resposta for afirmativa (`y`, `yes`, `sim`, ou equivalente claro).
- Se a resposta for negativa ou ambígua, **não** altere nenhum arquivo — apenas confirme que a Fase 3 foi cancelada e ofereça ajustar o relatório se o usuário pedir.
- Nunca pule esta pergunta, mesmo que o relatório tenha poucos findings ou o projeto pareça "simples".
