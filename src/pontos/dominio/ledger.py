from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_FLOOR
from .modelos import Campanha, Lancamento, Lote


def pontos_da_compra(valor: Decimal, campanhas: list[Campanha], em: date) -> int:
    if valor < 0:
        raise ValueError("valor da compra não pode ser negativo")
    multiplicador = max((c.multiplicador for c in campanhas if c.vigente_em(em)), default=1)
    return int(valor.to_integral_value(rounding=ROUND_FLOOR)) * multiplicador


def expira_em(compra_em: date) -> date:
    try:
        return compra_em.replace(year=compra_em.year + 1)
    except ValueError:  # 29 de fevereiro
        return compra_em.replace(year=compra_em.year + 1, month=2, day=28)


@dataclass(frozen=True)
class LoteSaldo:
    lote: Lote
    restante: int
    status: str


@dataclass(frozen=True)
class Saldo:
    disponivel: int
    expirado: int
    expira_em_30_dias: int
    lotes: list[LoteSaldo]


def calcular_saldo(lotes: list[Lote], lancamentos: list[Lancamento], em: date) -> Saldo:
    debitos_por_lote: dict[str, int] = {}
    for lancamento in lancamentos:
        if lancamento.efetivado_em <= em and lancamento.pontos < 0 and lancamento.lote_compra_id:
            debitos_por_lote[lancamento.lote_compra_id] = debitos_por_lote.get(lancamento.lote_compra_id, 0) + lancamento.pontos

    resultado: list[LoteSaldo] = []
    disponivel = expirado = vence_em_30 = 0
    limite = em + timedelta(days=30)
    for lote in sorted((l for l in lotes if l.compra_em <= em), key=lambda l: (l.expira_em, l.compra_id)):
        restante = lote.pontos + debitos_por_lote.get(lote.compra_id, 0)
        if em >= lote.expira_em:
            status = "expirado"
            expirado += max(restante, 0)
            disponivel += min(restante, 0)  # estornos após resgate permanecem como dívida
        elif lote.expira_em <= limite:
            status = "expirando"
            disponivel += restante
            vence_em_30 += max(restante, 0)
        else:
            status = "ativo"
            disponivel += restante
        resultado.append(LoteSaldo(lote=lote, restante=restante, status=status))
    return Saldo(disponivel, expirado, vence_em_30, resultado)


def lotes_resgataveis(saldo: Saldo) -> list[LoteSaldo]:
    return [l for l in saldo.lotes if l.status != "expirado" and l.restante > 0]
