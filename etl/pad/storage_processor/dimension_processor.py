"""
This processor sets up dimension tables that are used as foreign keys as other tables.
In general it should do no work; it just simplifies the setup for a new database.
"""
import logging

from pad.db.db_util import DbWrapper
from pad.db.sql_item import SimpleSqlItem

logger = logging.getLogger('processor')


class DAttribute(SimpleSqlItem):
    """Monster color attributes."""
    TABLE = 'd_attributes'
    KEY_COL = 'attribute_id'

    def __init__(self, attribute_id: int = None, name: str = None):
        self.attribute_id = attribute_id
        self.name = name


D_ATTRIBUTES = [
    DAttribute(0, 'Fire'),
    DAttribute(1, 'Water'),
    DAttribute(2, 'Wood'),
    DAttribute(3, 'Light'),
    DAttribute(4, 'Dark'),
]


class DType(SimpleSqlItem):
    """Monster types."""
    TABLE = 'd_types'
    KEY_COL = 'type_id'

    def __init__(self, type_id: int = None, name: str = None):
        self.type_id = type_id
        self.name = name


D_TYPES = [
    DType(0, 'Evolve'),
    DType(1, 'Balance'),
    DType(2, 'Physical'),
    DType(3, 'Healer'),
    DType(4, 'Dragon'),
    DType(5, 'God'),
    DType(6, 'Attacker'),
    DType(7, 'Devil'),
    DType(8, 'Machine'),
    DType(12, 'Awoken'),
    DType(14, 'Enhance'),
    DType(15, 'Vendor'),
]


class DimensionProcessor(object):
    def __init__(self):
        pass

    def process(self, db: DbWrapper):
        for item in D_ATTRIBUTES:
            db.insert_or_update(item)
        for item in D_TYPES:
            db.insert_or_update(item)
