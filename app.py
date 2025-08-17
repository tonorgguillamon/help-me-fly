from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi import WebSocket, WebSocketDisconnect
import uvicorn
from agent import configureLLM, buildPlan
from src.flightSearcher import FlightEngine
import random
import src.ai_agent.prompt as prompt
import json
from src.ga.ga_engine import GeneticAlgorithm, run_ga_generator
import asyncio

app = FastAPI()
templates = Jinja2Templates(directory="templates")

random.seed(50)
DB = "flightsAPI"
flightEngine = FlightEngine(DB)

llm = configureLLM()

history = []

@app.get("/")
async def getUI(request: Request):
    print("Comes to get ui")
    return templates.TemplateResponse("index.html", {"request": request, "history": history})

@app.post("/", response_class=HTMLResponse)
async def talk(request: Request, userQuery: str = Form(...)):
    print("comes to post")
    responseAgent = llm.generateTrip(
        prompt.tripBuilder.system,
        prompt.tripBuilder.user + userQuery
    )

    print(responseAgent)

    if isinstance(responseAgent, dict):
        if "missingInformation" not in responseAgent.keys():
            history.append(
                {
                    "query": userQuery,
                    "response": "\n Information provided successfully. Creating the best trip plan within your request!"
                }
            )
            return templates.TemplateResponse("index.html", {
                "request": request,
                "history": history,
                "responseAgent": json.dumps(responseAgent)  # dict -> str due to HTML limitations. Pass to js
            })
        else:
            history.append(
                {
                    "query": userQuery,
                    "response": responseAgent.get("missingInformation")
                }
            )
            return templates.TemplateResponse("index.html", {"request": request, "history": history})
        
@app.websocket("/ws/plan-trip")
async def websocketPlanTrip(websocket: WebSocket):
    await websocket.accept() # handshake to accept the communication from client (html/js)

    try:
        # Receives data from client: agent response
        data = await websocket.receive_text()
        userQuery = json.loads(data).get("userQuery")

        responseAgent = llm.generateTrip(
            prompt.tripBuilder.system,
            prompt.tripBuilder.user + userQuery
        )
        if isinstance(responseAgent, dict):
            if "missingInformation" in responseAgent:
                await websocket.send_text(responseAgent["missingInformation"])
            else:
                planCreated = buildPlan(responseAgent)

                gaEngine = GeneticAlgorithm(
                    travellersTemplate=planCreated.listTravellers,
                    travelPlan=planCreated.travelPlan,
                    flightEngine=flightEngine
                )
                async for updateProgress in run_ga_generator(gaEngine):
                    if isinstance(updateProgress, str): # data to display
                        await websocket.send_text(updateProgress)
                    else:
                        await websocket.send_text("This is my suggested trip plan:\n")
                        await websocket.send_text(json.dumps(updateProgress, default=str)) # serialize object, which is best Individual, into string
                        await websocket.send_text("[DONE]")
        else:
            await websocket.send_text(responseAgent)

    except WebSocketDisconnect:
        print("Client disconnected")
