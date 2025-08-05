import logging
import sqlite3
import os

from django.db.models.functions import JSONObject

db_name = 'stock_data_db.db'

company_names = {
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
    logging.info('database does not exist, creating')
    conn = sqlite3.connect(db_url)
    cur = get_cursor(conn)
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
    conn.close()
    return

def get_conn(db_url=db_name):
    if not os.path.exists(db_url):
        create_db()
    conn = sqlite3.connect(db_url)
    return conn

def get_cursor(conn=None):
    if conn is None:
        conn = get_conn()
    cur = conn.cursor()
    return cur

def select_query(query, parameterized_data=None):
    db_conn = get_conn()
    db_cursor = get_cursor(db_conn)
    if parameterized_data is None:
        results = db_cursor.execute(query)
    else:
        results = db_cursor.execute(query, parameterized_data)
    output = results.fetchall()
    db_conn.close()
    return output

def insert_query(query, check_up_query=None, parameterized_data=None):
    db_conn = get_conn()
    db_cursor = get_cursor(db_conn)
    logging.info(f'executing query: {query}')
    if parameterized_data is None:
        db_cursor.execute(query)
    else:
        logging.debug(f'insert_query(), parameterized_data found, query={query}, '
                      f'parameterized_data={parameterized_data, type(parameterized_data)}')
        db_cursor.execute(query, parameterized_data)
    db_conn.commit()
    db_conn.close()
    if check_up_query is None:
        return None
    else:
        return select_query(check_up_query)

def add_time_series_daily_entry(db_cursor, json_obj):
    """
    Adds all times series daily data from a JSON object into database.
    db_cursor: specify db to target (for default, use get_cursor() function).
    json_obj: built specifically for API response from Alphavantage.co time series
        daily calls.
    output: None
    """
    # collect/generate symbol id
    symbol = json_obj['Meta Data']['2. Symbol'].upper()
    # company_name = json_obj['']
    if not check_data_point_exists(get_cursor(get_conn()), "Companies", "symbol", symbol):
        insert_query(f"INSERT INTO Companies(symbol, company_name) VALUES('{str.upper(symbol)}', '{company_names[symbol]}')")
    x = f"SELECT id FROM Companies WHERE symbol='{symbol}';"
    logging.debug(f'submitting following query to find company_id from symbol: {x}')
    sql_query = select_query(x)
    if not sql_query:
        raise ValueError(f"Company symbol({symbol}) is not in database or was not found.")
    symbol_id = sql_query[0][0]

    for date in json_obj['Time Series (Daily)'].keys():
        # find/generate date id
        logging.debug(msg=f'add_time_series_daily_entry, start of each-date for loop, current date={date}')
        date_id = select_query(f'SELECT id FROM Dates WHERE date="{date}"')
        logging.debug(f'add_time_series_daily_entry(): attempting to get date_id for {date}: resutls: {date_id}')
        if not date_id: # Date not found in Dates table, must add and collect id#.
            logging.debug(f'date ({date}) not found, adding new id')
            insert_this = 'INSERT INTO Dates(date) VALUES (?);'
            insert_query(query=insert_this, parameterized_data=(f'{date}',))
            date_id = select_query(f'SELECT id FROM Dates WHERE date="{date}"')[0][0]
        else:
            date_id=date_id[0][0]
            logging.debug(f'date found, id={date_id}')
        # check if data for date for company is already recorded, add to DB if not
        if not check_data_point_exists(get_cursor(), 'DataPoints',
                                       f'company_id={symbol_id} and date', value=date_id):
            logging.info(f'inserting time series daily data for {symbol}, '
                         f'id:{symbol_id} into DataPoints table for date: {date}, date_id{date_id}')
            tsd_query = ('INSERT INTO DataPoints (company_id, date, open, close, high, low, volume) '
                         'Values (?, ?, ?, ?, ?, ?, ?);')
            prepared_data = (symbol_id,
                             date_id,
                             float(json_obj['Time Series (Daily)'][date]['1. open']),
                             float(json_obj['Time Series (Daily)'][date]['4. close']),
                             float(json_obj['Time Series (Daily)'][date]['2. high']),
                             float(json_obj['Time Series (Daily)'][date]['3. low']),
                             float(json_obj['Time Series (Daily)'][date]['5. volume']),
                             )
            logging.debug(f'add_time_series_daily_entry(), inserting prepared data into DB, '
                          f'parameterized. query={tsd_query}, data={prepared_data}')
            insert_query(query=tsd_query, parameterized_data=prepared_data)
            logging.info('data successfully added')
        else:
            logging.debug(f'date {date} data already logged for {symbol}')

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
    query = f"SELECT EXISTS (SELECT 1 FROM {table_name} WHERE {column_name} = ?)"
    logging.debug(f'performing following query: {query} --- parameterized variable={value}')
    cursor.execute(query, (value,))
    return cursor.fetchone()[0] > 0  # Get the first element from the fetchone tuple

def get_company_id(company_name):
    print(f"TEST LOG get_company_id(): company_name={company_name}")
    query = "SELECT id FROM Companies WHERE company_name=?"
    answer = select_query(query, (company_name,))
    print(f'TEST LOG get_company_id(), answer = {answer}')
    if not answer:
        raise ValueError(f'Database yielded no data for query "{query}" ?="{company_name}"')
    return answer[0][0]

def get_high_with_company_id(company_id, date_id=None):
    if isinstance(date_id, list):
        answer = []
        for date in date_id:
            data = select_query("SELECT high "
                                "FROM Datapoints "
                                "WHERE company_id=? AND date=?", (company_id, date))
            answer.append(data[0][0])
        return answer
    elif isinstance(date_id, int):
        data = select_query("SELECT high "
                            "FROM Datapoints "
                            "WHERE company_id=? AND date=?", (company_id, date_id))
        return data[0][0]
    elif date_id is None:
        latest_dates = get_latest_dates_by_id()
        for date in latest_dates:
            answer = select_query("SELECT high "
                                  "FROM Datapoints "
                                  "WHERE company_id=? AND date=?", (company_id, date))
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
        company_id = get_company_id(company_names[company])
        high_value = get_high_with_company_id(company_id)
        json_data_prep.setdefault(company_names[company],
                                  {company_names[company]: company_names[company], 'high':high_value, 'abbr': company})
    return json_data_prep

#{'IBM': {'IBM': 'IBM', 'high': 171.305, 'abbr': 'IBM'}, 'Apple': {'Apple': 'Apple', 'high': 215.17, 'abbr': 'AAPL'}, 'Google': {'Google': 'Google', 'high': 178.73, 'abbr': 'GOOG'}}