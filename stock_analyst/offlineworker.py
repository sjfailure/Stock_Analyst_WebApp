"""This script is to be run regularly (once a week) to update and maintain the data integrity of the database. It makes
API calls for all tracked companies and updates the model with the complete information set available for each company.
Script will run at BigO(n^n) but all transactions should be final and immediately queryable from the Django ORM."""
import logging

import requests
import os
import psycopg2

from stock_analyst.model.Api import companies

from helpers import companies

def offline_worker_task():
    def connection_builder():
        database_access_credentials = None
        if 'DATABASE_URL' in os.environ.keys():
            database_access_credentials = os.environ.get('DATABASE_URL')
        else:
            logging.error('DATABASE_URL not configured in Environment Variables correctly; cancelling task.')
            raise EnvironmentError('DATABASE_URL not configured in Environment Variables correctly; cancelling task.')
        connection = psycopg2.connect(dsn=database_access_credentials)
        return connection

    def check_data(data, date, company_symbol):
        company_id = get_company_id(company_symbol)
        date_id = get_date_id(date)
        retrieved_data = connection_builder().cursor().execute(query="""SELECT * 
                                                 FROM stock_analyst_datapoints 
                                                 WHERE company_id_id=%s AND date_id=%s""", params=)


    def get_company_id(company_symbol, company_name=None):
        data = select_request(query="""SELECT id 
                                       FROM stock_analyst_companies 
                                       WHERE symbol=%s;""", params=[company_symbol,])
        if not data:
            if company_name is None:
                company_name = companies[company_symbol]
            insert_or_update_query("""INSERT INTO stock_analyst_companies (company_name, symbol) 
                                      VALUES (%s, %s);""", params=[company_name, company_symbol,])
            data = select_request(query="""SELECT id 
                                                   FROM stock_analyst_companies
                                                   WHERE symbol=%s;""", params=[company_symbol, ])
        return data[0]

    def get_date_id(date_string):
        data = select_request(query="""SELECT id 
                                        FROM stock_analyst_dates 
                                        WHERE date=%s;""", params=[date_string,])
        if not data:
            insert_or_update_query("""INSERT INTO stock_analyst_dates (date)
                                      VALUES (%s);""", params=[date_string,])
            data = select_request(query="""SELECT id 
                                                    FROM stock_analyst_dates 
                                                    WHERE date=%s;""", params=[date_string, ])
        return data[0]

    def select_request(database=None, query=None, params=None):
        if database is None and query=None:
            raise AttributeError('offline_worker_task().select_request() must be given a database or formed SQL query')
        if query is None:
            query = f"""SELECT * FROM {database};"""
        connection = connection_builder()
        retrieved_data = None
        if params is None:
            with connection.cursor() as curs:
                curs.execute(query=query)
                retrieved_data = curs.fetchall()
        else:
            with connection.cursor() as curs:
                curs.execute(query=query, params=params)
                retrieved_data = curs.fetchall()
        connection.close()
        return retrieved_data

    def insert_or_update_query(query, params=None):
        connection = connection_builder()
        if params is None:
            with connection.cursor() as curs:
                curs.execute(query=query)
        else:
            with connection.cursor() as curs:
                curs.execute(query=query, params=params)
        connection.commit()
        connection.close()
        return True



    api_key = None
    if 'alpha_vantage_api_key' in os.environ.keys():
        api_key = os.environ.get('alpha_vantage_api_key')
    else:
        logging.error('API not configured in Environment Variables correctly; cancelling task.')
        return



    company_list_query = """SELECT symbol 
                            FROM stock_analyst_companies 
                            ORDER BY symbol;"""
    company_list = select_request(query=company_list_query)

