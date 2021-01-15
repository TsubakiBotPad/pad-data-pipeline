from pad.db.sql_item import SimpleSqlItem


class Series(SimpleSqlItem):
    """A monster series."""
    TABLE = 'series'
    KEY_COL = 'series_id'
    UNSORTED_SERIES_ID = 0

    @staticmethod
    def from_json(o):
        return Series(series_id=o['series_id'],
                      name_ja=o['name_ja'],
                      name_en=o['name_en'],
                      name_ko=o['name_ko'],
                      series_type=o['series_type'])

    def __init__(self,
                 series_id: int = None,
                 name_ja: str = None,
                 name_en: str = None,
                 name_ko: str = None,
                 series_type: str = None,
                 tstamp: int = None):
        self.series_id = series_id
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.series_type = series_type
        self.tstamp = tstamp

    def __str__(self):
        return 'Series ({}): {}'.format(self.key_value(), self.name_en)
