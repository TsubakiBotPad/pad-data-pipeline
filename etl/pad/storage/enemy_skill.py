from dadguide_proto.enemy_skills_pb2 import MonsterBehavior
from pad.db.sql_item import SimpleSqlItem
from pad.raw_processor.crossed_data import CrossServerESInstance
from pad.raw.skills.jp.enemy_skill_text import JpESTextConverter
from pad.raw.skills.en.enemy_skill_text import EnESTextConverter
#from pad.raw.skills.kr.enemy_skill_text import KrESTextConverter

class EnemySkill(SimpleSqlItem):
    """Enemy skill data."""
    TABLE = 'enemy_skills'
    KEY_COL = 'enemy_skill_id'

    @staticmethod
    def from_json(o):
        return EnemySkill(enemy_skill_id=o['enemy_skill_id'],
                          name_jp=o['name_jp'],
                          name_na=o['name_na'],
                          name_kr=o['name_kr'],
                          desc_jp=o['desc_jp'],
                          desc_na=o['desc_na'],
                          desc_kr=o['desc_kr'],
                          min_hits=o['min_hits'],
                          max_hits=o['max_hits'],
                          atk_mult=o['atk_mult'])

    @staticmethod
    def from_cseb(o: CrossServerESInstance) -> 'EnemySkill':
        exemplar = o.jp_skill.behavior

        has_attack = hasattr(exemplar, 'attack') and exemplar.attack
        min_hits = exemplar.attack.min_hits if has_attack else 0
        max_hits = exemplar.attack.max_hits if has_attack else 0
        atk_mult = exemplar.attack.atk_multiplier if has_attack else 0

        jp_desc = exemplar.full_description(JpESTextConverter())
        en_desc = exemplar.full_description(EnESTextConverter())
       #kr_desc = exemplar.full_description(KrESTextConverter())
        
        return EnemySkill(
            enemy_skill_id=o.enemy_skill_id,
            name_jp=o.jp_skill.name,
            name_na=o.na_skill.name,
            name_kr=o.kr_skill.name,
            desc_jp=jp_desc,
            desc_na=en_desc,
            desc_kr=en_desc,
            min_hits=min_hits,
            max_hits=max_hits,
            atk_mult=atk_mult)

    def __init__(self,
                 enemy_skill_id: int = None,
                 name_jp: str = None,
                 name_na: str = None,
                 name_kr: str = None,
                 desc_jp: str = None,
                 desc_na: str = None,
                 desc_kr: str = None,
                 min_hits: int = None,
                 max_hits: int = None,
                 atk_mult: int = None,
                 tstamp: int = None):
        self.enemy_skill_id = enemy_skill_id
        self.name_jp = name_jp
        self.name_na = name_na
        self.name_kr = name_kr
        self.desc_jp = desc_jp
        self.desc_na = desc_na
        self.desc_kr = desc_kr
        self.min_hits = min_hits
        self.max_hits = max_hits
        self.atk_mult = atk_mult
        self.tstamp = tstamp

    def __str__(self):
        return 'EnemySkill({}): {} - {}'.format(self.key_value(), self.name_na, self.desc_na)


class EnemyData(SimpleSqlItem):
    """Enemy skill data."""
    TABLE = 'enemy_data'
    KEY_COL = 'enemy_id'

    @staticmethod
    def from_mb(o: MonsterBehavior, status: int) -> 'EnemyData':
        return EnemyData(
            enemy_id=o.monster_id,
            status=status,
            behavior=o.SerializeToString())

    def __init__(self,
                 enemy_id: int = None,
                 status: int = None,
                 behavior: str = None,
                 tstamp: int = None):
        self.enemy_id = enemy_id
        self.status = status
        self.behavior = behavior
        self.tstamp = tstamp

    def __str__(self):
        return 'EnemyData({}): {}'.format(self.key_value(), len(self.behavior))
