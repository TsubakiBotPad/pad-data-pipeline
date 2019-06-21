from pad.db.sql_item import SimpleSqlItem


class AwokenSkill(SimpleSqlItem):
    """Monster awakening."""
    TABLE = 'awoken_skills'
    KEY_COL = 'awoken_skill_id'

    @staticmethod
    def from_json(o):
        return AwokenSkill(awoken_skill_id=o['pad_awakening_id'],
                           name_jp=o['name_jp'],
                           name_na=o['name_na'],
                           name_kr=o['name_kr'],
                           desc_jp=o['desc_jp'],
                           desc_na=o['desc_na'],
                           desc_kr=o['desc_kr'],
                           adj_hp=o['adj_hp'],
                           adj_atk=o['adj_atk'],
                           adj_rcv=o['adj_rcv'])

    def __init__(self,
                 awoken_skill_id: int = None,
                 name_jp=None,
                 name_na: str = None,
                 name_kr: str = None,
                 desc_jp: str = None,
                 desc_na: str = None,
                 desc_kr: str = None,
                 adj_hp: int = None,
                 adj_atk: int = None,
                 adj_rcv: int = None,
                 tstamp: int = None):
        self.awoken_skill_id = awoken_skill_id
        self.name_jp = name_jp
        self.name_na = name_na
        self.name_kr = name_kr
        self.desc_jp = desc_jp
        self.desc_na = desc_na
        self.desc_kr = desc_kr
        self.adj_hp = adj_hp
        self.adj_atk = adj_atk
        self.adj_rcv = adj_rcv
        self.tstamp = tstamp
