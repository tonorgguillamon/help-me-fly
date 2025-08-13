from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

history = []

@app.get("/")
async def getUI(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "history": history})

@app.post("/", response_class=HTMLResponse)
async def talk(request: Request, userQuery: str = Form(...)):
    # here agent invokation
    history.append(
        {
            "query": userQuery,
            "response": ""
        }
    )
    return templates.TemplateResponse("index.html", {"request": request, "history": history})
