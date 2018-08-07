import json
import requests
from bs4 import BeautifulSoup

def get_relevant_data_from_url(stock_url):
    page = requests.get(stock_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # return variable of function
    get_relevant_data = {}

    # Get current Price
    get_relevant_data['current_price'] = soup.find_all(id="Nse_Prc_tick")[0].string.strip()

    # Get other get_relevant data of iterate_over_stocks

    # return
    return get_relevant_data


# Add code for status code for both buy and sell
# Add for sell code
def get_buy_sell_action(stock, get_relevant_data):
    current_price = float(get_relevant_data['current_price'])
    suggested_price = float(stock['suggested_price'])
    buy_percentage_change = float(stock['buy_percentage_change'])

    suggested_price_range_low = float(suggested_price - (suggested_price * buy_percentage_change))
    suggested_price_range_high = float(suggested_price + (suggested_price * buy_percentage_change))

    print stock['name'], current_price, suggested_price, suggested_price_range_low, suggested_price_range_high

    # return variable of function
    get_action = {}

    if current_price >= suggested_price and current_price <= suggested_price_range_high:
        get_action['action'] = "Buy"
        get_action['comment'] = "In High Range"
    elif current_price <= suggested_price and current_price >= suggested_price_range_low:
        get_action['action'] = "Buy"
        get_action['comment'] = "In Low Range"
    elif current_price <= suggested_price_range_low:
        get_action['action'] = "Buy"
        get_action['comment'] = "Market Corrected"

    # Remember size of get_action will be 0 if the stocks fails to qualify for either buy or sell
    return get_action

def prepare_mail(buy_stock_list, sell_stock_list):
    str = "\n"

    # BUY
    if len(buy_stock_list) == 0:
        str += "No Buy Today\n"
    else:
        str += "###############\n"
        str += "#### BUY ######\n"
        str += "###############\n\n"
        for s in buy_stock_list:
            str += s['stock_name'] + " : " + s['action_comment'] + " : " + s['comment'] + "\n"

    str += "\n-----------------------\n\n"
    # SELL
    if len(sell_stock_list) ==  0:
        str += "No Sell Today\n"
    else:
        print "TODO: ADD SELL Logic"
    print str

def iterate_over_stocks(stocks):
    buy_result = []
    sell_result = {}

    for stock in stocks:
        relevant_data = get_relevant_data_from_url(stock['url'])
        action_data   = get_buy_sell_action(stock, relevant_data)

        if len(action_data) > 0:
            if(stock['buy_status'] == "Active" and action_data['action'] == "Buy"):
                buy_stock = {}
                buy_stock['stock_name']     = stock['name']
                buy_stock['comment']        = stock['comment']
                buy_stock['action_comment'] = action_data['comment']
                buy_result                  = buy_result + [buy_stock]
            elif(action_data['action'] == "Sell"):
                print "# TO ADD SELL Logic"

    prepare_mail(buy_result, sell_result)

# Enable cron job
# Enable Sending push notification or Email
# Add if else in case the company is not listed in NSE - Example: JK Agri Genetics Ltd -
# Add Json comment in future for JH Agri : You can book some profit above 2000 and keep rest of the shares for further gain. Still there is huge growth potential in next 4- 5 years
# To Add existing stocks in the json file

if __name__ == "__main__":
    with open("./stocks.json", "r") as read_file:
        stocks = json.load(read_file)
    iterate_over_stocks(stocks)
