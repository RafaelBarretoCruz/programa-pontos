from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pontos.aplicacao.servico import RegraDeNegocioError, ServicoPontos
from pontos.infraestrutura.memoria import RepositorioEmMemoria


class CompraEntrada(BaseModel):
    cliente_id: int = Field(gt=0)
    valor: Decimal = Field(ge=0)
    data: date
    compra_id: str | None = None


class CampanhaEntrada(BaseModel):
    inicia_em: date
    termina_em: date
    multiplicador: int


class ProdutoEntrada(BaseModel):
    produto_id: str
    nome: str
    custo_pontos: int
    efetivo_em: date


class ResgateEntrada(BaseModel):
    resgate_id: str
    cliente_id: int = Field(gt=0)
    produto_id: str
    data: date


class EstornoEntrada(BaseModel):
    estorno_id: str
    cliente_id: int = Field(gt=0)
    pontos: int = Field(gt=0)
    data: date


def criar_app(repositorio=None) -> FastAPI:
    repositorio = repositorio or RepositorioEmMemoria()
    servico = ServicoPontos(repositorio)
    app = FastAPI(title="Programa de Pontos")

    def executar(operacao):
        try:
            return operacao()
        except RegraDeNegocioError as erro:
            raise HTTPException(status_code=422, detail=str(erro)) from erro

    @app.get("/clientes/{cliente_id}/saldo")
    def consultar_saldo(cliente_id: int, em: date):
        saldo = servico.saldo(cliente_id, em)
        return {
            "saldo": saldo.disponivel,
            "expirado": saldo.expirado,
            "expira_em_30_dias": saldo.expira_em_30_dias,
            "lotes": [{"compra_em": l.lote.compra_em, "pontos": l.restante, "expira_em": l.lote.expira_em, "status": l.status} for l in saldo.lotes],
        }

    @app.post("/compras", status_code=201)
    def registrar_compra(entrada: CompraEntrada):
        compra_id = entrada.compra_id or f"tela-{uuid4()}"
        criado = executar(lambda: servico.registrar_compra(compra_id, entrada.cliente_id, entrada.valor, entrada.data))
        return {"compra_id": compra_id, "criada": criado}

    @app.post("/campanhas", status_code=201)
    def criar_campanha(entrada: CampanhaEntrada):
        campanha = executar(lambda: servico.criar_campanha(entrada.inicia_em, entrada.termina_em, entrada.multiplicador))
        return {"id": campanha.id, "inicia_em": campanha.inicia_em, "termina_em": campanha.termina_em, "multiplicador": campanha.multiplicador}

    @app.post("/catalogo/produtos", status_code=201)
    def criar_preco_de_produto(entrada: ProdutoEntrada):
        produto = executar(lambda: servico.cadastrar_produto(entrada.produto_id, entrada.nome, entrada.custo_pontos, entrada.efetivo_em))
        return {"produto_id": produto.id, "custo_pontos": produto.custo_pontos, "efetivo_em": produto.efetivo_em}

    @app.post("/resgates", status_code=201)
    def resgatar(entrada: ResgateEntrada):
        lancamentos = executar(lambda: servico.resgatar(entrada.resgate_id, entrada.cliente_id, entrada.produto_id, entrada.data))
        return {"resgate_id": entrada.resgate_id, "lancamentos": len(lancamentos)}

    @app.post("/compras/{compra_id}/estornos", status_code=201)
    def estornar(compra_id: str, entrada: EstornoEntrada):
        criado = executar(lambda: servico.estornar(entrada.estorno_id, compra_id, entrada.cliente_id, entrada.pontos, entrada.data))
        return {"estorno_id": entrada.estorno_id, "criado": criado}

    @app.get("/clientes/{cliente_id}/extrato")
    def extrato(cliente_id: int):
        return [{"id": l.id, "tipo": l.tipo, "pontos": l.pontos, "efetivado_em": l.efetivado_em, "compra_id": l.lote_compra_id, "referencia_id": l.referencia_id} for l in repositorio.lancamentos_do_cliente(cliente_id)]

    @app.get("/financeiro/passivo")
    def passivo(em: date):
        return {"em": em, "pontos_disponiveis": servico.passivo(em)}

    static = Path(__file__).resolve().parents[3] / "static" / "index.html"
    @app.get("/", include_in_schema=False)
    def tela_atendente():
        return FileResponse(static)
    return app
