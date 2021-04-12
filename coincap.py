import requests
import json
import time

URL = 'https://api.coincap.io/v2/'

class CoinCap:
    def __init__(self, url=URL):
        self.url = url

    def _query(self, endpoint):
        """Returns json as dictionary"""
        response = requests.request("GET", self.url + endpoint)

        if response.status_code != 200:
            raise Exception('The server has responded with an error')

        response = json.loads(response.text)
        return response

    def _get_date(self, num_days):
        end = time.time() * 1000
        start = end - (num_days * 86400000)
        return start, end

    def get_assets(self):
        return self._query("assets")

    def get_asset(self, asset):
        return self._query("assets/{}".format(asset))

    def get_asset_history(self, asset, interval="d1"):
        return self._query("assets/{}/history?interval={}".format(asset, interval))

    def get_asset_markets(self, asset):
        return self._query("assets/{}/markets".format(asset))

    def get_rates(self):
        return self._query("rates")

    def get_asset_rate(self, asset):
        return self._query("rates/{}".format(asset))

    def get_exchanges(self):
        return self._query("exchanges")

    def get_exchange(self, exchange):
        return self._query("exchanges/{}".format(exchange))

    def get_markets(self):
        return self._query("markets")

    def get_asset_candle(self, base_id, exchange, quote_id="bitcoin", interval="d1", time_period=14):
        start, end = self._get_date(time_period)
        return self._query(
            "candles?exchange={}&interval={}&baseId={}&quoteId={}&start={}&end={}".format(exchange, interval, base_id, quote_id, start, end))

    def get_symbol(self, asset):
        return self.get_asset(asset)['data']['symbol']