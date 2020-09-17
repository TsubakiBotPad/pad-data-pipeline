from pad.db.sql_item import SimpleSqlItem


class AwokenSkill(SimpleSqlItem):
    """Monster awakening."""
    TABLE = 'awoken_skills'
    KEY_COL = 'awoken_skill_id'

    @staticmethod
    def from_json(o):
        return AwokenSkill(awoken_skill_id=o['pad_awakening_id'],
                           name_ja=o['name_ja'],
                           name_en=o['name_en'],
                           name_ko=o['name_ko'],
                           desc_ja=o['desc_ja'],
                           desc_en=o['desc_en'],
                           desc_ko=o['desc_ko'],
                           adj_hp=o['adj_hp'],
                           adj_atk=o['adj_atk'],
                           adj_rcv=o['adj_rcv'])

    def __init__(self,
                 awoken_skill_id: int = None,
                 name_ja=None,
                 name_en: str = None,
                 name_ko: str = None,
                 desc_ja: str = None,
                 desc_en: str = None,
                 desc_ko: str = None,
                 adj_hp: int = None,
                 adj_atk: int = None,
                 adj_rcv: int = None,
                 tstamp: int = None):
        self.awoken_skill_id = awoken_skill_id
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.desc_ja = desc_ja
        self.desc_en = desc_en
        self.desc_ko = desc_ko
        self.adj_hp = adj_hp
        self.adj_atk = adj_atk
        self.adj_rcv = adj_rcv
        self.tstamp = tstamp

    def __str__(self):
        return 'AwokenSkill({}): {}'.format(self.key_value(), self.name_en)
