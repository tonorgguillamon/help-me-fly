from src.flight import FlightDB, FlightSelection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class FlightEngine:
    def __init__(self, databaseName: str):
        self.engine = create_engine(f'sqlite:///{databaseName}.db')
        self.Session = sessionmaker(bind=self.engine)

    def retrieveAllFlights(self):
        session = self.Session()
        try:
            return session.query(FlightDB).all()
        finally:
            session.close()

    def retrieveFlights(self, trip: FlightSelection):
        session = self.Session()
        try:
            filters = [
                FlightDB.departure_date >= trip.startDate,
                FlightDB.departure_date <= trip.endDate,
                FlightDB.from_city == trip.startCity,
            ]
            if trip.priceMax:
                filters.append(FlightDB.price_eur <= trip.priceMax)
            if trip.destinationCity:
                filters.append(FlightDB.to_city == trip.destinationCity)
            if trip.vetoDestinations: # filter out with ~
                filters.append(~FlightDB.to_city.in_(trip.vetoDestinations))
            if not trip.stayoversAllowed:
                filters.append(FlightDB.stayovers == 0)

            return session.query(FlightDB).filter(*filters).all()
        finally:
            session.close()
