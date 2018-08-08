import json
import requests
import datetime
import smtplib
import base64

from bs4 import BeautifulSoup

def get_relevant_data_from_url(stock_url):
    page = requests.get(stock_url)
    soup = BeautifulSoup(page.text, 'html.parser')

    # return variable of function
    get_relevant_data = {}

    # Get current Price
    # If NSE not found, find BSE Ex: https://www.moneycontrol.com/india/stockpricequote/fertilisers/jkagrigenetics/JKA03

    if len(list(soup.find_all(id="Nse_Prc_tick"))) > 0:
        get_relevant_data['current_price'] = soup.find_all(id="Nse_Prc_tick")[0].string.strip()
    else:
        get_relevant_data['current_price'] = soup.find_all(id="Bse_Prc_tick")[0].string.strip()

    # todo: Get other get_relevant data of iterate_over_stocks in future to add more metrics

    # return
    return get_relevant_data


# TO DO Change return variable and create two different variable
# Todo: Change comment name
def get_buy_sell_action(stock, get_relevant_data):
    current_price = float(get_relevant_data['current_price'])
    suggested_price = float(stock['suggested_price'])
    buy_percentage_change = float(stock['buy_percentage_change'])

    suggested_price_range_low = float(suggested_price - (suggested_price * buy_percentage_change))
    suggested_price_range_high = float(suggested_price + (suggested_price * buy_percentage_change))

    #print stock['name'], current_price, suggested_price, suggested_price_range_low, suggested_price_range_high

    # return variable of function
    get_action = {}

    # Buy Logic
    if current_price >= suggested_price and current_price <= suggested_price_range_high:
        get_action['action'] = "Buy"
        get_action['comment'] = "In High Range"
    elif current_price <= suggested_price and current_price >= suggested_price_range_low:
        get_action['action'] = "Buy"
        get_action['comment'] = "In Low Range"
    elif current_price <= suggested_price_range_low:
        get_action['action'] = "Buy"
        get_action['comment'] = "Market Corrected"

    # Sell Logic
    target_price = float(stock['target_price'])
    sell_percentage_change= float(stock['sell_percentage_change'])
    sell_price_range_low = float(target_price - (target_price * sell_percentage_change))
    sell_price_range_high = float(target_price + (target_price * sell_percentage_change))

    if current_price >= target_price and current_price >= sell_price_range_high:
        get_action['action'] = "Sell"
        get_action['comment'] = "Market SuperHigh"
    elif current_price >= target_price and current_price <= sell_price_range_high:
        get_action['action'] = "Sell"
        get_action['comment'] = "In High Range"
    elif current_price <= target_price and current_price >= sell_price_range_low:
        get_action['action'] = "Sell"
        get_action['comment'] = "In Low Range"

    # Remember size of get_action will be 0 if the stocks fails to qualify for either buy or sell
    return get_action

def send_mail(msg):
    with open("./emails.json", "r") as read_file:
        email = json.load(read_file)
    server = smtplib.SMTP(email['server'], email['port'])
    server.starttls()
    server.login(email['from'], base64.b64decode(email['password']))

    print "Sending Mail"
    server.sendmail(email['from'], email['to'], msg)
    server.quit()

def prepare_mail(buy_stock_list, sell_stock_list):
    now = datetime.datetime.now()
    str = "Date and Time: " + now.strftime("%d-%m-%Y %H:%M") + "\n\n"

    checker  = False

    # BUY
    if len(buy_stock_list) == 0:
        str += "No Buy Today\n"
    else:
        checker = True
        str += "#### BUY ######\n\n"
        for s in buy_stock_list:
            str += s['stock_name'] + " : " + s['action_comment'] + " : " + s['comment'] + "\n"

    str += "\n-----------------------\n\n"

    # SELL
    if len(sell_stock_list) ==  0:
        str += "No Sell Today\n"
    else:
        checker = True
        str += "#### SELL #####\n\n"
        for s in sell_stock_list:
            str += s['stock_name'] + " : " + s['action_comment'] + " : " + s['comment'] + "\n"

    if checker:
        send_mail(str)

    print str

def iterate_over_stocks(stocks):
    buy_result = []
    sell_result = []

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
            elif(stock['sell_status'] == "Active" and action_data['action'] == "Sell"):
                sell_stock = {}
                sell_stock['stock_name']     = stock['name']
                sell_stock['comment']        = stock['comment']
                sell_stock['action_comment'] = action_data['comment']
                sell_result                  = sell_result + [sell_stock]

    prepare_mail(buy_result, sell_result)

# Enable cron job
# Enable Sending push notification or Email
# To Add existing stocks in the json file

if __name__ == "__main__":
    with open("./stocks.json", "r") as read_file:
        stocks = json.load(read_file)
    iterate_over_stocks(stocks)
