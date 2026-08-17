# ADR-001 — Domínio isolado de infraestrutura

**Status:** aceito
**Data:** 2026-08-14

## Contexto

O PRD exige que o saldo seja consultado no PDV (rápido), que o
Financeiro reconstrua o passivo em datas passadas e que disputas de
cliente sejam auditáveis meses depois. São três consumidores diferentes
da mesma regra de negócio. Além disso, a primeira interface será uma
tela web, mas a operação de fechamento contábil provavelmente será um
processo em lote.

## Decisão

A regra de negócio fica em `src/pontos/dominio/` e não importa banco,
framework web ou I/O. O acesso a dados entra por um adaptador injetado.

## Alternativas consideradas

**Regra de negócio acessando SQLite diretamente.** Menos camadas, menos
arquivos, e para um sistema deste tamanho a abstração pode nunca se
pagar. É a escolha certa se o sistema tiver um único consumidor e vida
curta — não é o caso aqui, porque já sabemos de três.

## Consequências

- Testes de regra de negócio rodam sem banco, em milissegundos.
- Adicionar uma segunda interface não toca uma linha de domínio.
- Pagamos: mais arquivos, uma camada de tradução a mais, e a
  tentação constante de "furar" a fronteira quando der pressa.
- Toda consulta de saldo passa por agregação — se o PDV ficar lento,
  a solução é cache no adaptador, nunca desnormalizar o domínio.