# ADR-004 — PostgreSQL como persistência

**Status:** aceito
**Data:** 2026-08-17

## Contexto

O sistema recebe cerca de 25 mil compras por dia, precisa atender PDVs de forma
concorrente e manter um histórico auditável de lançamentos.

## Decisão

Usaremos PostgreSQL como banco transacional. O adaptador usa SQL direto, sem ORM,
e aplica migrações SQL versionadas.

## Consequências

O banco fornece transações, índices e restrições para idempotência e imutabilidade.
O ambiente de desenvolvimento e produção passa a exigir uma instância PostgreSQL.
