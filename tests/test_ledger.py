from datetime import date
from decimal import Decimal
import pytest
from pontos.dominio.ledger import calcular_saldo, expira_em, pontos_da_compra
from pontos.dominio.modelos import Campanha, Lancamento, Lote


def lote(pontos=100, compra_em=date(2025, 3, 12)):
    return Lote("c1", 42, pontos, compra_em, expira_em(compra_em))


def test_pontos_arredondam_para_baixo():
    assert pontos_da_compra(Decimal("10.99"), [], date(2025, 1, 1)) == 10


def test_campanha_aplica_maior_multiplicador_sobreposto():
    campanhas = [Campanha("a", date(2025, 1, 1), date(2025, 1, 31), 2), Campanha("b", date(2025, 1, 10), date(2025, 1, 20), 3)]
    assert pontos_da_compra(Decimal("10"), campanhas, date(2025, 1, 15)) == 30


def test_lote_expira_no_inicio_do_dia_de_aniversario():
    saldo = calcular_saldo([lote()], [], date(2026, 3, 12))
    assert saldo.disponivel == 0
    assert saldo.expirado == 100


def test_saldo_historico_ignora_debito_futuro():
    debito = Lancamento("d1", 42, "resgate", -30, date(2025, 4, 1), "c1", "r1")
    assert calcular_saldo([lote()], [debito], date(2025, 3, 20)).disponivel == 100


def test_estorno_depois_de_resgate_produz_saldo_negativo():
    lancamentos = [Lancamento("r", 42, "resgate", -100, date(2025, 4, 1), "c1", "r1"), Lancamento("e", 42, "estorno", -100, date(2025, 4, 2), "c1", "e1")]
    assert calcular_saldo([lote()], lancamentos, date(2025, 4, 2)).disponivel == -100
