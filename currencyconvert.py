#https://free.currconv.com/api/v7/convert?q=USD_EUR&compact=ultra&apiKey=670089713be0fe62957d
#URL1 = "https://free.currconv.com/api/v7/convert?" #q=USD_EUR
#URL2 = "&compact=ultra&apiKey=670089713be0fe62957"

from forex_python.converter import CurrencyRates

class currencyconvert:
    def get_currency_rate(currencyA, currencyB):
        c = CurrencyRates()
        return(c.get_rate(currencyA, currencyB))


if __name__ == '__main__':
    test = currencyconvert
    print(test.get_currency_rate('USD', 'EUR'))