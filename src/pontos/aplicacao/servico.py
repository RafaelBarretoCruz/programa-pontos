from datetime import date
from decimal import Decimal
from uuid import uuid4
from pontos.dominio.ledger import calcular_saldo, expira_em, lotes_resgataveis, pontos_da_compra
from pontos.dominio.modelos import Campanha, Lancamento, Lote, Produto
from .portas import RepositorioPontos


class RegraDeNegocioError(ValueError):
    pass


class ServicoPontos:
    def __init__(self, repositorio: RepositorioPontos):
        self.repositorio = repositorio

    def registrar_compra(self, compra_id: str, cliente_id: int, valor: Decimal, em: date) -> bool:
        if self.repositorio.compra_existe(compra_id):
            return False
        campanhas = self.repositorio.campanhas()
        pontos = pontos_da_compra(valor, campanhas, em)
        multiplicador = max((c.multiplicador for c in campanhas if c.vigente_em(em)), default=1)
        lote = Lote(compra_id, cliente_id, pontos, em, expira_em(em))
        self.repositorio.salvar_compra(lote, valor, multiplicador)
        return True

    def saldo(self, cliente_id: int, em: date):
        return calcular_saldo(self.repositorio.lotes_do_cliente(cliente_id), self.repositorio.lancamentos_do_cliente(cliente_id), em)

    def criar_campanha(self, inicia_em: date, termina_em: date, multiplicador: int) -> Campanha:
        if termina_em < inicia_em or multiplicador < 2:
            raise RegraDeNegocioError("campanha inválida")
        campanha = Campanha(str(uuid4()), inicia_em, termina_em, multiplicador)
        self.repositorio.salvar_campanha(campanha)
        return campanha

    def cadastrar_produto(self, produto_id: str, nome: str, custo_pontos: int, em: date) -> Produto:
        if not nome or custo_pontos <= 0:
            raise RegraDeNegocioError("produto inválido")
        produto = Produto(produto_id, nome, custo_pontos, em)
        self.repositorio.salvar_produto(produto)
        return produto

    def resgatar(self, resgate_id: str, cliente_id: int, produto_id: str, em: date) -> list[Lancamento]:
        if self.repositorio.resgate_existe(resgate_id):
            return []
        produto = self.repositorio.produto_em(produto_id, em)
        if produto is None:
            raise RegraDeNegocioError("produto indisponível")
        saldo = self.saldo(cliente_id, em)
        if saldo.disponivel < produto.custo_pontos:
            raise RegraDeNegocioError("saldo insuficiente")
        faltam = produto.custo_pontos
        debitos: list[Lancamento] = []
        for lote_saldo in lotes_resgataveis(saldo):
            usados = min(faltam, lote_saldo.restante)
            debitos.append(Lancamento(str(uuid4()), cliente_id, "resgate", -usados, em, lote_saldo.lote.compra_id, resgate_id))
            faltam -= usados
            if not faltam:
                break
        self.repositorio.salvar_resgate(resgate_id, cliente_id, produto_id, produto.custo_pontos, em, debitos)
        return debitos

    def estornar(self, estorno_id: str, compra_id: str, cliente_id: int, pontos: int, em: date) -> bool:
        if pontos <= 0:
            raise RegraDeNegocioError("pontos do estorno devem ser positivos")
        if self.repositorio.estorno_existe(estorno_id):
            return False
        lote = next((l for l in self.repositorio.lotes_do_cliente(cliente_id) if l.compra_id == compra_id), None)
        if lote is None or pontos > lote.pontos:
            raise RegraDeNegocioError("compra ou valor de estorno inválido")
        self.repositorio.salvar_lancamentos([Lancamento(str(uuid4()), cliente_id, "estorno", -pontos, em, compra_id, estorno_id)])
        return True

    def passivo(self, em: date) -> int:
        # Repositórios de produção podem fornecer esta consulta por índice; a regra permanece idêntica.
        clientes = getattr(self.repositorio, "clientes", lambda: [])()
        return sum(sum(max(l.restante, 0) for l in self.saldo(cliente, em).lotes if l.status != "expirado") for cliente in clientes)
