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
