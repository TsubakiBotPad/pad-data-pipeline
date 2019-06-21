"""
This processor sets up dimension tables that are used as foreign keys as other tables.
In general it should do no work; it just simplifies the setup for a new database.
"""
from pad.db.db_util import DbWrapper

D_ATTRIBUTE = {
    'name': 'd_attribute',
    'cols': ['attribute_id', 'name'],
    'rows': [
        [0, 'Fire'],
        [1, 'Water'],
        [2, 'Wood'],
        [3, 'Light'],
        [4, 'Dark'],
    ],
}

# Do we need this?
D_CONDITION = {
    'name': 'd_condition',
    'cols': ['condition_type', 'name'],
    'rows': [
        [1, 'active'],
        [2, 'leader'],
    ],
}

D_TYPE = {
    'name': 'd_type',
    'cols': ['type_id', 'name'],
    'rows': [
        [0, 'Evolve'],
        [1, 'Balance'],
        [2, 'Physical'],
        [3, 'Healer'],
        [4, 'Dragon'],
        [5, 'God'],
        [6, 'Attacker'],
        [7, 'Devil'],
        [8, 'Machine'],
        [12, 'Awoken'],
        [14, 'Enhance'],
        [15, 'Vendor'],
    ],
}

DIMENSION_TABLES = [D_ATTRIBUTE, D_CONDITION, D_TYPE]


class DimensionProcessor(object):
    def __init__(self):
        pass

    def process(self, db: DbWrapper):
        print('loading', len(DIMENSION_TABLES), 'dimension tables')
        for tbl in DIMENSION_TABLES:
            sql = 'INSERT IGNORE INTO {} ({}) VALUES '.format(tbl['name'], ','.join(tbl['cols']))
            rows = []
            for row in tbl['rows']:
                row = list(map(lambda x: "'{}'".format(x), row))
                rows.append('({})'.format(','.join(row)))
            sql += ','.join(rows)
            db.insert_item(sql)
