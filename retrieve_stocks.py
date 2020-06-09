from datetime import datetime, timedelta
import requests
import json

class StockData ():
    """Creates an object used to store an array of stock dicts from IEX"""

    def __init__(self):
        """Loads object with stock JSON data from IEX and the time of retrieval"""
        self.stock_data = self.retrieve_stocks()

    def retrieve_stocks(self):
        """Loads JSON file for stored stock data"""
        try:
            # checks if stock data is available locally
            stocksfile = open("stock_data.json", "r")
            self.stock_data = json.load(stocksfile)
            stocksfile.close()
            # Adds the date when stocks were obtained, using date of first stock
            self.time = datetime.strptime(self.stock_data[0]['date'], '%Y-%m-%d')
            if datetime.now() - self.time > timedelta(days=10):
                self.download_stocks()
            else:
                return self.stock_data

        except (IOError, OSError):
            # if no stock data, retrieve from API source and save it locally
            self.download_stocks()
    
    def download_stocks(self):
        """Look up all stock symbols for autocomplete and prunes all data that is not 'common-shares' from IEX"""
        try:
            api_key = "pk_3bb9d832c08949fabe3983d5fa39d64b"
            response = requests.get(f"https://cloud-sse.iexapis.com/stable/ref-data/region/US/symbols?token={api_key}")
            response.raise_for_status()
        except requests.RequestException:
            return None
        
        try:
            # filters response for 'common stock' symbols only
            self.stock_data = [d for d in response.json() if d['type'] == 'cs']
            
            # save stock data as json file
            stocksfile = open("stock_data.json", "w")
            json.dump(self.stock_data, stocksfile)
            stocksfile.close()

            # update timestamp
            self.time = datetime.now()

            return self.stock_data
        except (KeyError, TypeError, ValueError):
            return None