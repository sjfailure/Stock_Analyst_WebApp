import logging
# import sqlite3
import os
import pprint
import sqlite3
from http.client import responses
from pathlib import Path

from django.db import connection

from django.db.models.functions import JSONObject

db_name = os.path.join(Path(__file__).resolve().parent.parent, "model/stock_data_db.db")

company_names = {
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

create_table_query = 'CREATE TABLE DataPoints (' + \
                     'id INTEGER NOT NULL, ' \
                     'company_id INTEGER NOT NULL, ' + \
                     'date INTEGER, ' + \
                     'open REAL, ' + \
                     'close REAL, ' + \
                     'high REAL, ' + \
                     'low REAL, ' + \
                     'volume REAL, ' + \
                     'PRIMARY KEY(id), ' + \
                     'FOREIGN KEY(company_id) REFERENCES Companies(id), ' + \
                     'FOREIGN KEY(date) REFERENCES Dates(id)' + \
                     ');'
create_table_query2 = ('CREATE TABLE Companies(' +
                       'id INTEGER NOT NULL,' +
                       'symbol TEXT,' +
                       'company_name TEXT,' +
                       'PRIMARY KEY(id)' +
                       ');')
# create_table_query3 = 'CREATE TABLE CompanyNames(' + \
#                       'id INTEGER NOT NULL, ' + \
#                       'name TEXT, ' + \
#                       'PRIMARY KEY(id)' + \
#                       ');'
create_table_query4 = 'CREATE TABLE Dates(' + \
                      'id INTEGER NOT NULL,' + \
                      'date TEXT UNIQUE,' + \
                      'PRIMARY KEY(id)' + \
                      ');'
create_table_query5 = 'ALTER TABLE DataPoints ADD CONSTRAINT fk_date_to_dates FOREIGN KEY(date) REFERENCES Dates(id);'




def create_db(db_url=db_name):
    logging.debug(f'TEST: create_db to:{db_url}')
    logging.info('database does not exist, creating')
    cur = connection.cursor()
    logging.debug(msg=f'executing query: {create_table_query}')
    cur.execute(create_table_query)
    logging.debug(msg='create_table_query done')
    logging.debug(msg=f'executing query: {create_table_query2}')
    cur.execute(create_table_query2)
    logging.debug(msg='create_table_query2 done')
    # logging.debug(msg=f'executing query: {create_table_query3}')
    # cur.execute(create_table_query3)
    logging.debug(msg='table_query3 obsolete')
    logging.debug(msg=f'executing query: {create_table_query4}')
    cur.execute(create_table_query4)
    logging.debug(msg='create_table_query4 done')
    logging.debug(msg=f'executing query: {create_table_query5}')
    # conn.close()
    return

# def get_conn(db_url=db_name):
#     if not os.path.exists(db_url):
#         create_db()
#     conn = connection.connect(db_url)
#     return conn
#
# def get_cursor(conn=None):
#     if conn is None:
#         conn = get_conn()
#     cur = conn.cursor()
#     return cur

def check_db(query, db=db_name):
    def check_table_exists(table_name):
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=%s", [table_name])
            output = cursor.fetchone()
            logging.debug(f'DatabaseAdmin.check_db.check_table_exists(), output={output}')
            return output[0] > 0

    if not os.path.isfile(db):
        create_db()
        return
    query_table = None
    next_token = False
    for token in query.split():
        if next_token:
            query_table = token
            break
        elif token.upper() is "FROM" or token.upper() is "INTO":
            next_token = True
    if not check_table_exists(query_table):
        create_db()
    return


def select_query(query, parameterized_data=None):
    check_db(query)
    db_cursor = connection.cursor()
    if parameterized_data is None:
        results = db_cursor.execute(query)
    else:
        # parameterized_data = [str(i) for i in parameterized_data]
        logging.debug(f'DatabaseAdmin.select_query() query={query}, '
                      f'parameterized_data={parameterized_data}')
        results = db_cursor.execute(query, parameterized_data)
    output = results.fetchall()
    return output

def insert_query(query, parameterized_data=None):
    check_db(query)
    cursor = connection.cursor()
    logging.info(f'executing query: {query}')
    if parameterized_data is None:
        cursor.execute(query)
    else:
        # parameterized_data = [str(i) for i in parameterized_data]
        logging.debug(f'insert_query(), parameterized_data found, query={query}, '
                      f'parameterized_data={parameterized_data, type(parameterized_data)}')
        cursor.execute(query, parameterized_data)
    return

def add_time_series_daily_entry(json_obj):
    # Get the company symbol
    symbol = get_symbol_from_raw_json(json_obj)
    # Find or Assign an company_id
    company_id = get_company_id_by_symbol(symbol)
    # for each day's worth of data:
    for date in json_obj["Time Series (Daily)"]:
        # Find or Assign a date_id
        date_id = get_date_id(date)
        # Check that record does not already exist, if not:
        logging.debug(f'DatabaseAdmin.add_time_series_daily_entry(), json_obj (before parsing)={json_obj}')
        if not does_record_exist(company_id, date_id):
            insert_Datapoints_record(company_id,
                                     date_id,
                                     open=json_obj["Time Series (Daily)"][date]['1. open'],
                                     close=json_obj["Time Series (Daily)"][date]["4. close"],
                                     high=json_obj["Time Series (Daily)"][date]["2. high"],
                                     low=json_obj["Time Series (Daily)"][date]["3. low"],
                                     volume=json_obj["Time Series (Daily)"][date]["5. volume"],
                                     )
            logging.debug(f'DatabaseAdmin.add_time_series_daily_entry() - added date for '
                          f'{(symbol, company_id)} for {(date, date_id)}')
            # Perform Insert Query (INSERT INTO Datapoints (company_id, date, open, close, high, low, volume)
            #                       VALUES (?, ?, ?, ?, ?, ?, ?)
        # else: Continue, maybe Break even (no need to rehash old data)?????

    return

def get_symbol_from_raw_json(json_obj):
    logging.debug(f'DatabaseAdmin.get_symbol_from_raw_json(), json_obj={json_obj}')
    return str.upper(json_obj["Meta Data"]["2. Symbol"])

def get_company_id_by_symbol(symbol):
    company_id = is_company_in_Companies(symbol)
    logging.debug(f'DatabaseAdmin.get_company_id_by_symbol(), company_id={company_id}')
    if company_id:
        return company_id
    else:
        insert = "INSERT INTO Companies (symbol, company_name) VALUES (%s, %s)"
        company_name = None
        if not symbol in company_names:
            logging.warning(f"DatabaseAdmin: get_company_id_by_symbol; company '{symbol}' "
                            f"not included in company_names dictionary.")
        else:
            company_name = company_names[symbol]
        insert_query(insert, parameterized_data=[symbol, company_name])
        response = is_company_in_Companies(symbol)
        return response

def is_company_in_Companies(symbol):
    response = select_query("SELECT id FROM Companies WHERE symbol=%s", [symbol,])
    if response:
        return response[0][0]
    else:
        return False

def get_date_id(date):
    response = select_query("SELECT id FROM Dates WHERE Date=%s", [date,])
    if response:
        return response[0][0]
    else:
        insert = "INSERT INTO Dates (date) VALUES (%s)"
        insert_query(insert, parameterized_data=[date,])
        response = select_query("SELECT id FROM Dates WHERE Date=%s", [date, ])
        return response[0][0]

def does_record_exist(company_id, date_id):
    response = select_query("SELECT * from Datapoints "
                                  "WHERE company_id=%s AND date=%s", [company_id, date_id,])
    return response

def insert_Datapoints_record(company_id, date_id, open=None, close=None, high=None, low=None, volume=None):
     insert_query("INSERT INTO Datapoints (company_id, date, open, close, high, low, volume)"
                  "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                  parameterized_data=[company_id, date_id, open, close, high, low, volume,])
     return

def check_data_point_exists(cursor, table_name, column_name, value):
    """
    Checks if a data point exists in a table based on a specific column and value.

    Args:
        cursor: A cursor object from your sqlite3 connection.
        table_name: The name of the table to search.
        column_name: The name of the column to check for the value.
        value: The value to search for.

    Returns:
        True if the data point exists, False otherwise.
    """
    query = f"SELECT EXISTS (SELECT 1 FROM {table_name} WHERE {column_name} = %s)"
    logging.debug(f'performing following query: {query} --- parameterized variable={value}')
    cursor.execute(query, (value,))
    return cursor.fetchone()[0] > 0  # Get the first element from the fetchone tuple

def get_company_id_by_name(company_name):
    logging.debug(f"TEST LOG get_company_id(): company_name={company_name}")
    query = "SELECT id FROM Companies WHERE company_name=%s"
    # answer = select_query(query, [company_name,])
    answer = select_query("SELECT id FROM Companies WHERE company_name=%s", [company_name])
    logging.debug(f'TEST LOG get_company_id(), answer = {answer}')
    if not answer:
        raise ValueError(f'Database yielded no data for query "{query}" %s="{company_name}"')
    return answer[0][0]

def get_high_with_company_id(company_id, date_id=None):
    if isinstance(date_id, list):
        answer = []
        for date in date_id:
            data = select_query("SELECT high "
                                "FROM Datapoints "
                                "WHERE company_id=%s AND date=%s", [company_id, date])
            answer.append(data[0][0])
        return answer
    elif isinstance(date_id, int):
        data = select_query("SELECT high "
                            "FROM Datapoints "
                            "WHERE company_id=%s AND date=%s", [company_id, date_id])
        return data[0][0]
    elif date_id is None:
        latest_dates = get_latest_dates_by_id()
        for date in latest_dates:
            answer = select_query("SELECT high "
                                  "FROM Datapoints "
                                  "WHERE company_id=%s AND date=%s", [company_id, date])
            if answer:
                return answer[0][0]
    else:
        raise TypeError("date_id must be int, iterable of dates, or None")

def get_latest_dates_by_id():
    dates_descending_order = []
    data = select_query("SELECT id FROM Dates ORDER BY date DESC")
    for i in range(100):
        if i >= len(data):
            break
        dates_descending_order.append(data[i][0])
    return dates_descending_order

def data_wrangling_for_main():
    """Prepares a nested set of dictionary objects for use with the stock_analyst.views.main function.
    Schema : {company_name: {most_recent_high[float]}"""
    # TODO Add character limit so that company_name does not exceed space limit (or switch between abbreviation and
    #  full name where appropriate). *Might be best handled on front end.*
    json_data_prep = {}
    for company in company_names:
        company_id = get_company_id_by_name(company_names[company])
        high_value = get_high_with_company_id(company_id)
        json_data_prep.setdefault(company_names[company],
                                  {'company_name': company_names[company], 'high':high_value, 'abbr': company})
    return json_data_prep
