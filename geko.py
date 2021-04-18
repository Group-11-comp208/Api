import requests
import json
import time

URL = 'https://api.coingecko.com/api/v3/coins/'


class Geko:
    def __init__(self, url=URL):
        self.url = url

    def _query(self, endpoint):
        """Returns json as dictionary"""
        response = requests.request("GET", self.url + endpoint)

        if response.status_code != 200:
            raise Exception('The server has responded with an error')

        response = json.loads(response.text)
        return response

    def get_asset_candle(self, asset, currency='usd', time_period=14):
        return self._query(
            "{}/ohlc?vs_currency={}&days={}".format(asset, currency, time_period))
