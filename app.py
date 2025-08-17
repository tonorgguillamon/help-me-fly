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
            if "missingInformation" in responseAgent.keys():
                await websocket.send_text(responseAgent["missingInformation"])
            else:
                planCreated = buildPlan(responseAgent)

                gaEngine = GeneticAlgorithm(
                    travellersTemplate=planCreated.listTravellers,
                    travelPlan=planCreated.travelPlan,
                    flightEngine=flightEngine
                )
                async for updateProgress in run_ga_generator(gaEngine):
                    await websocket.send_text(updateProgress)
                    if "This is my suggested trip plan:" in updateProgress:
                        await websocket.send_text("[DONE]")
        else:
            await websocket.send_text(responseAgent)
        
        await websocket.close()
        return

    except WebSocketDisconnect:
        print("Client disconnected")
