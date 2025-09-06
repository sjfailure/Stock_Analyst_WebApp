import logging
from copy import deepcopy

from django.test import TestCase
from unittest.mock import patch
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import DataError

# Create your tests here.

from stock_analyst.models import Companies
from stock_analyst.helpers import get_date_instance_by_date

## Universal Values
date_formating = '%Y-%m-%d'
base_data_capsule = {
            '1. open': None,
            "2. high": None,
            "3. low": None,
            "4. close": None,
            "5. volume": None,
        }
faux_data_capsule = {
            '1. open': 1,
            "2. high": 1,
            "3. low": 1,
            "4. close": 1,
            "5. volume": 1,
        }

class GetCompanyInstanceBySymbol(TestCase):
    """Testing helpers.get_company_instance_by_symbol()"""
    """Points of weakness:
    1. non-string input
    2. will fail if not present
    3. confirm returned object id Companies ORM data
    """
    def setUp(self):
        x = Companies.objects.create(symbol='AAPL', company_name='Apple')
        x.save()
        x = Companies.objects.create(symbol='IBM', company_name='IBM')
        x.save()
        x = Companies.objects.create(symbol='GOOG', company_name='Google')
        x.save()

    def test_is_returning_company_instance(self):
        test = get_company_instance_by_symbol("IBM")
        check = Companies.objects.get(symbol="IBM")
        self.assertEqual(test, check)
        self.assertEqual(type(test), type(check))

    def test_calls_out_bad_input(self):
        self.assertRaises(TypeError, get_company_instance_by_symbol, 1)
        self.assertRaises(TypeError, get_company_instance_by_symbol, ['test'])

    def test_calls_out_non_existent_input(self):
        self.assertRaises(ObjectDoesNotExist, get_company_instance_by_symbol, "NPR")

class GetCompanyIDBySymbl(TestCase):

from stock_analyst.helpers import add_time_series_daily_datapoint
from stock_analyst.models import Datapoints, Dates, Companies
import copy, datetime

class AddTimeSeriesDailyDatapoint(TestCase):
    """Testing helpers.add_time_series_daily_datapoint()"""
    """Weaknesses:
    1. Should reject non-instance company data
    2. Should reject non-instance date data
    3. Should reject malformed data
    4. Should add data to correct fields."""

    def setUp(self):
        x = Companies.objects.create(company_name='IBM', symbol='IBM')
        x.save()
        company_instance = Companies.objects.create(company_name='Google', symbol='GOOG')
        company_instance.save()
        date = Dates.objects.create(date=(datetime.date.today()-datetime.timedelta(days=1)).strftime(date_formating))
        date.save()

    def test_calls_out_not_company_instance(self):
        today = datetime.date.today().strftime(date_formating)
        add_date_to_table(today)
        data = copy.deepcopy(base_data_capsule)
        for key in data:
            data[key] = 100
        self.assertRaises(TypeError,
                          add_time_series_daily_datapoint,
                          company_instance='GOOG',
                          date_instance=get_date_instance_by_date(today),
                          datapoint=data
                          )

    def test_calls_out_not_date_instance(self):
        data = copy.deepcopy(base_data_capsule)
        x = Datapoints.objects.create(company_id=get_company_instance_by_symbol('GOOG'),
                                      date=get_date_instance_by_date((datetime.date.today()-datetime.timedelta(days=1)).strftime(date_formating)),
                                      open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      )
        x.save()
        for key in data:
            data[key] = 100
        self.assertRaises(TypeError,
                          add_time_series_daily_datapoint,
                          company_instance=get_company_instance_by_symbol('GOOG'),
                          date_instance=datetime.date.today().strftime(date_formating),
                          datapoint=data)

    def test_calls_out_malformed_data(self):
        today = datetime.date.today().strftime(date_formating)
        add_date_to_table(today)
        data = copy.deepcopy(base_data_capsule)
        data = copy.deepcopy(base_data_capsule)
        x = Datapoints.objects.create(company_id=get_company_instance_by_symbol('GOOG'),
                                      date=get_date_instance_by_date((datetime.date.today()-datetime.timedelta(days=1)).strftime(date_formating)),
                                      open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      )
        x.save()
        for key in data:
            data[key] = 100
        data['1. open'] = '100'
        self.assertRaises(DataError,
                          add_time_series_daily_datapoint,
                          data,
                          get_company_instance_by_symbol("GOOG"),
                          get_date_instance_by_date(today)
                          )
        data['1. open'] = 100
        data['2. high'] = None
        self.assertRaises(DataError,
                          add_time_series_daily_datapoint,
                          data,
                          get_company_instance_by_symbol("GOOG"),
                          get_date_instance_by_date(today)
                          )
        data['2. high'] = 100
        data['3. low'] = 'test'
        self.assertRaises(DataError,
                          add_time_series_daily_datapoint,
                          data,
                          get_company_instance_by_symbol("GOOG"),
                          get_date_instance_by_date(today)
                          )
        data['3. low'] = 100
        data['4. close'] = Dates.objects.create(date=datetime.date(day=1, month=1, year=2025)).save()
        self.assertRaises(DataError,
                          add_time_series_daily_datapoint,
                          data,
                          get_company_instance_by_symbol("GOOG"),
                          get_date_instance_by_date(today)
                          )
        data['4. close'] = 100
        data['5. volume'] = True
        self.assertRaises(DataError,
                          add_time_series_daily_datapoint,
                          data,
                          get_company_instance_by_symbol("GOOG"),
                          get_date_instance_by_date(today)
                          )

    def test_is_storing_data_correctly(self):
        today = datetime.date.today().strftime(date_formating)
        date_instance = Dates.objects.create(date=today)
        date_instance.save()
        company_instance = get_company_instance_by_symbol('GOOG')
        data = {
            '1. open': 99,
            "2. high": 98,
            "3. low": 97,
            "4. close": 96,
            "5. volume": 1001,
        }

        """add_time_series_daily_datapoint() requires one datapoint already exist in db."""
        company_instance_x = Companies.objects.create(company_name='test', symbol='test')
        company_instance_x.save()
        date_x = Dates.objects.create(date='1900-01-01')
        date_x.save()
        datapoint_setup = Datapoints.objects.create(high=1, low=1, close=1, open=1, volume=1, company_id=company_instance_x, date=date_x)
        datapoint_setup.save()

        # Run function
        add_time_series_daily_datapoint(data,
                                        company_instance,
                                        date_instance
                                        )
        check = Datapoints.objects.get(company_id=company_instance.id, date=date_instance)
        self.assertEqual(check.open,data['1. open'])
        self.assertEqual(check.high, data["2. high"])
        self.assertEqual(check.low, data["3. low"])
        self.assertEqual(check.close, data["4. close"])
        self.assertEqual(check.volume, data["5. volume"])


from stock_analyst.helpers import should_api_call_be_made, get_company_instance_by_symbol, get_date_instance_by_date, add_date_to_table
from stock_analyst.models import Dates, Companies, Datapoints
import datetime


# class ShouldApiCallBeMadeTest(TestCase):
#     """Testing:
#     1. When no company is provided, the date of the latest data for any company is the deciding factor.
#     1a. If the date is a day or more from the current date, the function returns Trye otherwise False.
#     2. When a company IS provided, the date of the latest data for THAT company is the deciding factor.
#     2a. If the date is a day or more from the current date, the function returns True, otherwise False.
#     3. Incorrect Uses:
#     3a. Raise a Type Error if company_symbol is not a string."""
#     def setUp(self):
#         today = Dates.objects.create(date=datetime.date.today().strftime(date_formating))
#         today.save()
#         yesterday = Dates.objects.create(date=(datetime.date.today()-datetime.timedelta(days=1)).strftime(date_formating))
#         yesterday.save()
#         last_week = Dates.objects.create(date=(datetime.date.today()-datetime.timedelta(days=7)).strftime(date_formating))
#         last_week.save()
#         tomorrow = Dates.objects.create(date=(datetime.date.today()+datetime.timedelta(days=1)).strftime(date_formating))
#         tomorrow.save()
#         ibm_company = Companies.objects.create(symbol='IBM', company_name='IBM')
#         ibm_company.save()
#         apple_company = Companies.objects.create(symbol='aapl', company_name='Apple')
#         apple_company.save()
#         # ibm_test = Datapoints.objects.create(company_id=ibm_company, date=yesterday, open=100, high=101, low=98, close=99, volume=1000)
#         # ibm_test.save()
#         ibm_test = Datapoints.objects.create(company_id=ibm_company,
#                                              date=last_week,
#                                              open=100,
#                                              high=101,
#                                              low=98,
#                                              close=99,
#                                              volume=1000
#                                              )
#         ibm_test.save()
#         apple_test = Datapoints.objects.create(company_id=apple_company,
#                                                date=last_week,
#                                                open=100,
#                                                high=101,
#                                                low=98,
#                                                close=99,
#                                                volume=1000)
#         apple_test.save()
#
#
#     def test_is_checking_latest_for_all_companies_1(self):
#         """Asserting that function returns True when data is over a day old."""
#         """Data: IBM: [yesterday, last_week], Apple: [last_week]
#         Expecting True"""
#         self.assertTrue(should_api_call_be_made())
#         """Data: IBM: [yesterday, last_week], Apple: [yesterday, last_week]
#         Expecting True"""
#         date = Dates.objects.get(date=(datetime.date.today()-datetime.timedelta(days=1)).strftime(date_formating))
#         # date.save()
#         apple_test = Datapoints.objects.create(company_id=get_company_instance_by_symbol('AAPL'),
#                                                date=date,
#                                                open=100,
#                                                high=101,
#                                                low=98,
#                                                close=99,
#                                                volume=1000
#                                                )
#         apple_test.save()
#         self.assertTrue(should_api_call_be_made())
#
#     def test_is_checking_latest_for_all_companies_2(self):
#         """Asserting that function returns False when the latest datapoint for any company is less that a day old."""
#         """Data: IBM: [today, yesterday, last_week], Apple: [last_week]
#         Expecting True"""
#         today = datetime.date.today().strftime(date_formating)
#         add_date_to_table(today)
#         date = get_date_instance_by_date(today)
#         ibm_instance = get_company_instance_by_symbol('IBM')
#         data = copy.deepcopy(base_data_capsule)
#         for key in data:
#             data[key] = 100
#         add_time_series_daily_datapoint(data,
#                                         ibm_instance,
#                                         date)
#         self.assertFalse(should_api_call_be_made())
#
#     def test_is_checking_latest_for_specific_company_1(self):
#         """Asserting that function returns True if specified company's latest datapoint is old."""
#         """Data: IBM: [today, yesterday, last_week], Apple: [last_week]
#         Expecting True"""
#         today = datetime.date.today().strftime(date_formating)
#         add_date_to_table(today)
#         date = get_date_instance_by_date(today)
#         ibm_instance = get_company_instance_by_symbol('IBM')
#         data = copy.deepcopy(base_data_capsule)
#         for key in data:
#             data[key] = 100
#         add_time_series_daily_datapoint(data,
#                                         ibm_instance,
#                                         date)
#         self.assertTrue(should_api_call_be_made('AAPL'))
#
#     def test_is_checking_latest_for_specific_company_2(self):
#         """Asserting that function returns False if specified company's latest datapoint is NOT old."""
#         """Data: IBM: [today, yesterday, last_week], Apple: [last_week]
#                 Expecting True"""
#         today = datetime.date.today().strftime(date_formating)
#         add_date_to_table(today)
#         date = get_date_instance_by_date(today)
#         ibm_instance = get_company_instance_by_symbol('IBM')
#         data = copy.deepcopy(base_data_capsule)
#         for key in data:
#             data[key] = 100
#         add_time_series_daily_datapoint(data,
#                                         ibm_instance,
#                                         date)
#         self.assertFalse(should_api_call_be_made('IBM'))
#
#     def test_calls_out_improper_input(self):
#         self.assertRaises(TypeError, add_time_series_daily_datapoint, 1, [None,], False)
#         company_instance = get_company_instance_by_symbol('IBM')
#         self.assertRaises(TypeError, add_time_series_daily_datapoint, 1, company_instance, {'test': 1})
#         date_instance = get_date_instance_by_date(
#             date=(datetime.date.today()-datetime.timedelta(days=1)).strftime(date_formating))
#         self.assertRaises(TypeError, add_time_series_daily_datapoint, 1, company_instance, date_instance)
#         data = copy.deepcopy(base_data_capsule)
#         for entry in data:
#             data[entry] = 100
#         add_time_series_daily_datapoint(data, company_instance, date_instance)

from stock_analyst.helpers import add_company_to_table

class AddCompanyToTable(TestCase):
    """Testing functionality of helpers.add_company_to_table()"""
    """1. rejects if either input is not a string
    2. Accurately stores data for retrieval."""

    def setUp(self):
        x = Companies.objects.create(company_name='start_test_db', symbol='STDB')
        x.save()

    def test_rejects_junk_input(self):
        self.assertRaises(TypeError, add_company_to_table('test', 1))
        self.assertRaises(TypeError, add_company_to_table(False, 'sym'))
        self.assertRaises(TypeError,
                          add_company_to_table(['IBM, OpenAI, Google'],
                                               ['IBM', 'OAI', 'GOOG']))

    def test_accurately_stores_data(self):
        add_company_to_table(company_name="Stamos Corp", company_symbol='SCRP')
        x = Companies.objects.get(company_name="Stamos Corp")
        self.assertEqual(x.symbol, "SCRP")
        x = Companies.objects.get(symbol='SCRP')
        self.assertEqual(x.company_name, "Stamos Corp")
        add_company_to_table(company_name="The Martin Group", company_symbol='MART')
        x = Companies.objects.get(company_name="The Martin Group")
        self.assertEqual(x.symbol, 'MART')
        x = Companies.objects.get(symbol='MART')
        self.assertEqual(x.company_name, "The Martin Group")
        add_company_to_table(company_name="Bella&Rov, LLC", company_symbol='BERO')
        x = Companies.objects.get(company_name="Bella&Rov, LLC")
        self.assertEqual(x.symbol, 'BERO')
        x = Companies.objects.get(symbol='BERO')
        self.assertEqual(x.company_name, "Bella&Rov, LLC")

from stock_analyst.helpers import add_date_to_table
from django.core.exceptions import ValidationError

class AddDateToTable(TestCase):
    """Testing functionality of helpers.add_date_to_table()"""
    """1. Should reject input that is not a string.
    2. Should reject input that is not in the correct format.
    3. Accurately stores data from retrieval.
    """
    def test_rejects_junk_input(self):
        with self.assertRaises(TypeError):
            add_date_to_table(True)
        with self.assertRaises(TypeError):
            add_date_to_table({"date": '12/31/1999'})
        with self.assertRaises(TypeError):
            add_date_to_table(datetime.date.today())
        with self.assertRaises(TypeError):
            add_date_to_table(345)

    def test_rejects_incorrect_formatting(self):
        add_date_to_table(datetime.date.today().strftime(date_formating))
        with self.assertRaises(ValidationError):
            add_date_to_table(datetime.date(year=2025, day=1, month=1).strftime('%m-%d-%y')) # 2-digit year
        with self.assertRaises(ValidationError):
            add_date_to_table(datetime.date(year=2025, day=1, month=1).strftime('%y-%m-%d')) # 2-digit year
        with self.assertRaises(ValidationError):
            add_date_to_table(datetime.date(year=2025, day=1, month=1).strftime('%Y/%m/%d'))  # 2-digit year
        add_date_to_table(datetime.date(year=2000, day=1, month=1).isoformat())

    def test_accurately_stores_data(self):
        add_date_to_table(datetime.date(day=17, month=10, year=1985).strftime(date_formating))
        x = Dates.objects.get(date='1985-10-17')
        add_date_to_table(datetime.date(day=1, month=8, year=1585).strftime(date_formating))
        x = Dates.objects.get(date='1585-08-01')
        pass

from stock_analyst.helpers import is_company_in_db_by_symbol

class IsCompanyInDBBySymbol(TestCase):
    """Testing functionality of helpers.is_company_in_db_by_symbol()"""
    """1. should reject input that is not a string.
    2. Accurately identify if something is or isn't in the Companies table (return True if it is, False if it is not). """

    def setUp(self):
        x = Companies.objects.create(company_name='TestComp', symbol='TC1')
        x.save()
        x = Companies.objects.create(company_name='TestComp2', symbol='TC2')
        x.save()

    def test_rejects_junk_input(self):
        self.assertRaises(TypeError, is_company_in_db_by_symbol, True)
        self.assertRaises(TypeError, is_company_in_db_by_symbol, ['test'])
        self.assertRaises(TypeError, is_company_in_db_by_symbol, 12)

    def test_accurately_checks_data_1(self):
        logging.debug(f'test_accurately_checks_data() for is_company_in_db_by_symbol(): call is: "is_company_in_db_by_symbol("TC1")", result:{is_company_in_db_by_symbol("TC1")}')
        logging.debug(f'test_accurately_checks_data(): full database read={[entry for entry in Companies.objects.all()]}')
        self.assertTrue(is_company_in_db_by_symbol("TC1"))

    def test_accurately_checks_data_2(self):
        self.assertTrue(is_company_in_db_by_symbol("TC2"))

    def test_accurately_checks_data_3(self):
        logging.debug(f'test_accurately_checks_data_3() for is_company_in_db_by_symbol(): start of test, input is "{'TC'}"')
        answer = is_company_in_db_by_symbol('TC')
        logging.debug(f'test_accurately_checks_data_3() for is_company_in_db_by_symbol(): function returned={answer}, expecting:{False}')
        self.assertFalse(is_company_in_db_by_symbol("TC"))

    def test_accurately_checks_data_4(self):
        self.assertFalse(is_company_in_db_by_symbol("FBI"))

    def test_accurately_checks_data_5(self):
        self.assertFalse(is_company_in_db_by_symbol("GOOG"))

    def test_accurately_checks_data_6(self):
        add_company_to_table(company_name="Google", company_symbol='GOOG')
        self.assertTrue(is_company_in_db_by_symbol("GOOG"))


from stock_analyst.helpers import is_date_in_db
class IsDateInDB(TestCase):
    """Testing functionality of helpers.is_date_in_db()"""
    """1. Should reject input that is not a string.
    2. Should reject input that is not in the correct format.
    3. Accurately identify if a date is or isn't in the Dates db."""

    def setUp(self):
        x = Dates.objects.create(date="1900-01-01")
        x.save()
        x = Dates.objects.create(date="1985-10-17")
        x.save()

    def test_reject_incorrect_input(self):
        with self.assertRaises(TypeError):
            is_date_in_db(23)
        with self.assertRaises(TypeError):
            is_date_in_db(['test'])
        with self.assertRaises(TypeError):
            is_date_in_db({'test': 'data'})
        with self.assertRaises(TypeError):
            is_date_in_db(get_date_instance_by_date("1900-01-01"))

    def test_reject_malformed_input_date(self):
        with self.assertRaises(ValidationError):
            is_date_in_db('01-01-1900')
        with self.assertRaises(ValidationError):
            is_date_in_db('10/17/1985')
        with self.assertRaises(ValidationError):
            is_date_in_db('85-10-17')
        is_date_in_db('1900-01-01')
        is_date_in_db('2000-01-01')

    def test_accurately_checks_data(self):
        self.assertTrue(is_date_in_db('1900-01-01'))
        self.assertTrue(is_date_in_db("1985-10-17"))
        self.assertFalse(is_date_in_db('2001-01-01'))
        add_date_to_table('2001-01-01')
        self.assertTrue(is_date_in_db('2001-01-01'))
        today = datetime.date.today().strftime(date_formating)
        self.assertFalse(is_date_in_db(today))
        add_date_to_table(today)
        self.assertTrue(is_date_in_db(today))


from stock_analyst.helpers import get_latest_entry_date_in_datapoints

class GetLatestEntryDateInDatapoints(TestCase):
    """Testing functionality of helpers.get_latest_entry_date_in_datapoints()"""
    """Weaknesses:
    1. if datapoints is empty, return generic date (01/01/1900)
    2. returns actual latest date for datapoints"""

    def test_handles_empty_db(self):
        """Asserting empty database returns generic old date"""
        self.assertEqual('1900-01-01', get_latest_entry_date_in_datapoints())

    def test_accurately_reports_latest_date_1(self):
        """Asserting reports correct data, 1 entry"""
        x = Companies.objects.create(company_name='IBM', symbol='IBM')
        x.save()
        last_week = (datetime.date.today()-datetime.timedelta(days=7))
        y = Dates.objects.create(date=last_week.strftime(date_formating))
        y.save()
        z = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=x,
                                      date=y)
        z.save()
        self.assertEqual(get_latest_entry_date_in_datapoints(), last_week)

    def test_accurately_reports_latest_date_2(self):
        """Asserting reports correct data, 2 entries, same day."""
        x = Companies.objects.create(company_name='IBM', symbol='IBM')
        x.save()
        last_week = (datetime.date.today() - datetime.timedelta(days=7))
        y = Dates.objects.create(date=last_week.strftime(date_formating))
        y.save()
        z = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=x,
                                      date=y)
        z.save()

        a = Companies.objects.create(company_name='Google', symbol='GOOG')
        a.save()
        c = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=a,
                                      date=y)
        c.save()
        self.assertEqual(get_latest_entry_date_in_datapoints(), last_week)

    def test_accurately_reports_latest_date_3(self):
        """Asserting reports correct data, 2 entries, 1 company, 2 dates"""
        x = Companies.objects.create(company_name='IBM', symbol='IBM')
        x.save()
        last_week = (datetime.date.today() - datetime.timedelta(days=7))
        y = Dates.objects.create(date=last_week.strftime(date_formating))
        y.save()
        z = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=x,
                                      date=y)
        z.save()

        six_days_ago = (datetime.date.today() - datetime.timedelta(days=6))
        b = Dates.objects.create(date=six_days_ago.strftime(date_formating))
        b.save()
        c = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=x,
                                      date=b)
        c.save()
        self.assertEqual(get_latest_entry_date_in_datapoints(), six_days_ago) # reports more recent date

    def test_accurately_reports_latest_date_4(self):
        """Asserting reports correct data, 2 entries, 2 companies, 2 dates"""
        x = Companies.objects.create(company_name='IBM', symbol='IBM')
        x.save()
        last_week = (datetime.date.today() - datetime.timedelta(days=7))
        y = Dates.objects.create(date=last_week.strftime(date_formating))
        y.save()
        z = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=x,
                                      date=y)
        z.save()

        a = Companies.objects.create(company_name='Google', symbol='GOOG')
        a.save()
        six_days_ago = (datetime.date.today() - datetime.timedelta(days=6))
        b = Dates.objects.create(date=six_days_ago.strftime(date_formating))
        b.save()
        c = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=a,
                                      date=b)
        c.save()
        self.assertEqual(get_latest_entry_date_in_datapoints(), six_days_ago) # reports latest date, regardless of company_id

    def test_accurately_reports_latest_date_5(self):
        """Asserting reports correct data, 6 entries, 3 companies, 3 dates"""
        """2 entries per company, 2 companies data for last_week and six_days_ago, 1 for last_week and yesterday"""
        last_week = (datetime.date.today() - datetime.timedelta(days=7))
        last_week_instance = Dates.objects.create(date=last_week.strftime(date_formating))
        last_week_instance.save()
        six_days_ago = (datetime.date.today() - datetime.timedelta(days=6))
        six_days_ago_instance = Dates.objects.create(date=six_days_ago.strftime(date_formating))
        six_days_ago_instance.save()
        yesterday = (datetime.date.today() - datetime.timedelta(days=1))
        yesterday_instance = Dates.objects.create(date=yesterday.strftime(date_formating))
        yesterday_instance.save()


        # IBM, last_week, six_days_ago
        IBM_instance = Companies.objects.create(company_name="IBM", symbol="IBM")
        IBM_instance.save()
        x = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=IBM_instance,
                                      date=last_week_instance)
        x.save()
        x = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=IBM_instance,
                                      date=six_days_ago_instance)
        x.save()
        # Google, last_week, six_days_ago
        Google_instance = Companies.objects.create(company_name='Google', symbol='GOOG')
        Google_instance.save()
        x = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=Google_instance,
                                      date=last_week_instance)
        x.save()
        x = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=Google_instance,
                                      date=six_days_ago_instance)
        x.save()
        # AAPL - last week and yesterday
        Apple_instance = Companies.objects.create(company_name='Apple', symbol='AAPL')
        Apple_instance.save()
        x = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=Apple_instance,
                                      date=last_week_instance)
        x.save()
        x = Datapoints.objects.create(open=1,
                                      close=1,
                                      high=1,
                                      low=1,
                                      volume=1,
                                      company_id=Apple_instance,
                                      date=yesterday_instance)
        x.save()
        self.assertEqual(get_latest_entry_date_in_datapoints(), yesterday) # reports latest date, despite other variables

class OfflineWorkerTask(TestCase):
    """Proposed function: helpers.offline_worker_task(). Used to update current model with all available data from API.
    To be run manually to prevent long load time and interactivity of main app (see helpers.update_model() functionality.
    """
    """1. Function will require no parameters.
       2. Function will make complete-data call to API (all stock data for company X).
       3. Function will update model with this information:
          3a. If record already exists, skip.
          3b. If record present but incorrect or incomplete, correct it
          3c. If not present, record data point.
       4. Function is making full pass (10-15 companies at 10-20+years of data), will not be fast.
       5. To be hosted locally, directed at online DB."""

    data_template = {
        "Meta Data":
            {"1. Information": '?',
             "2. Symbol": None,
             "3. Last Refreshed": None,
             "4. Output Size": None,
             "5. Time Zone": None,
             },
        "Time Series (Daily)": None}
    tsd_datapoint_template = {"1. open": 11,
                              "2. high": 100,
                              "3. low": 100,
                              "4. close": 100,
                              "5. volume": 1000,
                              }

    def setUp(self):
        pass

    def test_skips_existing_datapoints(self):
        pass

    def test_adds_old_datapoints(self):
        pass

    def test_adds_new_datapoints(self):
        pass

    def test_updates_incorrect_data(self):
        pass



