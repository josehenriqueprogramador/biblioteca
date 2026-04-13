import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Ajuste aqui: Usamos o caminho relativo simples para o Render
templates = Jinja2Templates(directory="templates")

# --- MODELOS DE DADOS ---
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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # O arquivo index.html DEVE estar dentro da pasta /templates
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/relatorio")
async def gerar_relatorio(obras: List[Obra]):
    return sorted(obras, key=lambda x: x.titulo)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
