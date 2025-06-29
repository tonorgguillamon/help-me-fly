import random
from datetime import datetime, timedelta, time, date
import pytz
from src.flight import Base, FlightDB
import os

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DB = "flightsAPI.db"

if os.path.exists(DB):
    os.remove(DB)

# Create Engine and Session
engine = create_engine(f"sqlite:///{DB}")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

MAJOR_EUROPEAN_HOLIDAYS = {
    # Fixed dates
    date(2025, 1, 1),   # New Year's Day
    date(2025, 12, 24), # Christmas Eve
    date(2025, 12, 25), # Christmas
    date(2025, 12, 31), # New Year's Eve
    date(2025, 5, 1),   # Labour Day

    # Easter-related, approximately
    date(2025, 4, 18),
    date(2025, 4, 20),
    date(2025, 4, 21),
}

SUMMER_HOTSPOTS = {
    "Barcelona", "Nice", "Athens", "Rome", "Lisbon",
    "Split", "Valletta", "Dubrovnik", "Palermo",
    "Malta", "Marseille", "Seville", "Valencia",
    "Porto", "Thessaloniki", "Naples", "Santorini",
    "Ibiza", "Mykonos", "Cannes", "Corfu", "Malaga"
}

european_cities = {
    "London": "Europe/London",
    "Manchester": "Europe/London",
    "Paris": "Europe/Paris",
    "Lyon": "Europe/Paris",
    "Marseille": "Europe/Paris",
    "Brussels": "Europe/Brussels",
    "Amsterdam": "Europe/Amsterdam",
    "Rotterdam": "Europe/Amsterdam",
    "Luxembourg": "Europe/Luxembourg",
    "Berlin": "Europe/Berlin",
    "Frankfurt": "Europe/Berlin",
    "Munich": "Europe/Berlin",
    "Vienna": "Europe/Vienna",
    "Zurich": "Europe/Zurich",
    "Geneva": "Europe/Zurich",
    "Prague": "Europe/Prague",
    "Bratislava": "Europe/Bratislava",
    "Warsaw": "Europe/Warsaw",
    "Krakow": "Europe/Warsaw",
    "Budapest": "Europe/Budapest",
    "Rome": "Europe/Rome",
    "Milan": "Europe/Rome",
    "Naples": "Europe/Rome",
    "Palermo": "Europe/Rome",
    "Madrid": "Europe/Madrid",
    "Barcelona": "Europe/Madrid",
    "Valencia": "Europe/Madrid",
    "Malaga": "Europe/Madrid",
    "Seville": "Europe/Madrid",
    "Lisbon": "Europe/Lisbon",
    "Porto": "Europe/Lisbon",
    "Athens": "Europe/Athens",
    "Thessaloniki": "Europe/Athens",
    "Malta": "Europe/Malta",
    "Stockholm": "Europe/Stockholm",
    "Gothenburg": "Europe/Stockholm",
    "Oslo": "Europe/Oslo",
    "Bergen": "Europe/Oslo",
    "Copenhagen": "Europe/Copenhagen",
    "Helsinki": "Europe/Helsinki",
    "Tallinn": "Europe/Tallinn",
    "Riga": "Europe/Riga",
    "Vilnius": "Europe/Vilnius",
    "Sofia": "Europe/Sofia",
    "Bucharest": "Europe/Bucharest",
    "Belgrade": "Europe/Belgrade",
    "Skopje": "Europe/Skopje",
    "Sarajevo": "Europe/Sarajevo",
    "Podgorica": "Europe/Podgorica",
    "Tirana": "Europe/Tirane",
    "Chisinau": "Europe/Chisinau",
    "Ljubljana": "Europe/Ljubljana",
    "Zagreb": "Europe/Zagreb",
    "Andorra la Vella": "Europe/Andorra",
    "San Marino": "Europe/Rome",
    "Monaco": "Europe/Monaco",
    "Vaduz": "Europe/Vaduz",
    "Reykjavik": "Atlantic/Reykjavik",
    "Dublin": "Europe/Dublin"
}

def is_major_holiday(flight_date):
    return flight_date in MAJOR_EUROPEAN_HOLIDAYS

def dynamic_price(base_price, dep_datetime, stayovers, duration_hours):
    days_until_departure = (dep_datetime.date() - datetime.today().date()).days
    weekday = dep_datetime.weekday()  # Monday = 0, Sunday = 6
    month = dep_datetime.month
    hour = dep_datetime.hour

    flight_date = dep_datetime.date()

    price = base_price

    # 1. Price increases as date approaches
    if days_until_departure < 7:
        price *= 1.5  # Last-minute
    elif days_until_departure < 30:
        price *= 1.35
    elif days_until_departure < 60:
        price *= 1.2
    elif days_until_departure > 120:
        price *= 0.85

    # 2. Weekend multiplier
    if weekday in [4, 5]:  # Friday or Saturday
        price *= 1.15

    # 3. Stayovers discount
    if stayovers == 1:
        price *= 0.85

    # 4. Peak hours (morning & evening)
    if 7 <= hour <= 9 or 17 <= hour <= 20:
        price *= 1.1

    # 5. Longer flights = potentially higher cost
    price *= 1 + (duration_hours / 10)

    # 6. Holidays
    if is_major_holiday(flight_date):
        price *= 1.25

    # 7. Hotspots for summer
    if to_city in SUMMER_HOTSPOTS and month in [6, 7, 8]:
        price *=1.3

    return round(price, 2)

start_date = datetime.today()
dates = [start_date + timedelta(days=i) for i in range(180)]

flights = []
for _ in range(20000):
    from_city, to_city = random.sample(list(european_cities.keys()), 2)
    dateValue = random.choice(dates)
    from_tz = pytz.timezone(european_cities[from_city])
    to_tz = pytz.timezone(european_cities[to_city])

    base_price = random.randint(10, 300)
    duration_hours = round(random.uniform(1.0, 5.0), 1)
    stayovers=random.choice([0, 1])

    dep_hour = random.randint(5, 22)
    dep_minute = random.choice([0, 15, 30, 45])
    dep_datetime = from_tz.localize(datetime.combine(dateValue, time(dep_hour, dep_minute)))

    arr_datetime = dep_datetime + timedelta(hours=duration_hours)
    arr_datetime = arr_datetime.astimezone(to_tz)

    flightData = FlightDB(
        from_city=from_city,
        to_city=to_city,
        departure_date=dateValue,
        departure_time_local=dep_datetime,
        arrival_time_local=arr_datetime,
        price_eur=dynamic_price(
            base_price,
            dep_datetime,
            stayovers,
            duration_hours
        ),
        stayovers=stayovers,
        flight_number=f"{random.choice(['LH', 'AF', 'BA', 'IB', 'KL', 'SK', 'LO', 'AZ'])}{random.randint(100, 9999)}",
        duration_hours=duration_hours
    )

    session.add(flightData)

session.commit()
session.close()
