from pad.db.sql_item import SimpleSqlItem


class Series(SimpleSqlItem):
    """A monster series."""
    TABLE = 'series'
    KEY_COL = 'series_id'
    UNSORTED_SERIES_ID = 0

    def __init__(self,
                 series_id: int = None,
                 name_jp: str = None,
                 name_na: str = None,
                 name_kr: str = None,
                 tstamp: int = None):
        self.series_id = series_id
        self.name_jp = name_jp
        self.name_na = name_na
        self.name_kr = name_kr
        self.tstamp = tstamp
