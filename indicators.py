import coincap
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime


class Candle:
    def __init__(self, base_id, exchange, quote_id="bitcoin", interval="d1", time_period=14):
        self.api = coincap.CoinCap()
        self.asset = base_id
        self.candle = self.api.get_asset_candle(base_id, exchange, quote_id=quote_id, interval=interval, time_period=time_period)

        # Prepare the candle data using pandas
        self.df = pd.DataFrame(self.candle['data']).astype(float)
        self.df['period'] = pd.to_datetime(self.df['period'], unit='ms')

    def get_rsi(self):
        """ Return relative strength indicator of a currency"""
        diff = self.df['open'] - self.df['close']

        average_gain = diff[diff > 0].mean()
        average_loss = diff[diff < 0].mean() * -1

        relative_strength = average_gain/average_loss
        relative_strength_indicator = 100 - 100 / (1 + relative_strength)

        return relative_strength_indicator

    def get_obv(self):
        """ Returns on-balance volume indicator of a currency"""
        diff = self.df['open'] - self.df['close']

        p_volume = np.sum(self.df['volume'][diff > 0])
        n_volume = np.sum(self.df['volume'][diff < 0])
        obv = p_volume - n_volume

        return obv

    def plot_candle(self):
        """ Plots the candlesticks for a given time period"""
        symbol = self.api.get_symbol(self.asset)
        df = self.df
        fig = go.Figure(data=[go.Candlestick(x=df['period'],
                                             open=df['open'],
                                             high=df['high'],
                                             low=df['low'],
                                             close=df['close'])])

        fig.update_layout(xaxis_rangeslider_visible=False,
                          yaxis_title=symbol, xaxis_title="Time")
        fig.write_html("fig1.html")
        fig.write_image("fig1.png")


#candle = Candle("xrp", exchange="binance")
#candle.plot_candle()
