import requests
import json
import time

URL = 'http://www.floatrates.com/daily/usd.json'

class Converter:
    def __init__(self, url=URL):
        self.url = url
        
        response = requests.request("GET", self.url)

        if response.status_code != 200:
            raise Exception('The server has responded with an error')
        
        self.curreny = json.loads(response.text)
        
        response = requests.request("GET", "https://gist.githubusercontent.com/Fluidbyte/2973986/raw/8bb35718d0c90fdacb388961c98b8d56abc392c9/Common-Currency.json")

        if response.status_code != 200:
            raise Exception('The server has responded with an error')
        
        self.symbols =  json.loads(response.text)
        

    def get_rate(self, currency):
        rate = self.curreny[currency.lower()]['rate']
        return rate

    def get_symbol(self, currency):
        return self.symbols[currency.upper()]['symbol']