from src.flightSearcher import FlightEngine, FlightSelection
from src.flight import Flight
from datetime import date, datetime
import random
from src.ga.plan import *
import src.ga.ga_engine as ga_engine
from src.ai_agent.llm import LLM
import src.ai_agent.prompt as prompt
import boto3
from dotenv import load_dotenv
import os

def main():
    random.seed(50)
    DB = "flightsAPI"
    flightEngine = FlightEngine(DB)

    load_dotenv()
    
    #print([Flight.model_validate(flight) for flight in flightEngine.retrieveAllFlights()])

    #trip = FlightSelection(
    #    startDate=datetime(2025, 11, 1),
    #    endDate=datetime(2025, 11, 15),
    #    priceMax=200,
    #    startCity="Malaga",
    #    stayoversAllowed=False
    #)

    #print([Flight.model_validate(flight) for flight in flightEngine.retrieveFlights(trip)])

    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
        )

    llm = LLM(
        endpoint_id="eu.anthropic.claude-3-7-sonnet-20250219-v1:0",
        boto3_session=session,
        region=os.getenv("AWS_REGION"),
        version="bedrock-2023-05-31"
    )

    while True:
        query = input("Talk with the agency: ")
        if query.lower() in {"exit", "quit"}:
            break
        try:
            if query:
                explanation = llm.invoke(
                    prompt.tripBuilder.system,
                    prompt.tripBuilder.user + query
                )
                print("-"*50)
                print(f"\n [AGENT]: \n {explanation} \n")
                       
        except Exception as e:
            print(f"Error: {e}")

    travellerA = Traveller(
    origin="Malaga",
    budget=300
    )

    travellerB = Traveller(
        origin="Madrid",
        budget=320
    )

    travellerC = Traveller(
        origin="Munich",
        budget=250
    )

    travellersTemplate = [
        travellerA,
        travellerB,
        travellerC
    ]

    travelPlan = TravelPlan(
        flightEngine=flightEngine,
        fromDate=date(2025, 9, 20),
        toDate=date(2025, 12, 15),
        priceMax=300,
        days=10,
        availableDestinations=[
            "London", "Paris", "Rotterdam", "Berlin"
        ],
    )

    gaEngine = ga_engine.GeneticAlgorithm(
        travellersTemplate=travellersTemplate,
        travelPlan=travelPlan,
    )

    gaEngine.run()

if __name__ == '__main__':
    main()
