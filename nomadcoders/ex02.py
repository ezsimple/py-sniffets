# 비트코인 어제 종가 알아보기
# %%

import yfinance as yf
import requests

def get_bitcoin_price_in_krw():
    # Ticker symbol for Bitcoin on Yahoo Finance
    btc_ticker = 'BTC-USD'
    
    # Fetch the data for Bitcoin
    btc_data = yf.Ticker(btc_ticker)
    
    # Get the current price in USD
    btc_price_usd = btc_data.history(period='1d')['Close'].iloc[-1]
    
    # Your API access key
    api_key = 'YOUR_ACCESS_KEY'
    
    # Fetch the USD to KRW exchange rate
    url = f'http://api.exchangeratesapi.io/v1/latest?access_key={api_key}&symbols=USD,KRW'
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    exchange_rate_data = response.json()
    
    if not exchange_rate_data.get('success', True):
        raise Exception(f"API request failed: {exchange_rate_data.get('error', {}).get('info', 'Unknown error')}")
    
    eur_to_usd_rate = exchange_rate_data['rates']['USD']
    eur_to_krw_rate = exchange_rate_data['rates']['KRW']
    
    # Convert EUR to USD and then USD to KRW
    usd_to_krw_rate = eur_to_krw_rate / eur_to_usd_rate
    print(usd_to_krw_rate)
    
    # Convert the Bitcoin price to KRW
    btc_price_krw = btc_price_usd * usd_to_krw_rate
    
    return btc_price_krw

# Example usage
if __name__ == "__main__":
    try:
        current_btc_price_krw = get_bitcoin_price_in_krw()
        print(f"현재 비트코인 가격은: ₩{current_btc_price_krw:,.2f}")
    except Exception as e:
        print(f"Error: {e}")
