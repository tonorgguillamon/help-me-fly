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

## DEMO
# Real scenario tested on the agent
User query:
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
    "availableDestinations": ["Paris", "London", "Milan", "Warsaw", "Barcelona", "Denmark", "Norway", "Rome"]
  }
}
```

This is used to build the Plan instance, which is fed to the Genetic Algorithm.
With the foundations stablished, the GA starts to evolve, storing the best individual from each offspring.
After the determined number of generations, we can see how the algorithm is converging:
![ga_evolution](docs/ga_evolution.PNG)
