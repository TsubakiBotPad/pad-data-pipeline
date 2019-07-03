import logging
from typing import Optional

from pad.common.dungeon_types import RawDungeonType
from pad.db.db_util import DbWrapper
from pad.dungeon.wave_converter import WaveConverter, ResultFloor, ResultSlot
from pad.raw_processor import crossed_data
from pad.raw_processor.crossed_data import CrossServerSubDungeon, CrossServerDungeon
from pad.storage.dungeon import SubDungeonWaveData, DungeonWaveData
from pad.storage.encounter import Encounter
from pad.storage.wave import WaveItem

logger = logging.getLogger('processor')


class DungeonContentProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.data = data
        self.converter = WaveConverter(data)

    def process(self, db: DbWrapper):
        logger.warning('loading dungeon contents')
        self._process_dungeon_contents(db)
        # TODO: support rewards
        # TODO: support drops
        # TODO: support updates to encounters
        # TODO: support updates to drops

        logger.warning('done loading contents')

    def _process_dungeon_contents(self, db: DbWrapper):
        for dungeon in self.data.dungeons:
            if dungeon.dungeon_id % 250 == 0:
                logger.warning('scanning dungeon:%s', dungeon.dungeon_id)
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

        return self.converter.convert(wave_items)

    def _maybe_insert_encounters(self,
                                 db: DbWrapper,
                                 dungeon: CrossServerDungeon,
                                 sub_dungeon: CrossServerSubDungeon,
                                 result_floor: ResultFloor):
        sql = 'SELECT count(*) FROM encounters WHERE dungeon_id={} and sub_dungeon_id={}'.format(
            dungeon.dungeon_id, sub_dungeon.sub_dungeon_id)
        encounter_count = db.get_single_value(sql, int)
        if encounter_count:
            logger.debug('Skipping encounter insert for {}-{}'.format(dungeon.dungeon_id, sub_dungeon.sub_dungeon_id))
            return

        logger.warning('Executing encounter insert for {}-{}'.format(dungeon.dungeon_id, sub_dungeon.sub_dungeon_id))
        for stage in result_floor.stages:
            for slot in stage.slots:
                csc = self.data.card_by_monster_id(slot.monster_id)
                card = csc.jp_card.card
                enemy = card.enemy()

                turns = card.enemy_turns
                if dungeon.jp_dungeon.full_dungeon_type == RawDungeonType.TECHNICAL and card.enemy_turns_alt:
                    turns = card.enemy_turns_alt

                sd = sub_dungeon.jp_sub_dungeon
                hp = int(round(sd.hp_mult * enemy.hp.value_at(slot.monster_level)))
                atk = int(round(sd.atk_mult * enemy.atk.value_at(slot.monster_level)))
                defence = int(round(sd.def_mult * enemy.defense.value_at(slot.monster_level)))

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
                    amount=slot.min_spawn if slot.min_spawn==slot.max_spawn else None,
                    order_idx=slot.order,
                    turns=turns,
                    hp=hp,
                    atk=atk,
                    defence=defence)

                db.insert_or_update(encounter, force_insert=True)



    # floor_text = floor_text.lower()
    # reward_value = None
    # if 'reward' in floor_text or 'first time clear' in floor_text or '初クリア報酬' in floor_text:
    #     if 'coins' in floor_text or '万コイン' in floor_text:
    #         reward_value = SpecialIcons.Coin.value
    #     elif 'pal points' in floor_text or '友情ポイント' in floor_text:
    #         reward_value = SpecialIcons.Point.value
    #     elif 'dungeon' in floor_text:
    #         reward_value = SpecialIcons.QuestionMark.value
    #     elif '+ points' in floor_text or '+ポイント' in floor_text:
    #         reward_value = SpecialIcons.StarPlusEgg.value
    #     elif 'magic stone' in floor_text:
    #         reward_value = SpecialIcons.MagicStone.value
    #     else:
    #         matched_monsters = set()
    #         for m_name in monster_name_to_id.keys():
    #             if m_name in floor_text:
    #                 matched_monsters.add(m_name)
    #         if matched_monsters:
    #             best_match = max(matched_monsters, key=len)
    #             reward_value = monster_name_to_id[best_match].card_id
    #
    #     if reward_value is None:
    #         reward_value = SpecialIcons.RedX.value
    #
    # if reward_value:
    #     # TODO: support 1/2 reward types?
    #     reward_text = '0/{}'.format(reward_value)
    #     if sub_dungeon.resolved_sub_dungeon_reward is None:
    #         sub_dungeon.resolved_sub_dungeon_reward = dbdungeon.SubDungeonReward()
    #     sub_dungeon.resolved_sub_dungeon_reward.data = reward_text
    #
    #             # Sort the other drops for indexing purposes
    #             other_drops = list(sorted(other_drops))
    #
    #             existing_drops = {
    #                 int(ed.monster_no): ed for ed in monster.resolved_dungeon_monster_drops}
    #
    #             for drop in other_drops:
    #                 if int(drop) in existing_drops:
    #                     dmd = existing_drops.pop(drop)
    #                 else:
    #                     dmd = dbdungeon.DungeonMonsterDrop()
    #                     monster.resolved_dungeon_monster_drops.append(dmd)
    #                 dmd.monster_no = drop
    #                 dmd.order_idx = drop
    #                 dmd.status = 0

