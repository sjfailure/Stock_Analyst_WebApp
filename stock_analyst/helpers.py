import datetime
import json
import logging
import os
import pprint
import httpx

import requests
from asgiref.sync import sync_to_async
# from django.channels.db import database_sync_to_async

from . import models
from .models import Companies, Dates, Datapoints, Update
from mvp_stock_app.settings import USE_REAL_DATA, INITIAL_DATACOLLECTION_COMPLETE

site = f'https://www.alphavantage.co/query'
function_mode = 'TIME_SERIES_DAILY'
if USE_REAL_DATA:
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
        'OPEN': "Opendoor Technologies Inc."
    }
else:
    companies = {
        'IBM': "IBM",
        # 'AAP': "Advanced Auto Parts",
        'AAPL': "Apple",
        # 'AMD': "AMD",
        # 'AMZN': "Amazon",
        # 'INTC': "Intel Corp.",
        # 'MSFT': "Microsoft",
        'GOOG': "Google",
        # 'NVDA': "Nvidia",
    }
api_key = os.environ.get('alpha_vantage_api_key')
# with open('stock_analyst/model/apikey', 'r') as file:
#     api_key = file.read()



def should_api_call_be_made(company_symbol=None):
    if company_symbol is None:
        latest_entry = get_latest_entry_date_in_datapoints()
        return datetime.date.today() - datetime.date.fromisoformat(str(latest_entry)) > datetime.timedelta(days=1)
    else:
        latest_entry = get_latest_entry_date_for_a_company_in_datapoints(company_symbol)
        logging.warning(f'should_api_call_be_made(): examining for {company_symbol}, latest_entry={latest_entry, type(latest_entry)}')
        if latest_entry is None:
            return True
        else:
            return datetime.date.today() - datetime.date.fromisoformat(str(latest_entry)) > datetime.timedelta(days=1)
#
def get_latest_entry_date_in_datapoints():
    query = """SELECT stock_analyst_datapoints.*, stock_analyst_dates.date AS date_joined
               FROM stock_analyst_datapoints
               JOIN stock_analyst_dates ON stock_analyst_datapoints.date_id = stock_analyst_dates.id
               ORDER BY stock_analyst_dates.date DESC"""
    latest_entry = Datapoints.objects.raw(query)
    return latest_entry[0].date_joined

def get_latest_entry_date_for_a_company_in_datapoints(company_symbol):
    if not is_company_in_db_by_symbol(company_symbol):
        return None
    query = """SELECT stock_analyst_datapoints.*, stock_analyst_dates.date AS date_joined
               FROM stock_analyst_datapoints
               JOIN stock_analyst_dates ON stock_analyst_datapoints.date_id = stock_analyst_dates.id
               WHERE stock_analyst_datapoints.company_id_id = %s
               ORDER BY stock_analyst_dates.date DESC"""
    company_id = get_company_id_by_symbol(company_symbol)
    latest_entry = Datapoints.objects.raw(query, [company_id,])
    if not latest_entry:
        return None
    logging.debug(f'get_latest_entry_date_for_a_company_in_datapoints(): data gathered={latest_entry, type(latest_entry)}')
    return latest_entry[0].date_joined

def update_model():
    if USE_REAL_DATA:
        for company in companies:
            if should_api_call_be_made(company):
                logging.warning(f'update_model(): decision was made to update for {company}')
                data = make_api_call(company)
                try:
                    company_symbol = data["Meta Data"]["2. Symbol"] # Currently, just a check that JSON data returned by API
                except AttributeError as e:
                    logging.error(f'update_model(): API data incorrect: {e}')
                    continue
                if not is_company_in_db_by_symbol(company):
                    add_company_to_table(companies[company], company)
                company_instance = get_company_instance_by_symbol(company)
                # if is_data_stale(company_instance=company_instance):
                # latest_datapoint_for_company = get_latest_entry_date_for_a_company_in_datapoints(company)
                for datapoint in data["Time Series (Daily)"]:
                    if not is_date_in_db(datapoint):
                        add_date_to_table(datapoint)
                    date_instance = get_date_instance_by_date(datapoint)
                    if not is_datapoint_in_db(company_instance, date_instance):
                        add_time_series_daily_datapoint(data["Time Series (Daily)"][datapoint], company_instance, date_instance)
                    else:
                        continue
    else:
        check_company_symbol = "AAPL"
        check_date = "2024-06-14"
        if is_datapoint_in_db(get_company_instance_by_symbol(check_company_symbol), get_date_instance_by_date(check_date)):
            return
        else:
            for file in ['query.json', 'query1.json', 'query2.json']:
                with open(f'stock_analyst/model/{file}', 'r') as data:
                    data_cache = json.load(data)
                    if not is_company_in_db_by_symbol(data_cache["Meta Data"]["2. Symbol"]):
                        company_symbol = data_cache["Meta Data"]["2. Symbol"]
                        add_company_to_table(companies[company_symbol], company_symbol)
                    company_instance = get_company_instance_by_symbol(company_symbol)
                    for datapoint in data_cache["Time Series (Daily)"]:
                        if not is_date_in_db(datapoint):
                            add_date_to_table(datapoint)
                        date_instance = get_date_instance_by_date(datapoint)
                        if not is_datapoint_in_db(company_instance, date_instance):
                            add_time_series_daily_datapoint(data_cache["Time Series (Daily)"][datapoint], company_instance, date_instance)


#
#
def add_time_series_daily_datapoint(datapoint, company_instance, date_instance): # dict object
    x = Datapoints.objects.create(company_id=company_instance,
                      date=date_instance,
                      open=datapoint["1. open"],
                      high=datapoint["2. high"],
                      low=datapoint["3. low"],
                      close=datapoint["4. close"],
                      volume=datapoint["5. volume"],
                      )
    x.save()
    return

def add_company_to_table(company_name:str, company_symbol: str):
    x = Companies.objects.create(company_name=company_name,
                         symbol=company_symbol,
                        )
    x.save()
    return

def add_date_to_table(date:str):
    x = Dates.objects.create(date=date)
    x.save()
    return


def is_data_stale(company_id=None, company_instance=None):
    logging.error(f"is_data_stale(): incoming params - company_id={company_id}, company_instance={company_instance}")
    if company_instance is None and company_id is None:
        raise ValueError(f'is_data_stale(), must set either company_id value or company_instance_value')
    logging.error(f"is_data_stale(): accepted inputs, both not None")
    if company_instance is None:
        company_instance = get_company_instance_by_id(company_id)
        logging.error(f"is_data_stale(): gathering company_instance from id, (company_instance, type(company_instance))={company_instance, type(company_instance)}")
    if type(company_instance) != type(Companies.objects.get(id=1)):
        raise TypeError(f"Type for company_instance must be {type(Companies.objects.get(id=1))}, not {type(company_instance)}")
    latest_datapoint = get_latest_datapoint_by_company_id(company_instance)
    if not latest_datapoint:
        return True
    return datetime.date.today() - latest_datapoint.date_string > datetime.timedelta(days=1)
#
#
def is_company_in_db_by_symbol(symbol: str):
    if Companies.objects.filter(symbol=symbol):
        return True
    return False

#
def get_company_id_by_symbol(symbol: str):
    return Companies.objects.get(symbol=symbol).id
#
def get_company_instance_by_symbol(symbol: str):
    return Companies.objects.get(symbol=symbol)
#
def get_company_instance_by_id(id: int):
    return Companies.objects.get(id=id)
#
# def set_Companies_last_api_refresh(company: Companies, date: Dates):
#     company.last_api_refresh = date
#     company.save()
#     return
#
# def get_date_instance_by_id(id: int):
#     return Dates.objects.get(id=id)
#
def is_date_in_db(date: str):
    if Dates.objects.filter(date=date):
        return True
    return False
#
def get_date_instance_by_date(date: str):
    return Dates.objects.get(date=date)
#
#
#
#

#
# def get_practice_data():
#     mock_api_data = []
#     for file in ['query.json', 'query1.json', 'query2.json']:
#         with open(f'stock_analyst/model/{file}', 'r') as data:
#             mock_api_data.append(json.load(data))
#     for data_cache in mock_api_data:
#         logging.warning(
#             f'get_practice_data(), data_cache heading to add_times_series_daily_datapoint() = \n{pprint.pprint(data_cache)}')
#         add_times_series_daily_datapoint((data_cache))
#
#
# async def get_data_from_api(complete=False):
#     now = datetime.datetime.now()
#     set_last_update_default()
#     latest_update = datetime.datetime.fromisoformat(Update.objects.all()[0].last_update)
#     if now - latest_update > datetime.timedelta(days=1):
#         Update.last_update = now
#         Update.save()
#         for data_point in get_all_company_tsd_data(complete=complete):
#             logging.warning(
#                 msg=f'helpers.py.get_data_from_api() data_point={data_point, type(data_point)}, to pass on as json_object')
#             add_times_series_daily_datapoint(data_point)
#
#
# def get_date_id_instance(target_date):
#     x = Dates.objects.get(date=target_date)
#     return x
#
#
def get_company_id_instance_by_symbol(symbol):
    # logging.warning(f'get_company_id_instance_by_symbol(): getting for symbol={symbol}')
    x = Companies.objects.get(symbol=symbol)
    return x
#
#
# def add_times_series_daily_datapoint(json_data):
#     logging.warning(f'add_times_series_daily_datapoint(): incoming json_data \n{pprint.pprint(json_data)}')
#     company_symbol = json_data["Meta Data"]["2. Symbol"]
#     # should we bother?  is the data point already present in the model?
#
#     if not company_symbol in companies:
#         logging.warning(f'get_practice_data(): symbol {company_symbol} not in companies dict.')
#         companies.setdefault(company_symbol, None)
#     if not Companies.objects.filter(symbol=company_symbol):
#         new_company_entry = Companies(
#             symbol=company_symbol,
#             company_name=companies[company_symbol]
#         )
#         new_company_entry.save()
#     for activity_date in json_data["Time Series (Daily)"]:
#         if not Dates.objects.filter(date=activity_date):
#             new_date_entry = Dates(
#                 date=activity_date
#             )
#             new_date_entry.save()
#         if not Datapoints.objects.filter(
#                 date=get_date_id_instance(activity_date),
#                 company_id=get_company_id_instance_by_symbol(company_symbol)
#         ):
#             new_datapoint = Datapoints(
#                 date=get_date_id_instance(activity_date),
#                 company_id=get_company_id_instance_by_symbol(company_symbol),
#                 open=json_data["Time Series (Daily)"][activity_date]["1. open"],
#                 close=json_data["Time Series (Daily)"][activity_date]["4. close"],
#                 high=json_data["Time Series (Daily)"][activity_date]["2. high"],
#                 low=json_data["Time Series (Daily)"][activity_date]["3. low"],
#                 volume=json_data["Time Series (Daily)"][activity_date]["5. volume"],
#             )
#             new_datapoint.save()
#     return
#
#
def main_data_collector():
    json_data = {}
    for company in companies:
        logging.debug(f'main_data_collecter(): attempting call for company={company}')
        if not is_company_in_db_by_symbol(company):
            add_company_to_table(companies[company], company)
        company_data = get_company_id_instance_by_symbol(company)
        data = get_latest_datapoint_by_company_id(company_data)
        if not data:
            continue
        logging.debug(f'main_data_collector(): data.date_string={data.date_string}, type(data.date_string)={type(data.date_string)}')
        json_data.setdefault(company, {'company_name': company_data.company_name,
                                       'company_id': company_data.id,
                                       'abbreviation': company,
                                       'high': data.high,
                                       'low': data.low,
                                       'open': data.open,
                                       'close': data.close,
                                       'volume': data.volume,
                                       'date': data.date_string.strftime(format='%m/%d/%y'),
                                       }
                             )
    return json_data


def get_latest_datapoint_by_company_id(company_id_instance):
    query = ("""SELECT stock_analyst_datapoints.*, stock_analyst_dates.date AS date_string
                FROM stock_analyst_datapoints
                JOIN stock_analyst_dates ON stock_analyst_datapoints.date_id = stock_analyst_dates.id
                WHERE stock_analyst_datapoints.company_id_id = %s
                ORDER BY stock_analyst_dates.date DESC""")
    params = [company_id_instance.id, ]
    if Datapoints.objects.raw(query, params):
        return Datapoints.objects.raw(query, params)[0]
    return False
#
#
# # TODO introduce fail safe code for failed API call
# async def get_all_company_tsd_data(complete=False):
#     for company in companies:
#         logging.warning(f'gathering data for {company}')
#         if complete:
#             data = httpx.get(url=site, params={'function': function_mode, 'symbol': company, 'outputsize': 'full',
#                                                'apikey': api_key})
#         else:
#             data = httpx.get(url=site, params={'function': function_mode, 'symbol': company, 'apikey': api_key})
#         if data.status_code == 200:
#             logging.warning(f'successful call for {company} data, {data.url}')
#             # save_to_file(data.json(), f'{company.lower()}_data.json')
#             yield data.json()
#         else:
#             raise ValueError(
#                 f'API data requisition failed, symbol({company}), status code and response: {data.status_code, data.text}')
#
#
# def get_latest_update():
#     query = "SELECT * FROM stock_analyst_dates ORDER BY date DESC"
#     latest_update = Dates.objects.raw(query)
#     if not latest_update[0]:
#         return '1900-01-01'
#     return latest_update[0].date
#
#
# def set_last_update_default():
#     if not Update.last_update:
#         Update.last_update = datetime.datetime(day=1, month=1, year=1990)
#     return
#

def is_datapoint_in_db(company_instance, date_instance):
    if Datapoints.objects.filter(company_id=company_instance, date=date_instance):
        return True
    return False

def make_api_call(company_symbol:str):
    logging.warning(f'gathering data for {company_symbol}')
    if not INITIAL_DATACOLLECTION_COMPLETE:
        data = requests.get(url=site, params={'function': function_mode,
                                           'symbol': company_symbol,
                                           'outputsize': 'full',
                                           'apikey': api_key}
                         )
    else:
        data = requests.get(url=site, params={'function': function_mode,
                                           'symbol': company_symbol,
                                           'apikey': api_key},
                        )
    if data.status_code == 200:
        logging.debug(f'successful call for {company_symbol} data, {data.url}')
        # save_to_file(data.json(), f'{company.lower()}_data.json')
        return data.json()
    else:
        raise ValueError(
            f'API data requisition failed, symbol({company_symbol}), status code and response: {data.status_code, data.text}')

def detail_build(company_id):
    company_info = get_company_instance_by_id(company_id)
    page_data = {'company_id': company_info.id, 'company_name': company_info.company_name}
    return page_data

def detail_view_data_collector(company_id, category_id, period):
    if not isinstance(company_id, int) or company_id <= 0:
        raise ValueError("Invalid company ID provided.")

    period_map = {7: 7, 30: 31, 365: 365, 5: 5 * 365, 10: 3650}
    number_of_entries = period_map.get(period)
    if period is None:
        raise ValueError("Invalid period ID provided.")

    category_map = {1: 'high', 2: 'low', 3: 'open', 4: 'close', 5: 'volume'}
    category = category_map.get(category_id)
    if category is None:
        raise ValueError("Invalid category ID provided.")

    # query = f'''SELECT {category}, date, stock_analyst_datapoints.id
    #             FROM stock_analyst_datapoints
    #             JOIN stock_analyst_dates AS date_ids
    #             ON date_ids.id = stock_analyst_datapoints.date_id
    #             WHERE stock_analyst_datapoints.company_id_id = %s
    #             ORDER BY date_ids.date DESC
    #             LIMIT %s;'''
    # data = Datapoints.objects.raw(query, [company_id, number_of_entries, ])

    # Use the ORM to fetch the data
    data = (
        Datapoints.objects
        .filter(company_id_id=company_id)
        .select_related('date')  # Assuming 'date' is the related field name
        .order_by('-date__date')  # Assuming 'date' is the related model's field
        [:number_of_entries]  # Limit the number of entries
    )

    output = {}
    for datapoint in data:
        # Fetch the Dates instance corresponding to the date
        date_instance = Dates.objects.get(date=datapoint.date.date)  # Adjust this line as needed
        value = getattr(datapoint, category)
        output.setdefault(
            date_instance.date.strftime(format='%m/%d/%y'),
            {category: value, 'date': date_instance.date.strftime(format='%m/%d/%y')}
        )
    return output
