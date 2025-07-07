from sqlalchemy import create_engine, Column, Integer, String, Float, Date, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date
from typing import Optional

Base = declarative_base()

class FlightDB(Base):
    __tablename__ = "flights"
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_city = Column(String)
    to_city = Column(String)
    departure_date = Column(Date)
    departure_time_local = Column(DateTime)
    arrival_time_local = Column(DateTime)
    price_eur = Column(Float)
    stayovers = Column(Integer)
    flight_number = Column(String)
    duration_hours = Column(Float)

class Flight(BaseModel):
    from_city: str
    to_city: str
    departure_date: date
    departure_time_local: datetime
    arrival_time_local: datetime
    price_eur: float
    stayovers: int
    flight_number: str
    duration_hours: float

    model_config = ConfigDict(from_attributes=True)

    def __str__(self):
        return super().__str__()
    
    def __repr__(self):
        return f"Flight: {self.flight_number} | " \
        f"Origin: {self.from_city} -> Destination: {self.to_city} | " \
        f"Departure: {self.departure_time_local}, arriving at {self.arrival_time_local} (duration {self.duration_hours} hours) | " \
        f"Price: {self.price_eur} euro | " \
        f"Stayovers: {self.stayovers}"
    
class FlightSelection(BaseModel):
    startDate: date # spectrum of days you want to fly
    endDate: date
    priceMax: Optional[float] = None
    startCity: str
    destinationCity: Optional[str] = None
    vetoDestinations: Optional[list[str]] = None
    stayoversAllowed: bool = True