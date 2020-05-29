import requests
import os

from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table, Column, DateTime, Integer, String, inspect, select
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError


# Configure database
#engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine("postgres://cezodtnwmyvbhz:8155b6c6a9070c6b49ab1734425f4ed3d6d2b8d75a273faf4299ba8ac4ff64ca@ec2-176-34-183-20.eu-west-1.compute.amazonaws.com:5432/d2s1ov8hnefscj", echo=True)
db = scoped_session(sessionmaker(bind=engine))
table_name = 'test2'

def table_data():
    """Loads metadata instance for stocks table"""
    metadata = MetaData(engine)
    table = Table(table_name, metadata, autoload=True)
    return table


def download_stocks():
    """Look up all stock symbols for autocomplete and prunes all data that is not 'common-shares' from IEX"""
    """Only download the data if it will be inserted """
    try:
        api_key = "pk_3bb9d832c08949fabe3983d5fa39d64b"
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/ref-data/region/US/symbols?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None
    
    try:
        #filters response for 'common stock' symbols only
        stock_data = [d for d in response.json() if d['type'] == 'cs']
        
        # Select the stocks table to insert the data
        table = table_data()
        for stock in stock_data:
            ins = table.insert().values(iex_id=stock['iexId'], symbol=stock['symbol'], name=stock['name'], date=stock['date'])
            db.execute(ins)

        db.commit()
        db.close()
        print("stocks table updated successfully")
        return None
    except (KeyError, TypeError, ValueError):
        return None

def create_table():

    inspector = inspect(engine)
    table_list = inspector.get_table_names()
    if table_name in table_list:
        # Table already exists and no need to create
        pass
    else:
        # Create a metadata instance
        metadata = MetaData(engine)

        table = Table(table_name, metadata, 
                    Column('iex_id', String, primary_key=True), 
                    Column('symbol', String), 
                    Column('name', String),
                    Column('date', DateTime))

        table.create(engine, checkfirst=True)

def check_table_data():
    table = table_data()

    query = select([table.c.date]).order_by(table.c.date.asc())
    results = db.execute(query).fetchone()
    print(results)
    # compare date of return to today and then if logic

create_table()
download_stocks()