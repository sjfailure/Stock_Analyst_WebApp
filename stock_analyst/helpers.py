import datetime
import json
import logging
import os
import pprint
import re

import django.core.exceptions
import httpx

import requests
from asgiref.sync import sync_to_async
from django.db import DataError

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

def add_company_to_table(company_name:str, company_symbol: str):
    x = Companies.objects.create(company_name=company_name,
                         symbol=company_symbol,
                        )
    x.save()
    return

def add_date_to_table(date:str):
    if type(date) is not type('string'):
        raise TypeError(f'date must be a string, not {type(date)}')
    if not re.match(r'[0-2][0-9]{3}-[0|1][0-9]-[0-3][0-9]', date):
        raise django.core.exceptions.ValidationError(f'invalid date format, expecting YYYY-MM-DD, got {date}')
    x = Dates.objects.create(date=date)
    x.save()
    return

def add_time_series_daily_datapoint(datapoint, company_instance, date_instance): # dict object
    if type(company_instance) is not type(get_company_instance_by_symbol('GOOG')):
        raise TypeError(f"company_instance must be instance of Companies "
                         f"DB({type(get_company_instance_by_symbol('IBM'))}, not {type(company_instance)}")
    if type(date_instance) is not type(get_date_instance_by_date(get_latest_entry_date_in_datapoints())):
        raise TypeError(f"date_instance must be instance of Dates"
                         f"DB({type(get_date_instance_by_date(get_latest_entry_date_in_datapoints()))}, "
                         f"not {type(date_instance)}")
    for entry in datapoint:
        if entry not in ["1. open", "2. high", "3. low", "4. close","5. volume"]:
            raise DataError(f'unexpected datapoint value={entry}, datapoint[{entry}]={datapoint[entry]}')
        logging.debug(f'add_time_series_daily_datapoint(): data checkup loop: entry={entry}, datatype of datapoint[entry]={type(datapoint[entry])}')
        # TODO alter defense test to accept int or float as str as well
        # if type(datapoint[entry]) is not type(1) and type(datapoint[entry]) is not type(1.23456):
        #     raise DataError(f'unexpected value type for datapoint entry {entry},  datapoint[{entry}]={datapoint[entry]},'
        #                     f' type: {type(datapoint[entry])}')
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

def detail_build(company_id):
    company_info = get_company_instance_by_id(company_id)
    page_data = {'company_id': company_info.id, 'company_name': company_info.company_name}
    return page_data

# def detail_view_data_collector(company_id, category_id, period):
#     if not isinstance(company_id, int) or company_id <= 0:
#         raise ValueError("Invalid company ID provided.")
#
#     if period is None:
#         raise ValueError("Invalid period ID provided.")
#
#     category_map = {1: 'high', 2: 'low', 3: 'open', 4: 'close', 5: 'volume'}
#     category = category_map.get(category_id)
#     if category is None:
#         raise ValueError("Invalid category ID provided.")
#     data = None
#
#     if period == 7 or period == 30:
#         number_of_entries = 7
#         if period == 30:
#             number_of_entries = 31
#         data = (
#             Datapoints.objects
#             .filter(company_id_id=company_id)
#             .select_related('date')  # Assuming 'date' is the related field name
#             .order_by('-date__date')  # Assuming 'date' is the related model's field
#             [:number_of_entries]  # Limit the number of entries
#         )
#     elif period == 365 or period == 5 or period == 10:
#         data = []
#         modifier = 15
#         static = 365
#         company_instance = get_company_instance_by_id(company_id)
#         if period == 5:
#             modifier = 90
#             static = period = 5 * 365
#         elif period == 10:
#             modifier = 180
#             static =  period = 10 * 365
#         while period >= modifier:
#             datapoint_date = datetime.date.today() - datetime.timedelta(days=static - period)
#             if is_date_in_db(datapoint_date.isoformat()):
#                 date_instance = get_date_instance_by_date(datapoint_date.isoformat())
#                 data.append(get_datapoint_by_date_and_company_instances(company_instance, date_instance))
#             else:
#                 data.append(find_nearest_datapoint(datapoint_date, company_instance))
#             period -= modifier
#
#     output = {}
#     for datapoint in data:
#         # Fetch the Dates instance corresponding to the date
#         date_instance = datapoint.date  # Adjust this line as needed
#         value = getattr(datapoint, category)
#         output.setdefault(
#             date_instance.date.strftime(format='%m/%d/%y'),
#             {category: value, 'date': date_instance.date.strftime(format='%m/%d/%y')}
#         )
#     return output

def find_nearest_datapoint(date: datetime.date, company_instance):
    modifier = 1
    while modifier < 8:
        test_up = date + datetime.timedelta(days=modifier)
        test_down = date - datetime.timedelta(days=modifier)
        if is_date_in_db(test_up.isoformat()):
            test_date = get_date_instance_by_date(test_up.isoformat())
            if is_datapoint_in_db(company_instance=company_instance, date_instance=test_date):
                return get_datapoint_by_date_and_company_instances(company_instance, test_date)
        if is_date_in_db(test_down.isoformat()):
            test_date = get_date_instance_by_date(test_down.isoformat())
            if is_datapoint_in_db(company_instance=company_instance, date_instance=test_date):
                return get_datapoint_by_date_and_company_instances(company_instance, test_date)
        modifier += 1
    raise AssertionError(f'In attempting to find the nearest datapoint to {date.isoformat()} in DB for '
                         f'{company_instance.symbol}, find_nearest_datapoint() came up with nothing within 7 days.')

def get_company_id_by_symbol(symbol: str):
    return Companies.objects.get(symbol=symbol).id

def get_company_instance_by_id(id: int):
    return Companies.objects.get(id=id)

def get_company_instance_by_symbol(symbol: str):
    if type(symbol) is not type('str'):
        raise TypeError(f'symbol input must be a string, not {type(symbol)}')
    return Companies.objects.get(symbol=symbol)

def get_date_instance_by_date(date: str):
    return Dates.objects.get(date=date)

def get_datapoint_by_date_and_company_instances(company_instance, date_instance):
    return Datapoints.objects.get(date=date_instance, company_id=company_instance)

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

def get_latest_entry_date_in_datapoints():
    logging.debug(f'get_latest_entry_date_in_datapoints(): start of function, full dataset in datapoints={[entry for entry in Datapoints.objects.all()]}')
    query = """SELECT stock_analyst_datapoints.*, stock_analyst_dates.date AS date_joined
               FROM stock_analyst_datapoints
               JOIN stock_analyst_dates ON stock_analyst_datapoints.date_id = stock_analyst_dates.id
               ORDER BY stock_analyst_dates.date DESC"""
    latest_entry = Datapoints.objects.raw(query)
    if not latest_entry:
        return '1900-01-01'
    return latest_entry[0].date_joined

def is_company_in_db_by_symbol(symbol: str):
    logging.debug(f'is_company_in_db_by_symbol(): start of function, input: symbol={symbol}')
    if type(symbol) is not type('str'):
        raise TypeError(f'symbol must be string object, not {type(symbol)}')
    logging.debug(f'is_company_in_db_by_symbol(): input={symbol}, results of '
                    f'Companies.objects.filter(symbol={symbol}={Companies.objects.filter(symbol=symbol)} --- vs.  all()={Companies.objects.all()}')
    if Companies.objects.filter(symbol=symbol):
        return True
    return False

def is_datapoint_in_db(company_instance, date_instance):
    if Datapoints.objects.filter(company_id=company_instance, date=date_instance):
        return True
    return False

def is_date_in_db(date: str):
    if type(date) is not type('string'):
        raise TypeError(f'date must be a string, not {type(date)}')
    if not re.match(r'[0-2][0-9]{3}-[0|1][0-9]-[0-3][0-9]', date):
        raise django.core.exceptions.ValidationError(f'invalid date format, expecting YYYY-MM-DD, got {date}')
    if Dates.objects.filter(date=date):
        return True
    return False

def main_data_collector():
    json_data = {}
    for company in companies:
        logging.debug(f'main_data_collecter(): attempting call for company={company}')
        if not is_company_in_db_by_symbol(company):
            add_company_to_table(companies[company], company)
        company_data = get_company_instance_by_symbol(company)
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

def make_api_call(company_symbol:str):
    logging.debug(f'gathering data for {company_symbol}')
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

def should_api_call_be_made(company_symbol=None):
    if company_symbol is None:
        latest_entry = get_latest_entry_date_in_datapoints()
        return datetime.date.today() - datetime.date.fromisoformat(str(latest_entry)) > datetime.timedelta(days=1)
    elif type(company_symbol) is not type('str'):
        raise TypeError(f'company_symbol must be None or string, not {type(company_symbol)}')
    else:
        latest_entry = get_latest_entry_date_for_a_company_in_datapoints(company_symbol)
        logging.warning(f'should_api_call_be_made(): examining for {company_symbol}, latest_entry={latest_entry, type(latest_entry)}')
        if latest_entry is None:
            return True
        else:
            return datetime.date.today() - datetime.date.fromisoformat(str(latest_entry)) > datetime.timedelta(days=1)

def update_model():
    if USE_REAL_DATA:
        for company in companies:
            if should_api_call_be_made(company):
                logging.debug(f'update_model(): decision was made to update for {company}')
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





# def is_data_stale(company_id=None, company_instance=None):
#     logging.error(f"is_data_stale(): incoming params - company_id={company_id}, company_instance={company_instance}")
#     if company_instance is None and company_id is None:
#         raise ValueError(f'is_data_stale(), must set either company_id value or company_instance_value')
#     logging.error(f"is_data_stale(): accepted inputs, both not None")
#     if company_instance is None:
#         company_instance = get_company_instance_by_id(company_id)
#         logging.error(f"is_data_stale(): gathering company_instance from id, (company_instance, type(company_instance))={company_instance, type(company_instance)}")
#     if type(company_instance) != type(Companies.objects.get(id=1)):
#         raise TypeError(f"Type for company_instance must be {type(Companies.objects.get(id=1))}, not {type(company_instance)}")
#     latest_datapoint = get_latest_datapoint_by_company_id(company_instance)
#     if not latest_datapoint:
#         return True
#     return datetime.date.today() - latest_datapoint.date_string > datetime.timedelta(days=1)
#
#


#

#

#
# def set_Companies_last_api_refresh(company: Companies, date: Dates):
#     company.last_api_refresh = date
#     company.save()
#     return
#
# def get_date_instance_by_id(id: int):
#     return Dates.objects.get(id=id)
#
#

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
#         logging.debug(
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
#             logging.debug(
#                 msg=f'helpers.py.get_data_from_api() data_point={data_point, type(data_point)}, to pass on as json_object')
#             add_times_series_daily_datapoint(data_point)
#
#
# def get_date_id_instance(target_date):
#     x = Dates.objects.get(date=target_date)
#     return x
#
#
# def get_company_id_instance_by_symbol(symbol):
#     # logging.debug(f'get_company_id_instance_by_symbol(): getting for symbol={symbol}')
#     x = Companies.objects.get(symbol=symbol)
#     return x
#
#

def detail_view_data_collector(company_id, category_id, period):
    """New attempt to rewrite detail_view_data_collector() to improve performance. """
    x = datetime.datetime.now()
    logging.warning(f'start of detail_view_data_collector(): current time = {str(x)}')
    period_calculations = {7: 7, 30: 31, 365: 365, 5: 5*365, 10: 10*365}
    data_dump = Datapoints.objects.filter(
        company_id=company_id,
        date__date__gte=datetime.date.today() - datetime.timedelta(days=period_calculations[period])
    ).order_by('-date__date')
    y = datetime.datetime.now()
    logging.warning(f'middle of detail_view_data_collector(): time since start = {str(y - x)}')
    return_data = package_json_data(data_dump, category_id)
    logging.warning(f'end of detail_view_data_collector(): DB call time:{str(y - x)} -- data_packaging time: {str(datetime.datetime.now() - y)}')
    return return_data

category_map = {1: 'high', 2: 'low', 3: 'open', 4: 'close', 5: 'volume'}

def package_json_data(data, category_id):
    x = datetime.datetime.now()
    logging.warning(f'start of package_json_data(): start time: {str(x)}')
    output = {}
    category = category_map[category_id]
    y = datetime.datetime.now()
    logging.warning(f'middle of package_json_data(): time since start: {str(y - x)}')
    for datapoint in data:
        # Fetch the Dates instance corresponding to the date
        # date_instance = datapoint.date  # Adjust this line as needed
        value = getattr(datapoint, category)
        formatted_date = datapoint.date.date.strftime(format='%m/%d/%y')
        output[formatted_date] = {category: value, 'date': formatted_date}
    logging.warning(f'end of package_json_data(): time from start: {str(datetime.datetime.now() - x)} -- time from loop start: {str(datetime.datetime.now() - y)}')
    return output