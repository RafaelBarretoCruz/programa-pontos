from datetime import date
from decimal import Decimal
from pontos.dominio.modelos import Campanha, Lancamento, Lote, Produto


class RepositorioEmMemoria:
    def __init__(self):
        self._campanhas: list[Campanha] = []
        self._lotes: list[Lote] = []
        self._lancamentos: list[Lancamento] = []
        self._produtos: list[Produto] = []
        self._compras: set[str] = set()
        self._resgates: set[str] = set()
        self._estornos: set[str] = set()

    def campanhas(self): return list(self._campanhas)
    def salvar_campanha(self, campanha): self._campanhas.append(campanha)
    def compra_existe(self, compra_id): return compra_id in self._compras
    def salvar_compra(self, lote: Lote, valor: Decimal, multiplicador: int):
        self._compras.add(lote.compra_id); self._lotes.append(lote)
        self._lancamentos.append(Lancamento(f"acumulo-{lote.compra_id}", lote.cliente_id, "acumulo", lote.pontos, lote.compra_em, lote.compra_id, lote.compra_id))
    def lotes_do_cliente(self, cliente_id): return [l for l in self._lotes if l.cliente_id == cliente_id]
    def lancamentos_do_cliente(self, cliente_id): return [l for l in self._lancamentos if l.cliente_id == cliente_id]
    def salvar_lancamentos(self, lancamentos): self._lancamentos.extend(lancamentos); self._estornos.update(l.referencia_id for l in lancamentos if l.tipo == "estorno" and l.referencia_id)
    def produto_em(self, produto_id, em: date):
        candidatos = [p for p in self._produtos if p.id == produto_id and p.efetivo_em <= em]
        return max(candidatos, key=lambda p: p.efetivo_em, default=None)
    def salvar_produto(self, produto): self._produtos.append(produto)
    def resgate_existe(self, resgate_id): return resgate_id in self._resgates
    def salvar_resgate(self, resgate_id, cliente_id, produto_id, custo_pontos, em, lancamentos): self._resgates.add(resgate_id); self._lancamentos.extend(lancamentos)
    def estorno_existe(self, estorno_id): return estorno_id in self._estornos
    def clientes(self): return sorted({l.cliente_id for l in self._lotes})
