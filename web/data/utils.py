import binascii
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
            fixed_data = float(data)
        elif type(data) is datetime:
            fixed_data = data.isoformat(' ')
        elif type(data) == bytes:
            fixed_data = '0x' + binascii.hexlify(bytearray(data)).decode('ascii')
        elif type(data) not in [int, float, str]:
            fixed_data = str(data)
        else:
            fixed_data = data

        fixed_col = col
        row_data[fixed_col] = fixed_data
    return row_data


def dump_table(cursor):
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
            sql += ' AND end_timestamp > UNIX_TIMESTAMP()'

    # Added this to make client updating easier; if the update fails, the lowest-value records will have been inserted,
    # and the higher value ones will get inserted on the next run.
    sql += ' ORDER BY tstamp ASC'

    with connection.cursor() as cursor:
        cursor.execute(sql)
        data = dump_table(cursor)

    connection.close()
    return data
