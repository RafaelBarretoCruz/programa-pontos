# Programa de Pontos

Sistema de fidelidade da rede varejista. Substitui a planilha mantida
manualmente pelo time de Marketing.

## Como rodar

1. Crie um banco PostgreSQL e aplique `migrations/001_inicial.sql`.
2. Instale dependências: `python -m pip install -r requirements.txt`.
3. Defina `DATABASE_URL=postgresql://usuario:senha@localhost/programa_pontos`.
4. Execute `uvicorn pontos.main:app --reload`.

Para a validação de regras puras, execute `pytest`. Os testes não requerem banco.

## Onde está o quê

| caminho | o quê |
|---------|-------|
| `docs/PRD.md` | o que o negócio pediu |
| `docs/adr/` | decisões de arquitetura e o porquê de cada uma |
| `AGENTS.md` | como se trabalha neste repositório |
| `static/index.html` | tela de consulta do atendente (contrato fixo) |
| `migrations/` | migrações SQL do PostgreSQL |
| `docs/plan.md` | etapas e validações da implementação |
