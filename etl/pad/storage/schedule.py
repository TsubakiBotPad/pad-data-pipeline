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
            event_type_id=0,  # TODO: fixme
            start_timestamp=o.start_timestamp,
            end_timestamp=o.end_timestamp,
            icon_id=0,
            group_name=o.group.name if o.group else None,
            dungeon_id=o.dungeon.dungeon_id if o.dungeon else None,
            url=None,
            info_jp=None,
            info_na=None,
            info_kr=None
        )

    def __init__(self,
                 event_id: int = None,
                 server_id: int = None,
                 event_type_id: int = None,
                 start_timestamp: int = None,
                 end_timestamp: int = None,
                 icon_id: int = None,
                 group_name: str = None,
                 dungeon_id: int = None,
                 url: str = None,
                 info_jp: str = None,
                 info_na: str = None,
                 info_kr: str = None,
                 tstamp: int = None):
        self.event_id = event_id
        self.server_id = server_id
        self.event_type_id = event_type_id
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.icon_id = icon_id
        self.group_name = group_name
        self.dungeon_id = dungeon_id
        self.url = url
        self.info_jp = info_jp
        self.info_na = info_na
        self.info_kr = info_kr
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]
