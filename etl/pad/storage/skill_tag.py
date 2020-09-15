from pad.db.sql_item import SimpleSqlItem


class ActiveSkillTag(SimpleSqlItem):
    """Tags for active skills."""
    TABLE = 'active_skill_tags'
    KEY_COL = 'active_skill_tag_id'

    @staticmethod
    def from_json(o):
        return ActiveSkillTag(active_skill_tag_id=o['active_tag_id'],
                              name_ja=o['name_ja'],
                              name_en=o['name_en'],
                              name_ko=o['name_ko'],
                              order_idx=o['order_idx'])

    def __init__(self,
                 active_skill_tag_id: int = None,
                 name_ja=None,
                 name_en: str = None,
                 name_ko: str = None,
                 order_idx: int = None,
                 tstamp: int = None):
        self.active_skill_tag_id = active_skill_tag_id
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.order_idx = order_idx
        self.tstamp = tstamp

    def __str__(self):
        return 'ActiveSkillTag({}): {}'.format(self.key_value(), self.name_en)


class LeaderSkillTag(SimpleSqlItem):
    """Tags for leader skills."""
    TABLE = 'leader_skill_tags'
    KEY_COL = 'leader_skill_tag_id'

    @staticmethod
    def from_json(o):
        return LeaderSkillTag(leader_skill_tag_id=o['leader_tag_id'],
                              name_ja=o['name_ja'],
                              name_en=o['name_en'],
                              name_ko=o['name_ko'],
                              order_idx=o['order_idx'])

    def __init__(self,
                 leader_skill_tag_id: int = None,
                 name_ja=None,
                 name_en: str = None,
                 name_ko: str = None,
                 order_idx: int = None,
                 tstamp: int = None):
        self.leader_skill_tag_id = leader_skill_tag_id
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.order_idx = order_idx
        self.tstamp = tstamp

    def __str__(self):
        return 'LeaderSkillTag({}): {}'.format(self.key_value(), self.name_en)
