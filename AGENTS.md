# Programa de Pontos

Sistema de fidelidade da rede. O documento de negócio está em docs/PRD.md.

## Processo

- Leia docs/PRD.md antes de implementar qualquer feature.
- Antes de implementar, liste os requisitos ambíguos que encontrar.
  Não decida por conta própria o que o PRD deixou em aberto — pergunte.
- Decisões estruturais (modelagem de dados, fronteiras de módulo,
  dependências externas) precisam de um ADR em docs/adr/ antes do código.
- Consulte docs/adr/README.md antes de propor mudanças estruturais.
- Não contrarie uma decisão registrada em ADR sem avisar explicitamente.
  Se você discorda de um ADR, diga por quê e espere — não refatore.

## Qualidade

- Toda regra de negócio tem teste.
- Mudanças pequenas e revisáveis. Uma tarefa por vez.

## Arquitetura

- Domínio em src/pontos/dominio/, sem import de banco, web ou I/O. (ADR-001)
- Pontos são lançamentos imutáveis. Não existe campo de saldo. (ADR-002)
- Correção nunca altera lançamento: gera lançamento novo. (ADR-002)
- Stack: Python, FastAPI, SQLite. Sem ORM.

## Onde olhar

- docs/PRD.md — o que o negócio quer
- docs/adr/ — por que decidimos assim