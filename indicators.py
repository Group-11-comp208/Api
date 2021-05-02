import coincap
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from fx import Converter


class Candle:
    def __init__(self, base_id, quote_id="united-states-dollar", interval="d1", time_period=60, currency="usd"):
        self.api = coincap.CoinCap()
        self.asset = base_id
        self.currency = currency
        self.api = coincap.CoinCap()
        self.asset = self.api.get_asset(self.asset)

        self.id = self.asset['id']
        converter = Converter()

        exchanges = self.api.get_exchange_by_quote(self.id)['data']
        exchanges = sorted(exchanges, key=lambda k: float(k['percentExchangeVolume']))


        for exchange in exchanges:
            self.candle = self.api.get_asset_candle(
                self.id, exchange['exchangeId'], quote_id=quote_id, interval=interval, time_period=time_period)
            if len(self.candle['data']) != 0:
                break

        # Prepare the candle data using pandas
        self.df = pd.DataFrame(self.candle['data']).astype(float)


        self.currency_symbol = converter.get_symbol(currency)
        if currency != "usd":
            rate = converter.get_rate(currency)
            for row in self.df:
                if row != 'period':
                    self.df[row] = self.df.row * rate

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
        symbol = self.api.get_symbol(self.id)
        df = self.df
        fig = go.Figure(data=[go.Candlestick(x=df['period'],
                                             open=df['open'],
                                             high=df['high'],
                                             low=df['low'],
                                             close=df['close'])])

        fig.update_layout(xaxis_rangeslider_visible=False,
                          yaxis_title=symbol, xaxis_title="Time", title="{} vs {}".format(self.currency.upper(), symbol),  yaxis_tickformat=".1f")
        fig.write_image("candle.png")


candle = Candle("xrp")
candle.plot_candle()


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

        alpha = 2 / (self.n + 1)

        self.df.loc[0, 'ema'] = self.df.loc[0, 'priceUsd']

        self.df['ema'] = self.df.ewm(alpha=alpha).mean()

        self.df['sma'] = self.df['priceUsd'].rolling(window=self.n).mean()

        exp1 = self.df['priceUsd'].ewm(span=12, adjust=False).mean()
        exp2 = self.df['priceUsd'].ewm(span=26, adjust=False).mean()
        self.df['mcad'] = exp1 - exp2
        self.df['signal'] = self.df['mcad'].ewm(span=9, adjust=False).mean()

    def plot(self):
        symbol = self.api.get_symbol(self.id)

        max_value = self.df['mcad'].max() * 1.5

        fig = go.Figure(data=[go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Exponential Moving Average", name="EMA", y=self.df['ema'], line=dict(color='orange', width=2)),
                              go.Scatter(x=pd.to_datetime(
                                  self.df['time'], unit='ms'), text="Price", name="Price", y=self.df['priceUsd'], line=dict(color='red', width=2)),
                              go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Simple Moving Average",
                                         name="SMA", y=self.df['sma'], line=dict(color='green', width=2)),
                              go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Moving average convergence divergence ",
                                         name="MACD", y=self.df['mcad'], line=dict(color='blue', width=2), yaxis='y2'),
                              go.Scatter(x=pd.to_datetime(self.df['time'], unit='ms'), text="Signal Line", name="Signal Line", y=self.df['signal'], line=dict(color='purple', width=2), yaxis='y2')])

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
            self.df['priceUsd'] < self.df['lower_band'], 'buy', 'hold')
        self.df['sell'] = np.where(
            self.df['priceUsd'] > self.df['upper_band'], 'sell', 'hold')

        tmp = self.df.iloc[[-1]]
        return tmp['buy'].values[0], tmp['sell'].values[0]


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
