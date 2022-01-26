from typing import List

from pad.common.monster_id_mapping import server_monster_id_fn
from pad.db.sql_item import ExistsStrategy
from pad.dungeon.wave_converter import ResultFloor
from pad.raw_processor.crossed_data import CrossServerDungeon, CrossServerSubDungeon
from pad.storage_processor.shared_storage import ServerDependentSqlItem


class Dungeon(ServerDependentSqlItem):
    """Dungeon top-level item."""
    KEY_COL = 'dungeon_id'
    BASE_TABLE = 'dungeons'

    @staticmethod
    def from_csd(o: CrossServerDungeon) -> 'Dungeon':
        return Dungeon(
            dungeon_id=o.dungeon_id,
            name_ja=o.jp_dungeon.clean_name,
            name_en=o.na_dungeon.clean_name,
            name_ko=o.kr_dungeon.clean_name,
            dungeon_type=o.cur_dungeon.full_dungeon_type.value,
            visible=True)

    def __init__(self,
                 dungeon_id: int = None,
                 name_ja: str = None,
                 name_en: str = None,
                 name_ko: str = None,
                 dungeon_type: int = None,
                 visible: bool = None,
                 tstamp: int = None):
        self.dungeon_id = dungeon_id
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.dungeon_type = dungeon_type
        self.visible = visible
        self.tstamp = tstamp

    def _non_auto_update_cols(self):
        return ['visible']

    def __str__(self):
        return 'Dungeon({}): {}'.format(self.key_value(), self.name_en)


class DungeonWaveData(ServerDependentSqlItem):
    """Dungeon data that can only be computed from waves."""
    KEY_COL = 'dungeon_id'
    BASE_TABLE = 'dungeons'

    def __init__(self,
                 dungeon_id: int = None,
                 icon_id: int = None,
                 tstamp: int = None):
        self.dungeon_id = dungeon_id
        self.icon_id = icon_id
        self.tstamp = tstamp


class DungeonRewardData(ServerDependentSqlItem):
    """Dungeon data that can only be computed from bonus floor text."""
    KEY_COL = 'dungeon_id'
    BASE_TABLE = 'dungeons'

    def __init__(self,
                 dungeon_id: int = None,
                 reward_jp: str = None,
                 reward_na: str = None,
                 reward_kr: str = None,
                 reward_icon_ids: str = None,
                 tstamp: int = None,
                 **unused_args):
        self.dungeon_id = dungeon_id
        self.reward_jp = reward_jp
        self.reward_na = reward_na
        self.reward_kr = reward_kr
        self.reward_icon_ids = reward_icon_ids
        self.tstamp = tstamp

    def __str__(self):
        return 'DungeonReward({}): {} - {}'.format(self.key_value(), self.reward_na, self.reward_icon_ids)


class SubDungeon(ServerDependentSqlItem):
    """Per-difficulty dungeon section."""
    KEY_COL = 'sub_dungeon_id'
    BASE_TABLE = 'sub_dungeons'

    @staticmethod
    def from_csd(o: CrossServerDungeon) -> List['SubDungeon']:
        results = []
        for sd in o.sub_dungeons:
            results.append(SubDungeon(
                sub_dungeon_id=sd.sub_dungeon_id,
                dungeon_id=o.dungeon_id,
                name_ja=sd.jp_sub_dungeon.clean_name,
                name_en=sd.na_sub_dungeon.clean_name,
                name_ko=sd.kr_sub_dungeon.clean_name,
                floors=sd.cur_sub_dungeon.floors,
                stamina=sd.cur_sub_dungeon.stamina,
                hp_mult=sd.cur_sub_dungeon.hp_mult,
                atk_mult=sd.cur_sub_dungeon.atk_mult,
                def_mult=sd.cur_sub_dungeon.def_mult,
                s_rank=sd.cur_sub_dungeon.score,
                technical=sd.cur_sub_dungeon.technical))
        return results

    def __init__(self,
                 sub_dungeon_id: int = None,
                 dungeon_id: int = None,
                 name_ja: str = None,
                 name_en: str = None,
                 name_ko: str = None,
                 floors: int = None,
                 stamina: int = None,
                 hp_mult: float = None,
                 atk_mult: float = None,
                 def_mult: float = None,
                 s_rank: int = None,
                 technical: bool = None,
                 tstamp: int = None):
        self.sub_dungeon_id = sub_dungeon_id
        self.dungeon_id = dungeon_id
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.floors = floors
        self.stamina = stamina
        self.hp_mult = hp_mult
        self.atk_mult = atk_mult
        self.def_mult = def_mult
        self.s_rank = s_rank
        self.technical = technical
        self.tstamp = tstamp

    def __str__(self):
        return 'SubDungeon({}): {}'.format(self.key_value(), self.name_en)


class SubDungeonWaveData(ServerDependentSqlItem):
    """Sub-dungeon data that can only be computed from waves."""
    KEY_COL = 'sub_dungeon_id'
    BASE_TABLE = 'sub_dungeons'

    @staticmethod
    def from_waveresult(o: ResultFloor, cssd: CrossServerSubDungeon) -> 'SubDungeonWaveData':
        return SubDungeonWaveData(
            sub_dungeon_id=cssd.sub_dungeon_id,
            coin_max=o.coins_max,
            coin_min=o.coins_min,
            coin_avg=o.coins_avg,
            exp_max=o.exp_max,
            exp_min=o.exp_min,
            exp_avg=o.exp_avg,
            mp_avg=o.mp_avg,
            icon_id=o.boss_monster_id())

    def __init__(self,
                 sub_dungeon_id: int = None,
                 coin_max: int = None,
                 coin_min: int = None,
                 coin_avg: int = None,
                 exp_max: int = None,
                 exp_min: int = None,
                 exp_avg: int = None,
                 mp_avg: int = None,
                 icon_id: int = None,
                 tstamp: int = None):
        self.sub_dungeon_id = sub_dungeon_id
        self.coin_max = coin_max
        self.coin_min = coin_min
        self.coin_avg = coin_avg
        self.exp_max = exp_max
        self.exp_min = exp_min
        self.exp_avg = exp_avg
        self.mp_avg = mp_avg
        self.icon_id = icon_id
        self.tstamp = tstamp

    def __str__(self):
        return 'SDWaveData({}): {}'.format(self.key_value(), self.icon_id)


class SubDungeonRewardData(ServerDependentSqlItem):
    """Sub-dungeon data that can only be computed from bonus floor text."""
    KEY_COL = 'sub_dungeon_id'
    BASE_TABLE = 'sub_dungeons'

    def __init__(self,
                 sub_dungeon_id: int = None,
                 reward_jp: str = None,
                 reward_na: str = None,
                 reward_kr: str = None,
                 reward_icon_ids: str = None,
                 tstamp: int = None,
                 **unused_args):
        self.sub_dungeon_id = sub_dungeon_id
        self.reward_jp = reward_jp
        self.reward_na = reward_na
        self.reward_kr = reward_kr
        self.reward_icon_ids = reward_icon_ids
        self.tstamp = tstamp

    def __str__(self):
        return 'SDRewardData({}): {}'.format(self.key_value(), self.reward_na)


class FixedTeam(ServerDependentSqlItem):
    """A fixed team within a dungeon."""
    KEY_COL = 'fixed_team_id'
    BASE_TABLE = 'fixed_teams'

    @staticmethod
    def from_cssd(sd: CrossServerSubDungeon) -> 'SubDungeon':
        return FixedTeam(
            fixed_team_id=sd.sub_dungeon_id,
            sub_dungeon_id=sd.sub_dungeon_id)

    def __init__(self,
                 fixed_team_id: int = None,
                 sub_dungeon_id: int = None):
        self.fixed_team_id = fixed_team_id
        self.sub_dungeon_id = sub_dungeon_id
        self.tstamp = None

    def __str__(self):
        return 'FixedTeam({})'.format(self.key_value())


class FixedTeamMonster(ServerDependentSqlItem):
    """A fixed monster in a subdungeon fixed team."""
    KEY_COL = 'fixed_team_monster_id'
    BASE_TABLE = 'fixed_team_monsters'

    @staticmethod
    def from_fc(o: Optional[FixedCardObject], idx: int, cssd: CrossServerSubDungeon) -> 'FixedTeamMonster':
        if o is None:
            return FixedTeamMonster(
                fixed_team_id=cssd.sub_dungeon_id,
                fixed_slot_type_id=0,
                order_idx=idx)
        if not o.monster_id:
            return FixedTeamMonster(
                fixed_team_id=cssd.sub_dungeon_id,
                fixed_slot_type_id=1,
                order_idx=idx)
        return FixedTeamMonster(
            fixed_team_id=cssd.sub_dungeon_id,
            fixed_slot_type_id=2,
            alt_monster_id=server_monster_id_fn(cssd.server)(o.monster_id),
            monster_level=o.level,
            plus_hp=o.plus_hp,
            plus_atk=o.plus_atk,
            plus_rcv=o.plus_rcv,
            awakening_count=o.awakening_count,
            skill_level=o.skill_level,
            assist_alt_monster_id=o.assist,
            super_awakening_id=o.super_awakening_id,
            order_idx=idx)

    def __init__(self,
                 fixed_team_monster_id: int = None,
                 fixed_team_id: int = None,
                 fixed_slot_type_id: int = None,
                 alt_monster_id: Optional[int] = None,
                 monster_level: Optional[int] = None,
                 plus_hp: Optional[int] = None,
                 plus_atk: Optional[int] = None,
                 plus_rcv: Optional[int] = None,
                 awakening_count: Optional[int] = None,
                 skill_level: Optional[int] = None,
                 assist_alt_monster_id: Optional[int] = None,
                 super_awakening_id: Optional[int] = None,
                 order_idx: int = None,
                 tstamp: int = None):
        self.fixed_team_monster_id = fixed_team_monster_id
        self.fixed_team_id = fixed_team_id
        self.fixed_slot_type_id = fixed_slot_type_id
        self.alt_monster_id = alt_monster_id
        self.monster_level = monster_level
        self.plus_hp = plus_hp
        self.plus_atk = plus_atk
        self.plus_rcv = plus_rcv
        self.awakening_count = awakening_count
        self.skill_level = skill_level
        self.assist_alt_monster_id = assist_alt_monster_id
        self.super_awakening_id = super_awakening_id
        self.order_idx = order_idx
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

    def _lookup_columns(self):
        return ['fixed_team_id', 'order_idx']

    def __str__(self):
        return 'FixedCard({}): {} in {} (#{})'.format(
            self.key_value(), self.alt_monster_id,
            self.fixed_team_id, self.order_idx)
