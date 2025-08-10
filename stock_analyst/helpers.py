import datetime
import json
import logging
import os

import requests

from . import models
from .models import Companies, Dates, Datapoints

site = f'https://www.alphavantage.co/query'
function_mode = 'TIME_SERIES_DAILY'
companies = {
    'IBM': "IBM",
    'AAP': "Advanced Auto Parts",
    'AAPL': "Apple",
    'AMD': "AMD",
    'AMZN': "Amazon",
    'INTC': "Intel Corp.",
    'MSFT': "Microsoft",
    'GOOG': "Google",
    'NVDA': "Nvidia",
}
api_key = os.environ.get('alpha_vantage_api_key')
# with open('stock_analyst/model/apikey', 'r') as file:
#     api_key = file.read()
last_update = datetime.date(year=1900, day=1, month=1)
with open('stock_analyst/model/last_update', 'r') as file:
    date_info = file.read()
    last_update = datetime.date.fromisoformat(date_info)
if not last_update:
    last_update = datetime.date(1900, 1, 1)
else:
    last_update = datetime.date.fromisoformat('1900-01-01')

def get_practice_data():
    mock_api_data = []
    for file in ['query.json', 'query1.json', 'query2.json']:
        with open(f'stock_analyst/model/{file}', 'r') as data:
            mock_api_data.append(json.load(data))
    for data_cache in mock_api_data:
        add_times_series_daily_datapoint((data_cache))

def get_data_from_api(complete=False):
    if datetime.date.today() - last_update > datetime.timedelta(days=1):
        with open("stock_analyst/model/last_update", 'w') as file:
            file.write(str(datetime.date.today()))
        for data_point in get_all_company_tsd_data(complete=complete):
            logging.debug(msg=f'main.py, data_point={data_point, type(data_point)}, to pass on as json_object')
            add_times_series_daily_datapoint(data_point)

def get_date_id_instance(target_date):
    x = Dates.objects.get(date=target_date)
    return x

def get_company_id_instance_by_symbol(symbol):
    # logging.warning(f'get_company_id_instance_by_symbol(): getting for symbol={symbol}')
    x = Companies.objects.get(symbol=symbol)
    return x

def add_times_series_daily_datapoint(json_data):
    company_symbol = json_data["Meta Data"]["2. Symbol"]
    if not company_symbol in companies:
        logging.warning(f'get_practice_data(): symbol {company_symbol} not in companies dict.')
        companies.setdefault(company_symbol, None)
    if not Companies.objects.filter(symbol=company_symbol):
        new_company_entry = Companies(
            symbol=company_symbol,
            company_name=companies[company_symbol]
        )
        new_company_entry.save()
    for activity_date in json_data["Time Series (Daily)"]:
        if not Dates.objects.filter(date=activity_date):
            new_date_entry = Dates(
                date=activity_date
            )
            new_date_entry.save()
        if not Datapoints.objects.filter(
                date=get_date_id_instance(activity_date),
                company_id=get_company_id_instance_by_symbol(company_symbol)
        ):
            new_datapoint = Datapoints(
                date=get_date_id_instance(activity_date),
                company_id=get_company_id_instance_by_symbol(company_symbol),
                open=json_data["Time Series (Daily)"][activity_date]["1. open"],
                close=json_data["Time Series (Daily)"][activity_date]["4. close"],
                high=json_data["Time Series (Daily)"][activity_date]["2. high"],
                low=json_data["Time Series (Daily)"][activity_date]["3. low"],
                volume=json_data["Time Series (Daily)"][activity_date]["5. volume"],
            )
            new_datapoint.save()
    return

def main_data_collector():
    json_data = {}
    for company in companies:
        # logging.debug(f'main_data_collecter(): attempting call for company={company}')
        company_data = get_company_id_instance_by_symbol(company)
        data = get_latest_datapoint_by_company_id(company_data)
        json_data.setdefault(company, {'high':data.high,
                                       'company_name': company_data.company_name,
                                       'abbreviation': company
                                       }
                             )
    return json_data

def get_latest_datapoint_by_company_id(company_id_instance):
    query = "SELECT * FROM stock_analyst_datapoints WHERE company_id_id=%s ORDER BY date_id DESC"
    params = [company_id_instance.id,]
    return Datapoints.objects.raw(query, params)[0]

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
            # save_to_file(data.json(), f'{company.lower()}_data.json')
            yield data.json()
        else:
            raise ValueError(f'API data requisition failed, symbol({company}), status code and response: {data.status_code, data.text}')
