import json
import requests
from bs4 import BeautifulSoup

def get_relevant_data_from_url(stock_url):
    page = requests.get(stock_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    get_relevant_data = {}

    # Get current Price
    get_relevant_data['current_price'] = soup.find_all(id="Nse_Prc_tick")[0].string.strip()

    # Get other get_relevant data of iterate_over_stocks

    # return
    return get_relevant_data

# Add code for status code for both buy and sell
# Add for sell code

def calculate(stock, get_relevant_data):
    current_price = float(get_relevant_data['current_price'])
    suggested_price = float(stock['suggested_price'])
    buy_percentage_change = float(stock['buy_percentage_change'])

    suggested_price_range_low = float(suggested_price - (suggested_price * buy_percentage_change))
    suggested_price_range_high = float(suggested_price + (suggested_price * buy_percentage_change))

    print stock['name'], current_price, suggested_price, suggested_price_range_low, suggested_price_range_high

    if current_price >= suggested_price and current_price <= suggested_price_range_high:
        print "Buy High"
    elif current_price <= suggested_price and current_price >= suggested_price_range_low:
        print "Buy Low"
    elif current_price <= suggested_price_range_low:
        print "Buy Very Low"


def iterate_over_stocks(stocks):
    result = {}
    for stock in stocks:
        get_relevant_data = get_relevant_data_from_url(stock['url'])
        get_action_call = calculate(stock, get_relevant_data)

# Enable cron job
# Enable Sending push notification or Email
# Add if else in case the company is not listed in NSE - Example: JK Agri Genetics Ltd -
# Add Json comment in future for JH Agri : You can book some profit above 2000 and keep rest of the shares for further gain. Still there is huge growth potential in next 4- 5 years

if __name__ == "__main__":
    with open("./stocks.json", "r") as read_file:
        stocks = json.load(read_file)
    iterate_over_stocks(stocks)
