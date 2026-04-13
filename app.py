import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Configuração robusta de caminhos para o Render
base_dir = os.path.dirname(os.path.realpath(__file__))
templates = Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# --- MODELOS DE DADOS (O que era struct no C++) ---
class Autor(BaseModel):
    id: int
    nome: str
    nacionalidade: str

class Obra(BaseModel):
    isbn: str
    titulo: str
    autor_id: int
    status: str = "LIVRE"

# --- ROTAS ---

# Rota Principal: Carrega a interface
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Rota de API: Exemplo de processamento (Caso queira filtrar no servidor)
@app.post("/relatorio")
async def gerar_relatorio(obras: List[Obra]):
    # Exemplo: Retorna obras ordenadas por título
    return sorted(obras, key=lambda x: x.titulo)

# Se rodar localmente pelo terminal
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
