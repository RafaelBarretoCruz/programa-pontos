from datetime import date
from decimal import Decimal
import pytest
from pontos.aplicacao.servico import RegraDeNegocioError, ServicoPontos
from pontos.infraestrutura.memoria import RepositorioEmMemoria


def servico(): return ServicoPontos(RepositorioEmMemoria())


def test_compra_com_mesmo_id_e_idempotente():
    s = servico()
    assert s.registrar_compra("v1", 1, Decimal("20"), date(2025, 1, 1)) is True
    assert s.registrar_compra("v1", 1, Decimal("20"), date(2025, 1, 1)) is False
    assert s.saldo(1, date(2025, 1, 2)).disponivel == 20


def test_compra_cria_lancamento_imutavel_de_acumulo():
    repositorio = RepositorioEmMemoria(); s = ServicoPontos(repositorio)
    s.registrar_compra("v1", 1, Decimal("20"), date(2025, 1, 1))
    assert repositorio.lancamentos_do_cliente(1)[0].tipo == "acumulo"


def test_resgate_consume_lote_com_vencimento_mais_proximo():
    s = servico()
    s.registrar_compra("novo", 1, Decimal("100"), date(2025, 2, 1))
    s.registrar_compra("velho", 1, Decimal("100"), date(2025, 1, 1))
    s.cadastrar_produto("p", "Caneca", 80, date(2025, 1, 1))
    lancamentos = s.resgatar("r1", 1, "p", date(2025, 2, 2))
    assert lancamentos[0].lote_compra_id == "velho"


def test_resgate_sem_saldo_e_rejeitado():
    s = servico(); s.cadastrar_produto("p", "Caneca", 1, date(2025, 1, 1))
    with pytest.raises(RegraDeNegocioError, match="saldo insuficiente"):
        s.resgatar("r1", 1, "p", date(2025, 1, 2))


def test_preco_do_resgate_nao_muda_ao_cadastrar_nova_versao():
    s = servico(); s.registrar_compra("v", 1, Decimal("100"), date(2025, 1, 1))
    s.cadastrar_produto("p", "Caneca", 30, date(2025, 1, 1)); s.resgatar("r1", 1, "p", date(2025, 1, 2))
    s.cadastrar_produto("p", "Caneca", 50, date(2025, 2, 1))
    assert s.saldo(1, date(2025, 2, 2)).disponivel == 70


def test_estorno_nao_pode_exceder_pontos_da_compra():
    s = servico(); s.registrar_compra("v", 1, Decimal("10"), date(2025, 1, 1))
    with pytest.raises(RegraDeNegocioError): s.estornar("e", "v", 1, 11, date(2025, 1, 2))


def test_passivo_exclui_pontos_expirados():
    s = servico(); s.registrar_compra("v", 1, Decimal("10"), date(2025, 1, 1))
    assert s.passivo(date(2026, 1, 1)) == 0
