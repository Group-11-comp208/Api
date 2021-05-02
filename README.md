# CoinCap python Wrapper
A python wrapper for the coincap API, returns data as structured dictonary where keys repsond to json item names

## Usage

```
from coincap import CoinCap

coincap = CoinCap()
```

### Get single asset data
 ```
 coincap.get_asset('bitcoin')
 ```
##### Response
```
data	
id	"bitcoin"
rank	"1"
symbol	"BTC"
name	"Bitcoin"
supply	"18672456.0000000000000000"
maxSupply	"21000000.0000000000000000"
marketCapUsd	"1107798869676.6394893994158864"
volumeUsd24Hr	"22465466214.3528102554480625"
priceUsd	"59327.9678729268120594"
changePercent24Hr	"1.7838575668641382"
vwap24Hr	"59796.2948055513798961"
explorer	"https://blockchain.info/"
timestamp	1618093941684
```
##### Example

```
repsonse[data][id] -> bitcoin
repsonse[data][priceUsd] -> 59327.9678729268120594
```

# fx currency convert class 
A python class to convert the currencies 

## Usage

```
from fx import Converter

converter = Converter()
```

### Example: get exchange rate for USD (default currency) to GBP
 ```
 converter.get_rate("GBP")
 ```
##### Response
```
0.71930929108829
```
