from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Campanha:
    id: str
    inicia_em: date
    termina_em: date
    multiplicador: int

    def vigente_em(self, em: date) -> bool:
        return self.inicia_em <= em <= self.termina_em


@dataclass(frozen=True)
class Lote:
    compra_id: str
    cliente_id: int
    pontos: int
    compra_em: date
    expira_em: date


@dataclass(frozen=True)
class Lancamento:
    id: str
    cliente_id: int
    tipo: str
    pontos: int
    efetivado_em: date
    lote_compra_id: str | None = None
    referencia_id: str | None = None


@dataclass(frozen=True)
class Produto:
    id: str
    nome: str
    custo_pontos: int
    efetivo_em: date
