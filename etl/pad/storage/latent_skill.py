from pad.db.sql_item import SimpleSqlItem
from pad.raw_processor.crossed_data import CrossServerCard


class LatentSkill(SimpleSqlItem):
    """Monster latent."""
    TABLE = 'latent_skills'
    KEY_COL = 'latent_skill_id'

    @staticmethod
    def from_json(o):
        return LatentSkill(latent_skill_id=o['latent_skill_id'],
                           name_ja=o['name_ja'],
                           name_en=o['name_en'],
                           name_ko=o['name_ko'],
                           desc_ja=o['desc_ja'],
                           desc_en=o['desc_en'],
                           desc_ko=o['desc_ko'],
                           slots=o['slots'],
                           required_awakening=o['required_awakening'],
                           required_types=o['required_types'],
                           required_level=o['required_level'],
                           has_120_boost=o['has_120_boost'])

    def __init__(self,
                 latent_skill_id: int = None,
                 name_ja=None,
                 name_en: str = None,
                 name_ko: str = None,
                 desc_ja: str = None,
                 desc_en: str = None,
                 desc_ko: str = None,
                 slots: int = None,
                 required_awakening: int = None,
                 required_types: int = None,
                 required_level: int = None,
                 has_120_boost: bool = None,
                 monster_id: int = None,
                 tstamp: int = None):
        self.latent_skill_id = latent_skill_id
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.desc_ja = desc_ja
        self.desc_en = desc_en
        self.desc_ko = desc_ko
        self.slots = slots
        self.required_awakening = required_awakening
        self.required_types = required_types
        self.required_level = required_level
        self.has_120_boost = has_120_boost
        self.monster_id = monster_id
        self.tstamp = tstamp

    def __str__(self):
        return 'LatentSkill({}): {}'.format(self.key_value(), self.name_en)
