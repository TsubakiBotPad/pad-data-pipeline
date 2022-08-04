import json

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
                           name_ja_official=o['name_ja_official'],
                           name_en_official=o['name_en_official'],
                           name_ko_official=o['name_ko_official'],
                           desc_ja_official=o['desc_ja_official'],
                           desc_en_official=o['desc_en_official'],
                           desc_ko_official=o['desc_ko_official'],
                           slots=o['slots'],
                           required_awakening=o['required_awakening'],
                           required_types=o['required_types'],
                           required_level=o['required_level'],
                           has_120_boost=o['has_120_boost'])

    def __init__(self,
                 latent_skill_id: int = None,
                 name_ja: str = None,
                 name_en: str = None,
                 name_ko: str = None,
                 desc_ja: str = None,
                 desc_en: str = None,
                 desc_ko: str = None,
                 name_ja_official: str = None,
                 name_en_official: str = None,
                 name_ko_official: str = None,
                 desc_ja_official: str = None,
                 desc_en_official: str = None,
                 desc_ko_official: str = None,
                 slots: int = None,
                 required_awakening: int = None,
                 required_types: list = None,
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
        self.name_ja_official = name_ja_official
        self.name_en_official = name_en_official
        self.name_ko_official = name_ko_official
        self.desc_ja_official = desc_ja_official
        self.desc_en_official = desc_en_official
        self.desc_ko_official = desc_ko_official
        self.slots = slots
        self.required_awakening = required_awakening
        self.required_types = json.dumps(required_types)
        self.required_level = required_level
        self.has_120_boost = has_120_boost
        self.monster_id = monster_id
        self.tstamp = tstamp

    def _non_auto_update_cols(self):
        return ['monster_id']

    def _json_cols(self):
        return ['required_types']

    def __str__(self):
        return 'LatentSkill({}): {}'.format(self.key_value(), self.name_en)
