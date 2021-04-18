import coincap
import geko
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime


class Candle:
    def __init__(self, asset, time_period=14, currency='usd'):
        self.currency = currency
        self.api = coincap.CoinCap()
        self.geko = geko.Geko()
        asset = self.api.get_asset(asset)
        self.id = asset['id']
        self.candle = self.geko.get_asset_candle(self.id, time_period=time_period, currency=currency)

        # Prepare the candle data using pandas
        self.df = pd.DataFrame(self.candle).astype(float)
        self.df[0] = pd.to_datetime(self.df[0], unit='ms')

    def get_rsi(self):
        """ Return relative strength indicator of a currency"""
        diff = self.df[1] - self.df[4]

        average_gain = diff[diff > 0].mean()
        average_loss = diff[diff < 0].mean() * -1

        relative_strength = average_gain/average_loss
        relative_strength_indicator = 100 - 100 / (1 + relative_strength)

        return relative_strength_indicator

    def plot_candle(self):
        """ Plots the candlesticks for a given time period"""
        symbol = self.api.get_symbol(self.id)
        df = self.df
        fig = go.Figure(data=[go.Candlestick(x=df[0],
                                             open=df[1],
                                             high=df[2],
                                             low=df[3],
                                             close=df[4])])

        fig.update_layout(xaxis_rangeslider_visible=False,
                          yaxis_title=symbol, xaxis_title="Time", title="{} vs {}".format(self.currency.upper(), symbol))
        fig.write_html("fig1.html")
        fig.write_image("fig1.png")
