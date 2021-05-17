import logging
from typing import Optional

from pad.common.dungeon_types import RawDungeonType
from pad.common.icons import SpecialIcons
from pad.common.shared_types import Server
from pad.db.db_util import DbWrapper
from pad.dungeon.wave_converter import WaveConverter, ResultFloor
from pad.raw.bonus import BonusType
from pad.raw_processor import crossed_data
from pad.raw_processor.crossed_data import CrossServerSubDungeon, CrossServerDungeon
from pad.storage.dungeon import SubDungeonWaveData, DungeonWaveData, SubDungeonRewardData, DungeonRewardData
from pad.storage.encounter import Encounter, Drop
from pad.storage.wave import WaveItem

logger = logging.getLogger('processor')
human_fix_logger = logging.getLogger('human_fix')


class DungeonContentProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.data = data
        self.converter = WaveConverter(data)

    def process(self, db: DbWrapper):
        logger.info('loading dungeon contents')
        self._process_dungeon_contents(db)
        self._process_dungeon_rewards(db)
        # TODO: support multiple rewards

        logger.info('done loading contents')

    def _process_dungeon_contents(self, db: DbWrapper):
        for dungeon in self.data.dungeons:
            if dungeon.dungeon_id % 250 == 0:
                logger.info('scanning dungeon:%s', dungeon.dungeon_id)
            sub_dungeon_items = []

            for sub_dungeon in dungeon.sub_dungeons:
                result_floor = self._compute_result_floor(db, dungeon, sub_dungeon)
                if result_floor:
                    item = SubDungeonWaveData.from_waveresult(result_floor, sub_dungeon)
                    db.insert_or_update(item)
                    sub_dungeon_items.append(item)

                    self._maybe_insert_encounters(db, dungeon, sub_dungeon, result_floor)

            if sub_dungeon_items:
                max_sub_dungeon = max(sub_dungeon_items, key=lambda x: x.sub_dungeon_id)
                item = DungeonWaveData(dungeon_id=dungeon.dungeon_id, icon_id=max_sub_dungeon.icon_id)
                db.insert_or_update(item)

    def _compute_result_floor(self,
                              db: DbWrapper,
                              dungeon: CrossServerDungeon,
                              sub_dungeon: CrossServerSubDungeon) -> Optional[ResultFloor]:
        floor_id = sub_dungeon.sub_dungeon_id % 1000
        sql = 'SELECT * FROM wave_data WHERE dungeon_id={} and floor_id={}'.format(
            dungeon.dungeon_id, floor_id)
        wave_items = db.custom_load_multiple_objects(WaveItem, sql)

        if not wave_items:
            return None

        normal_or_tech = dungeon.cur_dungeon.full_dungeon_type in [RawDungeonType.NORMAL,
                                                                   RawDungeonType.TECHNICAL]
        try_common_monsters = normal_or_tech and dungeon.cur_dungeon.dungeon_id < 1000

        return self.converter.convert(wave_items, try_common_monsters)

    def _maybe_insert_encounters(self,
                                 db: DbWrapper,
                                 dungeon: CrossServerDungeon,
                                 sub_dungeon: CrossServerSubDungeon,
                                 result_floor: ResultFloor):
        for stage in result_floor.stages:
            seen_enemies = set()
            for slot in stage.slots:
                csc = self.data.card_by_monster_id(slot.monster_id)
                card = csc.cur_card.card
                enemy = card.enemy()
                seen_enemies.add(slot.monster_id)

                turns = card.enemy_turns
                if dungeon.cur_dungeon.full_dungeon_type == RawDungeonType.TECHNICAL and card.enemy_turns_alt:
                    turns = card.enemy_turns_alt

                sd = sub_dungeon.cur_sub_dungeon
                hp = int(round(sd.hp_mult * enemy.hp.value_at(slot.monster_level)))
                atk = int(round(sd.atk_mult * enemy.atk.value_at(slot.monster_level)))
                defence = int(round(sd.def_mult * enemy.defense.value_at(slot.monster_level)))
                exp = int(round(enemy.xp.value_at(slot.monster_level)))

                # TODO: add comments based on slot data
                encounter = Encounter(
                    dungeon_id=dungeon.dungeon_id,
                    sub_dungeon_id=sub_dungeon.sub_dungeon_id,
                    enemy_id=slot.monster_id,
                    monster_id=slot.visible_monster_id(),
                    stage=stage.stage_idx,
                    comment_jp=None,
                    comment_na=None,
                    comment_kr=None,
                    amount=slot.min_spawn if slot.min_spawn == slot.max_spawn else None,
                    order_idx=slot.order,
                    turns=turns,
                    level=slot.monster_level,
                    hp=hp,
                    atk=atk,
                    defence=defence,
                    exp=exp)

                sql = '''
                    SELECT encounter_id 
                    FROM encounters 
                    WHERE dungeon_id={} 
                    AND sub_dungeon_id={}
                    AND stage={}
                    AND enemy_id={}
                    AND level={}
                '''.format(dungeon.dungeon_id, sub_dungeon.sub_dungeon_id, stage.stage_idx,
                           slot.monster_id, slot.monster_level)
                stored_encounter_id = db.get_single_value(sql, int, fail_on_empty=False)

                if stored_encounter_id:
                    encounter.encounter_id = stored_encounter_id

                db.insert_or_update(encounter)

                drops = Drop.from_slot(slot, encounter)
                for drop in drops:
                    db.insert_or_update(drop)

            if seen_enemies:
                sql = '''
                    SELECT encounter_id, enemy_id
                    FROM encounters
                    WHERE dungeon_id={}
                    AND sub_dungeon_id={}
                    AND stage={}
                    AND enemy_id not in ({})
                    '''.format(dungeon.dungeon_id, sub_dungeon.sub_dungeon_id, stage.stage_idx,
                               ','.join(map(str, seen_enemies)))
                self._print_bad_enemies('in-stage', dungeon, sub_dungeon, db, sql)

        # In case there are missing stages (e.g. no more invades/commons)
        seen_stage_indexes = [stage.stage_idx for stage in result_floor.stages]
        sql = '''
            SELECT encounter_id, enemy_id
            FROM encounters
            WHERE dungeon_id={}
            AND sub_dungeon_id={}
            AND stage not in ({})
            '''.format(dungeon.dungeon_id, sub_dungeon.sub_dungeon_id, ','.join(map(str, seen_stage_indexes)))
        self._print_bad_enemies('out-stage', dungeon, sub_dungeon, db, sql)

    def _print_bad_enemies(self, desc: str, dungeon, sub_dungeon, db: DbWrapper, sql: str):
        bad_stored_encounters = db.fetch_data(sql)
        if not bad_stored_encounters:
            return

        encounter_list_str = ','.join([str(x['encounter_id']) for x in bad_stored_encounters])
        encounter_info_list_str = ','.join(
            ['{}/{}'.format(x['encounter_id'], x['enemy_id']) for x in bad_stored_encounters])
        delete_drops_sql = 'DELETE FROM drops WHERE encounter_id IN ({});'.format(encounter_list_str)
        delete_encounters_sql = 'DELETE FROM encounters WHERE encounter_id IN ({});'.format(
            encounter_list_str)
        human_fix_logger.warning('Found bad %s stored encounters for %s: [%s] - %s\n%s\n%s',
                                 desc,
                                 dungeon.na_dungeon.clean_name,
                                 sub_dungeon.na_sub_dungeon.clean_name,
                                 encounter_info_list_str,
                                 delete_drops_sql,
                                 delete_encounters_sql)

        deleted_drops = db.update_item(delete_drops_sql)
        deleted_encounters = db.update_item(delete_encounters_sql)
        human_fix_logger.warning('Auto deleted {} drops and {} encounters'.format(deleted_drops, deleted_encounters))

    def _process_dungeon_rewards(self, db):
        def is_floor_bonus(x):
            return x.dungeon and x.bonus.bonus_info.bonus_type == BonusType.dungeon_floor_text

        # Get the bonuses from all servers that have a dungeon attached, and 'floor text'.
        # Might need an additional filter for dungeons, perhaps 'dungeon_special_event'?
        all_bonuses = self.data.jp_bonuses + self.data.na_bonuses + self.data.kr_bonuses
        floor_bonuses = list(filter(is_floor_bonus, all_bonuses))

        # Stick all the monster names, from all languages, lowercased, into a lookup map.
        monster_name_to_id = {x.jp_card.card.name: x for x in self.data.ownable_cards}
        monster_name_to_id.update({x.na_card.card.name: x for x in self.data.ownable_cards})
        monster_name_to_id.update({x.kr_card.card.name: x for x in self.data.ownable_cards})
        monster_name_to_id = {x.lower(): y for x, y in monster_name_to_id.items()}

        for merged_bonus in floor_bonuses:
            raw_text = merged_bonus.bonus.clean_message
            text = raw_text.lower()
            has_reward = any(item in text for item in ['reward', 'first time clear', '初クリア報酬'])
            if not has_reward:
                continue

            reward_value = None
            if 'coins' in text or '万コイン' in text:
                reward_value = SpecialIcons.Coin.value
            elif 'pal points' in text or '友情ポイント' in text:
                reward_value = SpecialIcons.Point.value
            elif 'dungeon' in text:
                reward_value = SpecialIcons.QuestionMark.value
            elif '+ points' in text or '+ポイント' in text:
                reward_value = SpecialIcons.StarPlusEgg.value
            elif 'magic stone' in text:
                reward_value = SpecialIcons.MagicStone.value
            else:
                matched_monsters = set()
                for m_name in monster_name_to_id.keys():
                    if m_name in text:
                        matched_monsters.add(m_name)
                if matched_monsters:
                    best_match = max(matched_monsters, key=len)
                    reward_value = monster_name_to_id[best_match].monster_id

            if merged_bonus.bonus.sub_dungeon_id:
                # Primarily we update sub dungeons.
                saved_data = db.load_single_object(SubDungeonRewardData, merged_bonus.bonus.sub_dungeon_id)
                reward_value = reward_value or SpecialIcons.RedX.value
                saved_data.reward_icon_ids = str(reward_value)
            else:
                saved_data = db.load_single_object(DungeonRewardData, merged_bonus.bonus.dungeon_id)
                # Dungeons shouldn't get X's on parsing failures.
                # Also shouldn't override if we parsed one previously but this failed.
                if reward_value:
                    saved_data.reward_icon_ids = str(reward_value)

            # Fix the proper text for server this bonus is tagged with.
            if merged_bonus.server == Server.jp:
                saved_data.reward_jp = raw_text
            elif merged_bonus.server == Server.na:
                saved_data.reward_na = raw_text
            elif merged_bonus.server == Server.kr:
                saved_data.reward_kr = raw_text

            # Apply overwrites from other servers if we don't have a good one.
            saved_data.reward_jp = saved_data.reward_jp or saved_data.reward_na or saved_data.reward_kr
            saved_data.reward_na = saved_data.reward_na or saved_data.reward_jp or saved_data.reward_kr
            saved_data.reward_kr = saved_data.reward_kr or saved_data.reward_na or saved_data.reward_jp

            # Update the value if necessary.
            db.insert_or_update(saved_data)
