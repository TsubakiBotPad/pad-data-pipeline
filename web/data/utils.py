from datetime import datetime
from decimal import Decimal

import pymysql


def fix_row(row):
    row_data = {}
    for col in row:
        data = row[col]
        if data is None:
            fixed_data = None
        elif type(data) is Decimal:
            first = '{}'.format(float(data))
            second = '{:.1f}'.format(float(data))
            fixed_data = max((first, second), key=len)
        elif type(data) is datetime:
            fixed_data = data.isoformat(' ')
        elif type(data) not in [int, float, str]:
            fixed_data = str(data)
        else:
            fixed_data = data

        fixed_col = col
        row_data[fixed_col] = fixed_data
    return row_data

def dump_table(table_name, cursor):
    result_json = {'items': []}
    for row in cursor:
        result_json['items'].append(fix_row(row))

    return result_json


def load_from_db(db_config, table, tstamp):
    connection = pymysql.connect(host=db_config['host'],
                                 user=db_config['user'],
                                 password=db_config['password'],
                                 db=db_config['db'],
                                 charset=db_config['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)

    table = table.lower()
    sql = 'SELECT * FROM `{}`'.format(table)

    if table == 'timestamps':
        pass
    else:
        sql += ' WHERE tstamp > {}'.format(int(tstamp))

        if table == 'schedule':
            sql += ' AND close_timestamp > UNIX_TIMESTAMP()'

    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dump_table(table, cursor)

    connection.close()
    return data
