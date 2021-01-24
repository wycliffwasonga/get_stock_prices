from tabulate import tabulate
from datetime import datetime
from io import StringIO
import requests
import argparse
import csv
import os

def tidy_response(csvstring):
    prices = []

    input = StringIO(csvstring)

    reader = csv.reader(input, delimiter=',')

    next(reader, None) # skip the header
    for row in reader:
        price = {
            "date": datetime.strptime(row[0], "%Y-%m-%d").strftime('%d/%m/%Y'),
            "close": row[4]
            }
        prices.append(price)
    
    return prices

def get_stock_prices(symbol, region, time_period_start, time_period_end):
    url = 'https://query1.finance.yahoo.com/v7/finance/download/{}'.format(symbol)

    querystring = {
        "period1": time_period_start.strftime('%s'),
        "period2": time_period_end.strftime('%s'),
        "interval": "1d",
        "events": "history"
        }

    response = requests.request("GET", url, params=querystring)

    return tidy_response(response.text)

def valid_date(s):
    try:
        return datetime.strptime(s, "%d/%m/%Y")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


# Construct the argument parser
ap = argparse.ArgumentParser()

# Add the arguments to the parser
ap.add_argument("-s",
                "--symbol",
                required=True,
                help="Ticker symbol")
ap.add_argument("-r",
                "--region",
                required=False,
                help="Region",
                default="US")
ap.add_argument("-f",
                "--from",
                required=True,
                type=valid_date,
                help="Time period start - format dd/mm/yyyy")
ap.add_argument("-t",
                "--to",
                required=True,
                type=valid_date,
                help="Time period end - format dd/mm/yyyy")

args = vars(ap.parse_args())

symbol = args["symbol"]
region = args["region"]
time_period_start = args["from"]
time_period_end = args["to"]

prices = get_stock_prices(symbol, region, time_period_start, time_period_end)

print(tabulate(prices, headers="keys", tablefmt="github"))
