import os
import requests
import re

def get_stock_data():
    try:
        api_key = "pk_3bb9d832c08949fabe3983d5fa39d64b"
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/ref-data/region/US/symbols?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    try:
        #filters response for 'common stock' symbols only
        symbols = [d for d in response.json() if d['type'] == 'cs']
        print(symbols[100])
        return symbols
    except (KeyError, TypeError, ValueError):
        return None

def search_stock_data():
    # This should return a list of dicts to search
    symbols = get_stock_data()
    returned_stocks = []
    
    for symbol in symbols:
        if re.match('ap.*', symbol['name'], re.IGNORECASE) and len(returned_stocks) < 11:
            returned_stocks.append(symbol)
        
            

    print(returned_stocks)

    # search the name in each dict which matches the query
    # append each dict to a new list
    # stop when 10 dicts are found

search_stock_data()