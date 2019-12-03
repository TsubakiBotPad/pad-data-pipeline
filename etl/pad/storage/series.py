from pad.db.sql_item import SimpleSqlItem


class Series(SimpleSqlItem):
    """A monster series."""
    TABLE = 'series'
    KEY_COL = 'series_id'
    UNSORTED_SERIES_ID = 0

    @staticmethod
    def from_json(o):
        return Series(series_id=o['series_id'],
                      name_jp=o['name_jp'],
                      name_na=o['name_na'],
                      name_kr=o['name_kr'])

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

    def __str__(self):
        return 'Series ({}): {}'.format(self.key_value(), self.name_na)
