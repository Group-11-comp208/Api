import coincap
import pandas as pd
import numpy as np

class Candle:
    def __init__(self, base_id, exchange, quote_id="bitcoin", interval="d1", time_period=14):
        api = coincap.CoinCap()
        self.candle = api.get_asset_candle(base_id,exchange="binance")
        self.df = pd.DataFrame(self.candle['data']).astype(float)

    def get_rsi(self):
        """ Return relative strength indicator of a currency"""
        diff = self.df['open'] - self.df['close']

        average_gain = diff[diff > 0].mean()
        avergae_loss = diff[diff < 0].mean() * -1

        relative_strength = average_gain/avergae_loss
        relative_strength_indicator = 100 - 100 / (1 + relative_strength)

        return relative_strength_indicator

    def get_obv(self):
        """ Returns on-balance volume indicator of a currency"""
        diff = self.df['open'] - self.df['close']

        p_volume = np.sum(self.df['volume'][diff > 0])
        n_volume = np.sum(self.df['volume'][diff < 0])
        obv = p_volume - n_volume

        return obv

candle = Candle("filecoin",exchange="binance")
print(candle.get_obv())

