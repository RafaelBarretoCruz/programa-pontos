# ADR-002 — Pontos como lançamentos imutáveis

**Status:** aceito
**Data:** 2026-08-14

## Contexto

O PRD impõe quatro restrições que um saldo agregado não atende:
pontos expiram 12 meses após a compra que os originou — ou seja, a
expiração é por lote, não pelo total; o estorno desfaz os pontos de
uma compra específica; o atendente precisa explicar ao cliente como o
saldo foi formado; e o Financeiro precisa do passivo em uma data
passada, auditável meses depois.

## Decisão

Pontos são registrados como lançamentos imutáveis, cada um com data de
origem e valor. Não existe campo de saldo no cliente. O saldo é sempre
calculado a partir dos lançamentos, para uma data de referência.

## Alternativas consideradas

**Campo de saldo no cliente, atualizado a cada operação.** Leitura
instantânea, sem agregação — e o PRD exige consulta rápida no PDV, com
o cliente esperando no caixa. É a escolha certa quando o saldo é apenas
um número corrente. Perde aqui porque não sabe qual parte do saldo
expira quando, e porque sobrescrever destrói exatamente a informação
que o fechamento contábil precisa reconstruir.

## Consequências

- Toda consulta de saldo passa a ser uma agregação. Se o PDV ficar
  lento, a resposta é cache no adaptador ou uma tabela derivada —
  nunca substituir os lançamentos pela soma.
- O extrato do atendente sai de graça: é a própria lista de lançamentos.
- Correção nunca altera lançamento: gera um lançamento novo de ajuste.
- Escrevemos mais código e ocupamos mais disco para responder a
  pergunta mais simples do sistema: "quanto o cliente tem?".