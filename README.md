# HELP ME FLY
## Introduction
Application which intends to ease the search of flights. With the break-out of LLM into quotodian usage, talking to an AI-Agent should be enough to find your perfect flight demand. No more drop-down menus, pop-up calendar, nor checkboxes. Just talk.
Addionally, employing metaheuristic techniques, the API can design the perfect flight-trip for multiple travelers departing from different cities (i.e. each of your friends lives in a different city and regardless you want to meet in a city matching your budget and approximate dates).

>[!IMPORTANT]
> Currently there is NOT even one REST API cost-free to retrieve flights, so I have included a script which simulates thousand "API request-respose" in JSON format and stores it into a SQL database.

## Scope
Design an AI Agent based on LLM. Since this requires high computer power I will leverage AWS Bedrock services to use a pretrained model.
Metaheuristic-based algorithm to converge into an optimal solution which suits user/s requirements.

## Stack
- Python
- Pydantic
- AWS Bedrock
- REST API - Flask/FastAPI

## Workflow
![workflow](docs/help-me-fly-schema.jpg)

## DEMO
### Real scenario tested on the agent
Simple user interface (FastAPI + HTML)
![alt text](docs/ui-simple.png)

User query

Talk with the agency: we are two people. One from malaga with 500 euro budget. The other from valencia, with 600 euro budget. 
we want to travel for 5 days between september and december 2025. We would like to visit either of the following cities: paris, london, milan, warsaw, barcelona, any city in denmark, any city in norway and rome. Price max of the whole trip 700 euro

Response:
```json
{
  "listTravellers": [      
    {
      "origin": "Malaga",  
      "budget": 500.0      
    },
    {
      "origin": "Valencia",
      "budget": 600.0      
    }
  ],
  "travelPlan": {
    "fromDate": "2025-09-01",
    "toDate": "2025-12-31",
    "vetoCities": null,
    "preferredCities": null,
    "priceMax": 700,
    "days": 5,
    "allowStayover": true,
    "availableDestinations": ["Paris", "London", "Milan", "Warsaw", "Barcelona", "Copenhagen", "Oslo", "Bergen", "Aarhus", "Aalborg", "Odense", "Stavanger", "Trondheim", "Tromsø", "Rome"]
  }
}
```

This is used to build the Plan instance, which is fed to the Genetic Algorithm.
With the foundations stablished, the GA starts to evolve, storing the best individual from each offspring.
After the determined number of generations, we can see how the algorithm is converging:
![ga_evolution](docs/ga_evolution.png)

Suggested trip:

Chosen destination: London
```
Traveller 1:
  Origin: Malaga
  Budget: €500.00
  Outbound Flight:
    Malaga → London
    Date: 2025-11-23 | Departure: 20:45:00 | Arrival: 00:15:00
    Price: €309.11 | Stayovers: 0 | Flight: LH3498 | Duration: 4.5h
  Return Flight:
    London → Malaga
    Date: 2025-11-26 | Departure: 06:00:00 | Arrival: 12:00:00
    Price: €29.26 | Stayovers: 1 | Flight: AF8903 | Duration: 5.0h
  Total Route Cost: €338.37

Traveller 2:
  Origin: Valencia
  Budget: €600.00
  Outbound Flight:
    Valencia → London
    Date: 2025-11-11 | Departure: 18:15:00 | Arrival: 22:09:00
    Price: €314.99 | Stayovers: 1 | Flight: IB8996 | Duration: 4.9h
  Return Flight:
    London → Valencia
    Date: 2025-11-13 | Departure: 11:30:00 | Arrival: 15:36:00
    Price: €170.37 | Stayovers: 1 | Flight: AZ450 | Duration: 3.1h
  Total Route Cost: €485.36
```
