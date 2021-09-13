from typing import Optional

from pad.db.sql_item import SimpleSqlItem, ExistsStrategy
from pad.raw_processor.merged_data import MergedBonus


class ScheduleEvent(SimpleSqlItem):
    """A scheduled event.

    This could indicate a dungeon is open, a dungeon has a modifier active,
    or just a line of text + icon that indicates something.
    """
    TABLE = 'schedule'
    KEY_COL = 'event_id'

    @staticmethod
    def from_mb(o: MergedBonus) -> Optional['ScheduleEvent']:
        return ScheduleEvent(
            event_id=None,  # Key that is looked up or inserted
            server_id=o.server.value,
            group_name=o.group.name if o.group else None,
            event_type_id=o.bonus.bonus_id,
            start_timestamp=o.bonus.start_timestamp,
            end_timestamp=o.bonus.end_timestamp,
            message=o.bonus.message,
            url=o.bonus.url,
            value=o.bonus.bonus_value,
            dungeon_id=o.bonus.dungeon_id,
            sub_dungeon_id=o.bonus.sub_dungeon_id,
        )

    def __init__(self,
                 event_id: int = None,
                 server_id: int = None,
                 group_name: str = None,
                 event_type_id: int = None,
                 start_timestamp: int = None,
                 end_timestamp: int = None,
                 message: str = None,
                 url: str = None,
                 value: str = None,
                 dungeon_id: int = None,
                 sub_dungeon_id: int = None,
                 tstamp: int = None):
        self.event_id = event_id
        self.server_id = server_id
        self.group_name = group_name
        self.event_type_id = event_type_id
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.message = message
        self.url = url
        self.value = value
        self.dungeon_id = dungeon_id
        self.sub_dungeon_id = sub_dungeon_id
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]
