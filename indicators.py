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
        self.asset = self.api.get_asset(asset)
        self.id = self.asset['id']
        self.candle = self.geko.get_asset_candle(
            self.id, time_period=time_period, currency=currency)

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
                          yaxis_title=symbol, xaxis_title="Time", title="{} vs {}".format(self.currency.upper(), symbol),  yaxis_tickformat=".1f")
        fig.write_image("fig1.png")


class MovingAverages():
    def __init__(self, asset, n=10, currency='usd', interval='d1', num_days=120):
        self.n = n
        self.currency = currency
        self.api = coincap.CoinCap()
        self.asset = self.api.get_asset(asset)
        self.id = self.asset['id']
        history = self.api.get_asset_history(self.id, num_days=num_days)['data']
        self.df = pd.DataFrame(
            history, columns=['priceUsd', 'time']).astype(float)

    def plot(self):
        symbol = self.api.get_symbol(self.id)
        alpha = 2 / (self.n + 1)

        self.df.loc[0, 'ema'] = self.df.loc[0, 'priceUsd']

        self.df['ema'] = self.df.ewm(alpha=alpha).mean()

        self.df['sma'] = self.df['priceUsd'].rolling(window=self.n).mean()

        exp1 = self.df['priceUsd'].ewm(span=12, adjust=False).mean()
        exp2 = self.df['priceUsd'].ewm(span=26, adjust=False).mean()
        self.df['mcad'] = exp1 - exp2

        max_value = self.df['mcad'].max() * 1.5

        fig = go.Figure(data=[go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Exponential Moving Average", name="EMA", y=self.df['ema'], line=dict(color='orange', width=2)),
                              go.Scatter(x=pd.to_datetime(
                                  self.df['time'], unit='ms'), text="Price", name="Price", y=self.df['priceUsd'], line=dict(color='red', width=2)),
                              go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Simple Moving Average",
                                         name="SMA", y=self.df['sma'], line=dict(color='green', width=2)),
                              go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Moving average convergence divergence ", name="MACD", y=self.df['mcad'], line=dict(color='blue', width=2), yaxis='y2')])
        
        fig.update_layout(yaxis_title=symbol, xaxis_title="Time", title="{} vs {}".format(self.currency.upper(), symbol), yaxis_tickformat=".0f", yaxis2=dict(title='MCAD', overlaying='y', side='right', range=[ -max_value, max_value]))

        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

        fig.write_image("moving_averages.png")

class BoilerBands:
    def __init__(self, asset, n=10, currency='usd', interval='d1', num_days=120):
        self.n = n
        self.currency = currency
        self.api = coincap.CoinCap()
        self.asset = self.api.get_asset(asset)
        self.id = self.asset['id']
        history = self.api.get_asset_history(self.id, num_days=num_days)['data']
        self.df = pd.DataFrame(
            history, columns=['priceUsd', 'time']).astype(float)

    def plot(self, num_sd=2):
        symbol = self.api.get_symbol(self.id)

        self.df['sma'] = self.df['priceUsd'].rolling(window=self.n).mean()
        self.df['std'] = self.df['priceUsd'].rolling(window=self.n).std()
        self.df['lower_band'] = self.df['sma'] + (self.df['std'] * num_sd)
        self.df['upper_band'] = self.df['sma'] - (self.df['std'] * num_sd)

        fig = go.Figure(data=[go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Lower Band", name="Lower Band", y=self.df['lower_band'], line=dict(color='red', width=2)),
        go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Upper Band", name="Upper Band", y=self.df['upper_band'], line=dict(color='red', width=2) , fill='tonexty'),
                              go.Scatter(x=pd.to_datetime(
                                  self.df['time'], unit='ms'), text="Price", name="Price", y=self.df['priceUsd'], line=dict(color='blue', width=2)),
                              go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Simple Moving Average",
                                         name="SMA", y=self.df['sma'], line=dict(color='green', width=2))])
        
        fig.update_layout(yaxis_title=symbol, xaxis_title="Time", title="{} vs {}".format(self.currency.upper(), symbol), yaxis_tickformat=".0f")

        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

        fig.write_image("boiler_bands.png")


bb = BoilerBands("eth")

bb.plot()