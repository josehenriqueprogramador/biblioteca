from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Configuração de templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Opcional: Rota de API caso queira processar relatórios no servidor
class Obra(BaseModel):
    isbn: str
    titulo: str
    autor: str
    status: str

@app.post("/processar-relatorio")
async def processar(obras: List[Obra]):
    # Exemplo de lógica: ordenar no servidor e devolver
    return sorted(obras, key=lambda x: x.titulo)

if __name__ == "__main__":
    import uvicorn
#    uvicorn.run(app, host="127.0.0.1", port=8000)
