import logging

import requests
from FetchApiKey import get_api_key
import sqlite3
import json
from jsonHandling import save_to_file

api_key = get_api_key()
site = f'https://www.alphavantage.co/query'
function_mode = 'TIME_SERIES_DAILY'
companies = ['IBM',
         'AAP',
         'AAPL',
         'AMD',
         'AMZN',
         'INTC',
         'MSFT',
         'GOOG',
         'NVDA',
             ]


def get_all_company_tsd_data(complete=False):
    for company in companies:
        logging.info(f'gathering data for {company}')
        if complete:
            data = requests.get(url=site, params={'function': function_mode, 'symbol': company, 'outputsize': 'full',
                                                  'apikey': api_key})
        else:
            data = requests.get(url=site, params={'function': function_mode, 'symbol': company, 'apikey': api_key})
        if data.status_code == 200:
            logging.info(f'successful call for {company} data, {data.url}')
            save_to_file(data.json(), f'{company.lower()}_data.json')
            yield data.json()
        else:
            raise ValueError(f'API data requisition failed, symbol({company}), status code and response: {data.status_code, data.text}')

def get_practice_data():
    output = []
    for f in ['query.json', 'query1.json', 'query2.json']:
        with open(f, 'r') as data:
            output.append(json.load(data))
    return output

# # print(r.json())
# data = r.json()
# print(list(data.keys()))
# print(list(data['Meta Data'].keys()))
# print(list(data['Time Series (Daily)'].keys()))
# print(data["Meta Data"]["1. Information"])
# print(data['Meta Data']['2. Symbol'])
# print(list(data['Time Series (Daily)']['2024-04-26'].keys()))
# print(data['Time Series (Daily)']['2024-04-26']['5. volume'])

"""
API response structure (Time Series Daily):
    {"Meta Data:
        {"1. Information", 
         "2. Symbol",
         "3. Last Refreshed",
         "4. Output Size",
         "5. Time Zone
         }
     "Time Series (Daily)": 
        {--dict, keys are YYYY-MM-DD (str)--:
            {"1. open": --value as str--,
             "2. high": --,
             "3. low": --,
             "4. close": --,
             "5. volume": --,
        }
    }
"""

# https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=demo