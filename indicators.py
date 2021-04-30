import coincap
import geko
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from fx import Converter


class Candle:
    def __init__(self, asset, time_period=30, currency='usd'):
        self.currency = currency
        self.api = coincap.CoinCap()
        self.geko = geko.Geko()
        self.asset = self.api.get_asset(asset)
        self.id = self.asset['id']

        period = time_period

        if time_period <= 7:
            period = 14
        if time_period >= 14 and time_period < 50:
            period = 30
        if time_period >= 50 and time_period < 120:
            period = 90
        if time_period >= 120 and time_period < 250:
            period = 180
        if time_period >= 250:
            period = 365

        self.candle = self.geko.get_asset_candle(
            self.id, time_period=period, currency=currency)

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
        fig.write_image("candle.png")


class MovingAverages:
    def __init__(self, asset, currency='usd', num_days=120):
        self.n = 10
        self.currency = currency
        self.api = coincap.CoinCap()
        self.asset = self.api.get_asset(asset)
        self.id = self.asset['id']
        converter = Converter()

        interval = "d1"
        if num_days < 30:
            self.n = 5
            interval = "h12"
        if num_days < 10:
            self.n = 2
            interval = "h6"
        if num_days < 5:
            self.n = 2
            interval = "h2"

        history = self.api.get_asset_history(
            self.id, num_days=num_days, interval=interval)['data']
        self.df = pd.DataFrame(
            history, columns=['priceUsd', 'time']).astype(float)

        self.currency_symbol = converter.get_symbol(currency)
        if currency != "usd":
            rate = converter.get_rate(currency)
            self.df['priceUsd'] = self.df['priceUsd'] * rate

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

        fig.update_layout(yaxis_title=symbol, xaxis_title="Time", title="{} vs {}".format(self.currency.upper(
        ), symbol), yaxis_tickformat=".0f", yaxis2=dict(title='MCAD', overlaying='y', side='right', range=[-max_value, max_value]))

        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

        fig.write_image("moving_averages.png")


class BoilerBands:
    def __init__(self, asset, currency='usd', num_days=120, num_sd=2):
        self.n = 10
        self.currency = currency
        self.api = coincap.CoinCap()
        self.asset = self.api.get_asset(asset)
        self.id = self.asset['id']
        converter = Converter()

        interval = "d1"
        if num_days < 30:
            self.n = 5
            interval = "h12"
        if num_days < 10:
            self.n = 2
            interval = "h6"
        if num_days < 5:
            self.n = 2
            interval = "h2"

        history = self.api.get_asset_history(
            self.id, num_days=num_days, interval=interval)['data']
        self.df = pd.DataFrame(
            history, columns=['priceUsd', 'time']).astype(float)

        self.currency_symbol = converter.get_symbol(currency)
        if currency != "usd":
            rate = converter.get_rate(currency)
            self.df['priceUsd'] = self.df['priceUsd'] * rate

        self.df['sma'] = self.df['priceUsd'].rolling(window=self.n).mean()
        self.df['std'] = self.df['priceUsd'].rolling(window=self.n).std()
        self.df['upper_band'] = self.df['sma'] + (self.df['std'] * num_sd)
        self.df['lower_band'] = self.df['sma'] - (self.df['std'] * num_sd)

    def plot(self):
        symbol = self.api.get_symbol(self.id)

        fig = go.Figure(data=[go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Lower Band", name="Lower Band", y=self.df['lower_band'], line=dict(color='red', width=2)),
                              go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Upper Band", name="Upper Band", y=self.df['upper_band'], line=dict(
                                  color='red', width=2), fill='tonexty'),
                              go.Scatter(x=pd.to_datetime(
                                  self.df['time'], unit='ms'), text="Price", name="Price", y=self.df['priceUsd'], line=dict(color='blue', width=2)),
                              go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Simple Moving Average",
                                         name="SMA", y=self.df['sma'], line=dict(color='green', width=2))])

        fig.update_layout(yaxis_title=symbol, xaxis_title="Time", title="{} vs {}".format(
            self.currency.upper(), symbol), yaxis_tickformat=".0f")

        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))

        fig.write_image("boiler_bands.png")

    def get_signal(self):
        self.df['buy'] = np.where(
            self.df['priceUsd'] > self.df['upper_band'], 'buy', 'hold')
        self.df['sell'] = np.where(
            self.df['priceUsd'] < self.df['lower_band'], 'sell', 'hold')

        tmp = self.df.iloc[[-1]]
        return tmp['buy'], tmp['sell']


class Returns:
    def __init__(self, asset, currency='usd', num_days=365, risk_free=0.01):
        self.rf = risk_free
        self.currency = currency
        self.api = coincap.CoinCap()
        self.asset = self.api.get_asset(asset)
        self.id = self.asset['id']
        converter = Converter()

        interval = "d1"
        if num_days < 30:
            self.n = 5
            interval = "h12"
        if num_days < 10:
            self.n = 2
            interval = "h6"
        if num_days < 5:
            self.n = 2
            interval = "h2"

        history = self.api.get_asset_history(
            self.id, num_days=num_days, interval=interval)['data']
        self.df = pd.DataFrame(
            history, columns=['priceUsd', 'time']).astype(float)

        self.currency_symbol = converter.get_symbol(currency)
        if currency != "usd":
            rate = converter.get_rate(currency)
            self.df['priceUsd'] = self.df['priceUsd'] * rate

    def calculate_returns(self):
        returns = self.df['priceUsd'].cumsum()
        returns = (returns - returns.shift(1))/returns.shift(1)
        sharpe_ratio = (returns.mean() - self.rf)/returns.std() * np.sqrt(252)

        return sharpe_ratio