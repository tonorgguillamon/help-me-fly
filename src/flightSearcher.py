from pydantic import BaseModel
from src.flight import FlightDB
from datetime import datetime, date
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Trip(BaseModel):
    startDate: date # spectrum of days you want to fly
    endDate: date
    priceMax: Optional[int] = None
    startCity: str
    preferredDestinations: Optional[list[str]] = None
    vetoDestinations: Optional[list[str]] = None
    stayoversAllowed: bool = True

class FlightEngine:
    def __init__(self, databaseName: str):
        self.engine = create_engine(f'sqlite:///{databaseName}.db')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def retrieveAllFlights(self):
        try:
            return self.session.query(FlightDB).all()
        finally:
            self.session.close()

    def retrieveFlights(self, trip: Trip):
        try:
            filters = [
                FlightDB.departure_date >= trip.startDate,
                FlightDB.departure_date <= trip.endDate,
                FlightDB.from_city == trip.startCity,
            ]
            if trip.priceMax:
                filters.append(FlightDB.price_eur <= trip.priceMax)
            if trip.preferredDestinations:
                filters.append(FlightDB.to_city.in_(trip.preferredDestinations))
            if trip.vetoDestinations: # filter out with ~
                filters.append(~FlightDB.to_city.in_(trip.vetoDestinations))
            if not trip.stayoversAllowed:
                filters.append(FlightDB.stayovers == 0)

            return self.session.query(FlightDB).filter(*filters).all()
        finally:
            self.session.close()
