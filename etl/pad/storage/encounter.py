from pad.db.sql_item import SimpleSqlItem, ExistsStrategy


class Encounter(SimpleSqlItem):
    """A monster that appears in a dungeon."""
    TABLE = 'encounters'
    KEY_COL = 'encounter_id'

    def __init__(self,
                 encounter_id: int = None,
                 dungeon_id: int = None,
                 sub_dungeon_id: int = None,
                 enemy_id: int = None,
                 monster_id: int = None,
                 stage: int = None,
                 comment_jp: str = None,
                 comment_na: str = None,
                 comment_kr: str = None,
                 amount: int = None,
                 order_idx: int = None,
                 turn: int = None,
                 level: int = None,
                 hp: int = None,
                 atk: int = None,
                 defence: int = None,
                 tstamp: int = None):
        self.encounter_id = encounter_id
        self.dungeon_id = dungeon_id
        self.sub_dungeon_id = sub_dungeon_id
        self.enemy_id = enemy_id
        self.monster_id = monster_id
        self.stage = stage
        self.comment_jp = comment_jp
        self.comment_na = comment_na
        self.comment_kr = comment_kr
        self.amount = amount
        self.order_idx = order_idx
        self.turn = turn
        self.level = level
        self.hp = hp
        self.atk = atk
        self.defence = defence
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.CUSTOM
