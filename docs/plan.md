# Plano de implementação — Programa de Pontos

## Etapa 1 — Fundação

- ADRs 004 e 005, estrutura em camadas, FastAPI, PostgreSQL e migrações SQL.
- **Validação:** `pytest` e inicialização da aplicação.

## Etapa 2 — Acúmulo e saldo

- Compras idempotentes, pontos inteiros arredondados para baixo, lotes e saldo histórico.
- **Validação:** testes de emissão, duplicidade, expiração e contrato da tela.

## Etapa 3 — Campanhas e resgates

- Campanhas, catálogo versionado e resgates por vencimento mais próximo.
- **Validação:** testes de sobreposição, preço fixado e saldo insuficiente.

## Etapa 4 — Estorno e fechamento

- Estornos imutáveis, extrato e passivo por data.
- **Validação:** testes de saldo negativo, reconstrução e passivo auditável.

## Etapa 5 — Entrega

- Índices, documentação e validação da integração com a tela fixa.
- **Validação:** `pytest` completo e conferência dos ADRs.
