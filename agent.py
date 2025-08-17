from src.flightSearcher import FlightEngine, FlightSelection
from src.flight import Flight
from datetime import date, datetime
import random
from src.ga.plan import *
import src.ga.ga_engine as ga_engine
from src.ai_agent.llm import LLM
import src.ai_agent.prompt as prompt
from src.visual import plotBestInviduals
import boto3
from dotenv import load_dotenv
import os
from datetime import datetime

def buildPlan(plan_json):
    """
    plan json is the output of the Agent which parametrizes the user' query
    into Traveller and TravelPlan
    """
    travellers_json = plan_json["listTravellers"]
    travellers = []

    for traveller_json in travellers_json:
        travellers.append(Traveller.model_validate(traveller_json))

    travel_json = plan_json["travelPlan"]
    travel_plan = TravelPlan(
        fromDate=datetime.strptime(travel_json["fromDate"], "%Y-%m-%d").date(),
        toDate=datetime.strptime(travel_json["toDate"], "%Y-%m-%d").date(),
        vetoCities=travel_json.get("vetoCities"),
        preferredCities=travel_json.get("preferredCities"),
        priceMax=travel_json.get("priceMax"),
        days=travel_json.get("days"),
        allowStayover=travel_json.get("allowStayover"),
        availableDestinations=travel_json.get("availableDestinations")
    )
    
    return Plan(
        listTravellers=travellers,
        travelPlan=travel_plan
    )

def configureLLM():
    load_dotenv()
    
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
    return llm

def main():
    random.seed(50)
    DB = "flightsAPI"
    flightEngine = FlightEngine(DB)

    llm = configureLLM()

    while True:
        query = input("Talk with the agency: ")
        if query.lower() in {"exit", "quit"}:
            break
        try:
            if query:
                explanation = llm.generateTrip(
                    prompt.tripBuilder.system,
                    prompt.tripBuilder.user + query
                )

                if isinstance(explanation, dict):
                    if "missingInformation" not in explanation.keys():
                        planCreated = buildPlan(explanation)
                        print("\n Information provided successfully. Creating the best trip plan within your request!")
                        break
                    else:
                        explanation = explanation.get("missingInformation")
                print("-"*50)
                print(f"\n {explanation} \n")

        except Exception as e:
            print(f"Error: {e}")

    gaEngine = ga_engine.GeneticAlgorithm(
        travellersTemplate=planCreated.listTravellers,
        travelPlan=planCreated.travelPlan,
        flightEngine=flightEngine
    )

    bestIndividualsScore, bestIndividual = gaEngine.run()

    plotBestInviduals(bestIndividualsScore)
    print(bestIndividual)

    print(f"\nChosen destination: {bestIndividual.chosenDestination}\n")
    for i, traveller in enumerate(bestIndividual.travellers):
        print(f"Traveller {i+1}:")
        print(f"  Origin: {traveller.origin}")
        print(f"  Budget: €{traveller.budget:.2f}")
        if traveller.selectedRoute:
            to = traveller.selectedRoute.flightToGo
            back = traveller.selectedRoute.flightBack
            print("  Outbound Flight:")
            print(f"    {to.from_city} → {to.to_city}")
            print(f"    Date: {to.departure_date} | Departure: {to.departure_time_local.time()} | Arrival: {to.arrival_time_local.time()}")
            print(f"    Price: €{to.price_eur:.2f} | Stayovers: {to.stayovers} | Flight: {to.flight_number} | Duration: {to.duration_hours}h")
            print("  Return Flight:")
            print(f"    {back.from_city} → {back.to_city}")
            print(f"    Date: {back.departure_date} | Departure: {back.departure_time_local.time()} | Arrival: {back.arrival_time_local.time()}")
            print(f"    Price: €{back.price_eur:.2f} | Stayovers: {back.stayovers} | Flight: {back.flight_number} | Duration: {back.duration_hours}h")
            print(f"  Total Route Cost: €{traveller.selectedRoute.cost:.2f}\n")
if __name__ == '__main__':
    main()
