import logging

from . import Api
from . import DatabaseAdmin

in_production = False
test_json_write_data = False
complete_data_acquired = False

logging.basicConfig(level=logging.DEBUG)

logging.info('start')
x = DatabaseAdmin.get_conn()
x.close()

if in_production:
    logging.info('gather json from api')
    for data_point in Api.get_all_company_tsd_data(complete=complete_data_acquired):
        logging.debug(msg=f'main.py, data_point={data_point, type(data_point)}, to pass on as json_object')
        DatabaseAdmin.add_time_series_daily_entry(DatabaseAdmin.get_conn(), data_point)

elif test_json_write_data:
    logging.info('testing jsonHandling.py functionality')
    for datum in Api.get_all_company_tsd_data(True):
        logging.debug('data stored')
else:
    logging.info('practice_mode, import sample api data')

    for data_point in Api.get_practice_data():
        DatabaseAdmin.add_time_series_daily_entry(DatabaseAdmin.get_conn(), data_point)
print('done')

# for x in DatabaseAdmin.select_query("SELECT * FROM DataPoints"):
#     print(x)
