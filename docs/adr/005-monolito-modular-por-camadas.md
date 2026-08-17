# ADR-005 — Monólito modular por camadas

**Status:** aceito
**Data:** 2026-08-17

## Contexto

O primeiro produto possui uma API, uma tela fixa e processos administrativos,
mas ainda não justifica operação distribuída.

## Decisão

O serviço é um monólito modular: `dominio` contém regras puras, `aplicacao`
orquestra casos de uso, `infraestrutura` implementa persistência e `api` adapta HTTP.

## Consequências

Mantemos implantação simples e fronteiras claras. Integrações futuras entram por
adaptadores, sem mover regras de negócio para FastAPI ou PostgreSQL.
