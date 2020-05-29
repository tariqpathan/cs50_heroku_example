from datetime import datetime, timedelta
import requests

class StockData:
    """Creates an object used to store an array of stock dicts from IEX"""

    def __init__(self):
        """Loads object with stock JSON data from IEX and the time of retrieval"""
        self.stock_data = self.retrieve_stocks()
        self.time = datetime.now()

    def check_stock_data(self):
        """Retrieves stocks if they were obtained over 6 hours ago"""
        print(datetime.now() - self.time)
        if datetime.now() - self.time > timedelta(hours=6):
            self.retrieve_stocks()
        else:
            return self.stock_data

    def retrieve_stocks(self):
        """Look up all stock symbols for autocomplete and prunes all data that is not 'common-shares' from IEX"""

        try:
            api_key = "pk_3bb9d832c08949fabe3983d5fa39d64b"
            response = requests.get(f"https://cloud-sse.iexapis.com/stable/ref-data/region/US/symbols?token={api_key}")
            response.raise_for_status()
        except requests.RequestException:
            return None
        
        try:
            #filters response for 'common stock' symbols only
            self.stock_data = [d for d in response.json() if d['type'] == 'cs']
            self.time = datetime.now()
            return self.stock_data
        except (KeyError, TypeError, ValueError):
            return None
    
        