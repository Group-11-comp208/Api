import coincap
import pandas as pd

api = coincap.CoinCap()
candle = api.get_asset_candle("ethereum", "bitcoin", exchange="binance")

df = pd.DataFrame(candle['data']).astype(float)
diff = df['open'] - df['close']

average_gain = diff[diff > 0].mean()
avergae_loss = diff[diff < 0].mean() * -1

relative_strength = average_gain/avergae_loss
relative_strength_indicator = 100 - 100 / (1 + relative_strength)

print(relative_strength_indicator)

