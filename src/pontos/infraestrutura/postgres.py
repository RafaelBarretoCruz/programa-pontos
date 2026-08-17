from datetime import date
from decimal import Decimal
from uuid import uuid4
from pontos.dominio.modelos import Campanha, Lancamento, Lote, Produto


class RepositorioPostgres:
    """Adaptador PostgreSQL de SQL direto; o domínio não depende deste módulo."""
    def __init__(self, database_url: str):
        import psycopg
        self._conexao = psycopg.connect(database_url)

    def campanhas(self):
        with self._conexao.cursor() as cur:
            cur.execute("SELECT id::text, inicia_em, termina_em, multiplicador FROM campanhas")
            return [Campanha(*linha) for linha in cur.fetchall()]

    def salvar_campanha(self, c):
        self._executar("INSERT INTO campanhas (id, inicia_em, termina_em, multiplicador) VALUES (%s, %s, %s, %s)", (c.id, c.inicia_em, c.termina_em, c.multiplicador))

    def compra_existe(self, compra_id): return self._existe("SELECT 1 FROM compras WHERE id = %s", (compra_id,))

    def salvar_compra(self, lote: Lote, valor: Decimal, multiplicador: int):
        with self._conexao.transaction(), self._conexao.cursor() as cur:
            cur.execute("INSERT INTO compras (id, cliente_id, valor, compra_em, pontos, multiplicador) VALUES (%s,%s,%s,%s,%s,%s)", (lote.compra_id, lote.cliente_id, valor, lote.compra_em, lote.pontos, multiplicador))
            cur.execute("INSERT INTO lotes (compra_id, cliente_id, pontos, compra_em, expira_em) VALUES (%s,%s,%s,%s,%s)", (lote.compra_id, lote.cliente_id, lote.pontos, lote.compra_em, lote.expira_em))
            cur.execute("INSERT INTO lancamentos (id, cliente_id, tipo, pontos, efetivado_em, lote_compra_id, referencia_id) VALUES (%s,%s,'acumulo',%s,%s,%s,%s)", (uuid4(), lote.cliente_id, lote.pontos, lote.compra_em, lote.compra_id, lote.compra_id))

    def lotes_do_cliente(self, cliente_id):
        with self._conexao.cursor() as cur:
            cur.execute("SELECT compra_id, cliente_id, pontos, compra_em, expira_em FROM lotes WHERE cliente_id = %s", (cliente_id,))
            return [Lote(*linha) for linha in cur.fetchall()]

    def lancamentos_do_cliente(self, cliente_id):
        with self._conexao.cursor() as cur:
            cur.execute("SELECT id::text, cliente_id, tipo, pontos, efetivado_em, lote_compra_id, referencia_id FROM lancamentos WHERE cliente_id = %s", (cliente_id,))
            return [Lancamento(*linha) for linha in cur.fetchall()]

    def salvar_lancamentos(self, lancamentos):
        with self._conexao.transaction(), self._conexao.cursor() as cur:
            cur.executemany("INSERT INTO lancamentos (id, cliente_id, tipo, pontos, efetivado_em, lote_compra_id, referencia_id) VALUES (%s::uuid,%s,%s,%s,%s,%s,%s)", [(l.id, l.cliente_id, l.tipo, l.pontos, l.efetivado_em, l.lote_compra_id, l.referencia_id) for l in lancamentos])

    def produto_em(self, produto_id, em: date):
        with self._conexao.cursor() as cur:
            cur.execute("SELECT produto_id, nome, custo_pontos, efetivo_em FROM precos_catalogo WHERE produto_id=%s AND efetivo_em<=%s ORDER BY efetivo_em DESC LIMIT 1", (produto_id, em))
            linha = cur.fetchone()
            return Produto(*linha) if linha else None

    def salvar_produto(self, p):
        self._executar("INSERT INTO precos_catalogo (produto_id, nome, custo_pontos, efetivo_em) VALUES (%s,%s,%s,%s)", (p.id, p.nome, p.custo_pontos, p.efetivo_em))

    def resgate_existe(self, resgate_id): return self._existe("SELECT 1 FROM resgates WHERE id = %s", (resgate_id,))
    def salvar_resgate(self, resgate_id, cliente_id, produto_id, custo_pontos, em, lancamentos):
        with self._conexao.transaction(), self._conexao.cursor() as cur:
            cur.execute("INSERT INTO resgates (id, cliente_id, produto_id, custo_pontos, resgatado_em) VALUES (%s,%s,%s,%s,%s)", (resgate_id, cliente_id, produto_id, custo_pontos, em))
            cur.executemany("INSERT INTO lancamentos (id, cliente_id, tipo, pontos, efetivado_em, lote_compra_id, referencia_id) VALUES (%s::uuid,%s,%s,%s,%s,%s,%s)", [(l.id, l.cliente_id, l.tipo, l.pontos, l.efetivado_em, l.lote_compra_id, l.referencia_id) for l in lancamentos])
    def estorno_existe(self, estorno_id): return self._existe("SELECT 1 FROM lancamentos WHERE referencia_id=%s AND tipo='estorno'", (estorno_id,))
    def clientes(self):
        with self._conexao.cursor() as cur:
            cur.execute("SELECT DISTINCT cliente_id FROM lotes")
            return [x[0] for x in cur.fetchall()]
    def _existe(self, sql, parametros):
        with self._conexao.cursor() as cur:
            cur.execute(sql, parametros)
            return cur.fetchone() is not None
    def _executar(self, sql, parametros):
        with self._conexao.transaction(), self._conexao.cursor() as cur: cur.execute(sql, parametros)
