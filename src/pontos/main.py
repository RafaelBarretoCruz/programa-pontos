import os
from pontos.api import criar_app
from pontos.infraestrutura.postgres import RepositorioPostgres

url = os.environ.get("DATABASE_URL")
if not url:
    raise RuntimeError("DATABASE_URL deve apontar para PostgreSQL")
app = criar_app(RepositorioPostgres(url))
