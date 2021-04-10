# CoinCap python Wrapper
A python wrapper for the coincap API

## Usage

```
from coincap import CoinCap

coincap = CoinCap()
```

 
### Get list of all assets
 ```
 coincap.get_assets()
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
