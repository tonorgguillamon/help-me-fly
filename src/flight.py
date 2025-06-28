from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Flight(Base):
    __tablename__ = "flights"
    id = Column(Integer, primary_key=True, autoincrement=True)
    from_city = Column(String)
    to_city = Column(String)
    departure_date = Column(String)
    departure_time_local = Column(String)
    arrival_time_local = Column(String)
    price_eur = Column(Float)
    stayovers = Column(Integer)
    flight_number = Column(String)
    duration_hours = Column(Float)