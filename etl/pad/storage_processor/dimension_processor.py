"""
This processor sets up dimension tables that are used as foreign keys as other tables.
In general it should do no work; it just simplifies the setup for a new database.
"""
import logging

from pad.common.shared_types import Server
from pad.db.db_util import DbWrapper
from pad.db.sql_item import SimpleSqlItem

logger = logging.getLogger('processor')


class DimensionItem(SimpleSqlItem):
    """Dimension table superclass"""
    def __init__(self, dimension_id: int, name: str):
        self.__dict__[self.KEY_COL] = dimension_id
        self.name = name


class DAttribute(DimensionItem):
    """Monster color attributes."""
    TABLE = 'd_attributes'
    KEY_COL = 'attribute_id'


class DType(DimensionItem):
    """Monster types."""
    TABLE = 'd_types'
    KEY_COL = 'type_id'


class DServer(DimensionItem):
    """PAD Servers."""
    TABLE = 'd_servers'
    KEY_COL = 'server_id'


class DEventType(DimensionItem):
    """Event types."""
    TABLE = 'd_event_types'
    KEY_COL = 'event_type_id'


class DEggMachinesType(DimensionItem):
    """Egg machine categories."""
    TABLE = 'd_egg_machine_types'
    KEY_COL = 'egg_machine_type_id'


class DCompoundSkillTypes(DimensionItem):
    """Compound active skill group types."""
    TABLE = 'd_compound_skill_types'
    KEY_COL = 'compound_skill_type_id'


class DFixedSlotType(DimensionItem):
    """Compound active skill group types."""
    TABLE = 'd_fixed_slot_type'
    KEY_COL = 'fixed_slot_type_id'


DIMENSION_OBJECTS = [
    DAttribute(0, 'Fire'),
    DAttribute(1, 'Water'),
    DAttribute(2, 'Wood'),
    DAttribute(3, 'Light'),
    DAttribute(4, 'Dark'),
    DAttribute(5, 'Unknown'),
    DAttribute(6, 'None'),

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

    DServer(Server.jp.value, 'JP'),
    DServer(Server.na.value, 'NA'),
    DServer(Server.kr.value, 'KR'),

    DEventType(0, 'General'),
    DEventType(1, 'EXP Boost'),
    DEventType(2, 'Coin Boost'),
    DEventType(3, 'Drop Boost'),
    DEventType(5, 'Stamina Reduction'),
    DEventType(6, 'Dungeon'),
    DEventType(8, 'PEM Event'),
    DEventType(9, 'REM Event'),
    DEventType(10, 'PEM Cost'),
    DEventType(11, 'Feed XP Bonus Chance'),
    DEventType(12, 'Plus Drop Rate 1'),
    DEventType(13, 'Unknown 13'),
    DEventType(14, 'Unknown 14'),
    DEventType(15, 'Send Egg Roll'),
    DEventType(16, 'Plus Drop Rate 2'),
    DEventType(17, 'Feed Skillup Bonus Chance'),
    DEventType(20, 'Tournament Active'),
    DEventType(21, 'Tournament Closed'),
    DEventType(22, 'Score Announcement'),
    DEventType(23, 'PAD Metadata'),
    DEventType(24, 'Gift Dungeon with Reward'),
    DEventType(25, 'Dungeon Special Event'),
    DEventType(29, 'Multiplayer Announcement'),
    DEventType(31, 'Multiplayer Dungeon Text'),
    DEventType(32, 'Tournament Text'),
    DEventType(33, 'PAD Metadata 2'),
    DEventType(36, 'Daily Dragons'),
    DEventType(37, 'Monthly Quest Dungeon'),
    DEventType(38, 'Exchange Text'),
    DEventType(39, 'Dungeon Floor Text'),
    DEventType(40, 'Unknown 40'),
    DEventType(41, 'Normal Announcement'),
    DEventType(42, 'Technical Announcement'),
    DEventType(43, 'Dungeon Web Info Link'),
    DEventType(44, 'Stone Purchase Text'),
    DEventType(47, 'Story Category Text'),
    DEventType(50, 'Special Dungeon Info Link'),
    DEventType(52, 'Dungeon Unavailable Popup'),
    DEventType(53, '8P Reward Table'),
    DEventType(54, 'VEM Event'),

    DEggMachinesType(0, 'Special'),
    DEggMachinesType(1, 'REM'),
    DEggMachinesType(2, 'PEM'),
    DEggMachinesType(3, 'VEM'),

    DCompoundSkillTypes(0, 'Normal'),
    DCompoundSkillTypes(1, 'Random'),
    DCompoundSkillTypes(2, 'Evolving'),
    DCompoundSkillTypes(3, 'Looping'),

    DFixedSlotType(0, 'Not Fixed'),
    DFixedSlotType(1, 'Fixed Empty'),
    DFixedSlotType(2, 'Fixed Monster'),
]


class DimensionProcessor(object):
    def __init__(self):
        pass

    def process(self, db: DbWrapper):
        for item in DIMENSION_OBJECTS:
            db.insert_or_update(item)
