"""
This processor sets up dimension tables that are used as foreign keys as other tables.
In general it should do no work; it just simplifies the setup for a new database.
"""
import logging

from pad.common.shared_types import Server
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
    DAttribute(5, 'Unused'),
    DAttribute(6, 'Null'),
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


class DServer(SimpleSqlItem):
    """PAD Servers."""
    TABLE = 'd_servers'
    KEY_COL = 'server_id'

    def __init__(self, server_id: int = None, name: str = None):
        self.server_id = server_id
        self.name = name


D_SERVERS = [
    DServer(Server.jp.value, 'JP'),
    DServer(Server.na.value, 'NA'),
    DServer(Server.kr.value, 'KR'),
]


class DEventType(SimpleSqlItem):
    """Event types."""
    TABLE = 'd_event_types'
    KEY_COL = 'event_type_id'

    def __init__(self, event_type_id: int = None, name: str = None):
        self.event_type_id = event_type_id
        self.name = name


D_EVENT_TYPES = [
    DEventType(0, 'General'),
]


class DEggMachinesType(SimpleSqlItem):
    """Egg machine categories."""
    TABLE = 'd_egg_machine_types'
    KEY_COL = 'egg_machine_type_id'

    def __init__(self, egg_machine_type_id: int = None, name: str = None):
        self.egg_machine_type_id = egg_machine_type_id
        self.name = name


D_EGG_MACHINE_TYPES = [
    DEggMachinesType(0, 'Special'),
    DEggMachinesType(1, 'REM'),
    DEggMachinesType(2, 'PEM'),
]


class DimensionProcessor(object):
    def __init__(self):
        pass

    def process(self, db: DbWrapper):
        for item in D_ATTRIBUTES:
            db.insert_or_update(item)
        for item in D_TYPES:
            db.insert_or_update(item)
        for item in D_SERVERS:
            db.insert_or_update(item)
        for item in D_EVENT_TYPES:
            db.insert_or_update(item)
        for item in D_EGG_MACHINE_TYPES:
            db.insert_or_update(item)
