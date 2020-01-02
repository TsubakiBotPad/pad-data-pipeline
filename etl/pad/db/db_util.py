import json
import logging
import random
from typing import Callable

import pymysql
from pymysql import InterfaceError

from pad.common import pad_util
from .sql_item import SqlItem, _col_compare, _tbl_name_ref, _process_col_mappings, ExistsStrategy

logger = logging.getLogger('database')
logger.setLevel(logging.ERROR)


class DbWrapper(object):
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.connection = None

    def connect(self, db_config):
        logger.debug('DB Connecting')
        self.connection = pymysql.connect(host=db_config['host'],
                                          user=db_config['user'],
                                          password=db_config['password'],
                                          db=db_config['db'],
                                          charset=db_config['charset'],
                                          cursorclass=pymysql.cursors.DictCursor,
                                          autocommit=True)
        logger.info('DB Connected')

    def execute(self, cursor, sql):
        logger.debug('Executing: %s', sql)
        try:
            return cursor.execute(sql)
        except InterfaceError:
            self.connection.ping()
            return cursor.execute(sql)

    def fetch_data(self, sql):
        with self.connection.cursor() as cursor:
            self.execute(cursor, sql)
        return list(cursor.fetchall())

    def load_to_key_value(self, key_name, value_name, table_name, where_clause=None):
        with self.connection.cursor() as cursor:
            sql = 'SELECT {} AS k, {} AS v FROM {}'.format(key_name, value_name, table_name)
            if where_clause:
                sql += ' WHERE ' + where_clause
            self.execute(cursor, sql)
            data = list(cursor.fetchall())
            return {row['k']: row['v'] for row in data}

    def get_single_or_no_row(self, sql):
        with self.connection.cursor() as cursor:
            self.execute(cursor, sql)
            data = list(cursor.fetchall())
            num_rows = len(data)
            if num_rows > 1:
                raise ValueError('got too many results:', num_rows, sql)
            if num_rows == 0:
                return None
            else:
                return data[0]

    def get_single_value(self, sql, op: Callable = str, fail_on_empty=True):
        with self.connection.cursor() as cursor:
            self.execute(cursor, sql)
            data = list(cursor.fetchall())
            num_rows = len(data)
            if num_rows == 0:
                if self.dry_run or not fail_on_empty:
                    return None
                raise ValueError('got zero results:', sql)
            if num_rows > 1:
                raise ValueError('got too many results:', num_rows, sql)
            row = data[0]
            if len(row.values()) > 1:
                raise ValueError('too many columns in result:', sql)
            result_value = list(row.values())[0]
            if result_value is None:
                if fail_on_empty:
                    raise ValueError('got null result:', sql)
                else:
                    return None
            return op(result_value)

    def load_single_object(self, obj_type, key_val):
        sql = 'SELECT * FROM {} WHERE {}'.format(
            _tbl_name_ref(obj_type.TABLE),
            _col_compare(obj_type.KEY_COL))
        sql = sql.format(**{obj_type.KEY_COL: key_val})
        data = self.get_single_or_no_row(sql)
        return obj_type(**_process_col_mappings(obj_type, data)) if data else None

    def load_multiple_objects(self, obj_type, key_val):
        sql = 'SELECT * FROM {} WHERE {}'.format(
            _tbl_name_ref(obj_type.TABLE),
            _col_compare(obj_type.LIST_COL))
        sql = sql.format(**{obj_type.LIST_COL: key_val})
        data = self.fetch_data(sql)
        return [obj_type(**_process_col_mappings(obj_type, d)) for d in data]

    def custom_load_multiple_objects(self, obj_type, lookup_sql):
        data = self.fetch_data(lookup_sql)
        return [obj_type(**_process_col_mappings(obj_type, d)) for d in data]

    def check_existing(self, sql):
        with self.connection.cursor() as cursor:
            num_rows = self.execute(cursor, sql)
            if num_rows > 1:
                raise ValueError('got too many results:', num_rows, sql)
            return bool(num_rows)

    def check_existing_value(self, sql):
        with self.connection.cursor() as cursor:
            num_rows = self.execute(cursor, sql)
            if num_rows > 1:
                raise ValueError('got too many results:', num_rows, sql)
            elif num_rows == 0:
                return None
            else:
                row_values = list(cursor.fetchone().values())
                if len(row_values) > 1:
                    return row_values
                else:
                    return row_values[0]

    def insert_item(self, sql):
        with self.connection.cursor() as cursor:
            if self.dry_run:
                logger.warn('not inserting item due to dry run')
                return random.randrange(-99999, -1)
            self.execute(cursor, sql)
            data = list(cursor.fetchall())
            num_rows = len(data)
            if num_rows > 0:
                raise ValueError('got too many results for insert:', num_rows, sql)
            return cursor.lastrowid

    def update_item(self, sql):
        with self.connection.cursor() as cursor:
            if self.dry_run:
                logger.warn('not running update due to dry run')
                return 0
            self.execute(cursor, sql)
            data = list(cursor.fetchall())
            num_rows = len(data)
            if num_rows > 0:
                raise ValueError('got too many results for update:', num_rows, sql)
            return cursor.rowcount
    
    def insert_or_update(self, item: SqlItem, force_insert=False):
        try:
            return self._insert_or_update(item, force_insert=force_insert)
        except Exception as ex:
            logger.fatal('Failed to insert item: %s', pad_util.json_string_dump(item, pretty=True))
            raise ex

    def _insert_or_update(self, item: SqlItem, force_insert: bool):
        key = item.key_value()

        if force_insert:
            new_key = self.insert_item(item.insert_sql())
            if not key:
                key = new_key
                item.set_key_value(key)
            logger.info('force inserted an item: %s', item)
            return

        if item.exists_strategy() == ExistsStrategy.BY_KEY:
            if not self.check_existing(item.key_exists_sql()):
                logger.info('item needed insert: %s', item)
                self.insert_item(item.insert_sql())
            elif not self.check_existing(item.needs_update_sql()):
                logger.info('item needed update: %s', item)
                self.insert_item(item.update_sql())

        elif item.exists_strategy() == ExistsStrategy.BY_KEY_IF_SET:
            if not key:
                key = self.insert_item(item.insert_sql())
                item.set_key_value(key)
                logger.info('item needed by-key insert: %s', item)
            elif not self.check_existing(item.needs_update_sql()):
                logger.info('item needed by-key update: %s', item)
                self.insert_item(item.update_sql())

        elif item.exists_strategy() == ExistsStrategy.BY_VALUE:
            key = self.get_single_value(item.value_exists_sql(), op=int, fail_on_empty=False)
            item.set_key_value(key)

            if not key:
                key = self.insert_item(item.insert_sql())
                item.set_key_value(key)
                logger.info('item needed by-value insert: %s', item)
            elif not self.check_existing(item.needs_update_sql()):
                logger.info('item needed by-value update: %s', item)
                self.insert_item(item.update_sql())

        elif item.exists_strategy() == ExistsStrategy.CUSTOM:
            raise ValueError('Item cannot be upserted: {}'.format(item))

        return key
