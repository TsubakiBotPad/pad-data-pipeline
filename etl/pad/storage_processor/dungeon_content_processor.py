import logging
from typing import Optional

from pad.db.db_util import DbWrapper
from pad.dungeon.wave_converter import WaveConverter
from pad.raw_processor import crossed_data
from pad.raw_processor.crossed_data import CrossServerSubDungeon, CrossServerDungeon
from pad.storage.dungeon import SubDungeonWaveData, DungeonWaveData
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
        # TODO: support encounters
        # TODO: support drops
        logger.warning('done loading contents')

    def _process_dungeon_contents(self, db: DbWrapper):
        for dungeon in self.data.dungeons:
            sub_dungeon_items = []

            for sub_dungeon in dungeon.sub_dungeons:
                item = self._compute_sub_dungeon_content(db, dungeon, sub_dungeon)
                if item:
                    db.insert_or_update(item)
                    sub_dungeon_items.append(item)

            if sub_dungeon_items:
                max_sub_dungeon = max(sub_dungeon_items, key=lambda x: x.sub_dungeon_id)
                item = DungeonWaveData(dungeon_id=dungeon.dungeon_id, icon_id=max_sub_dungeon.icon_id)
                db.insert_or_update(item)

    def _compute_sub_dungeon_content(self,
                                     db: DbWrapper,
                                     dungeon: CrossServerDungeon,
                                     sub_dungeon: CrossServerSubDungeon) -> Optional[SubDungeonWaveData]:
        sql = 'SELECT * FROM wave_data WHERE dungeon_id={} and floor_id={}'.format(
            dungeon.dungeon_id, sub_dungeon.sub_dungeon_id)
        wave_items = db.custom_load_multiple_objects(WaveItem, sql)

        if not wave_items:
            return None

        result_floor = self.converter.convert(wave_items)
        return SubDungeonWaveData.from_waveresult(result_floor, sub_dungeon)

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
    # monster_tree = make_tree_from_cards(monster_id_to_card.values())
    #
    # for stage in result_stages:
    #     existing = filter(lambda dm: dm.floor == stage.stage_idx,
    #                       sub_dungeon.resolved_dungeon_monsters)
    #     existing_id_to_monster = {dm.monster_no: dm for dm in existing}
    #     for slot in stage.slots:
    #         card = monster_id_to_card[slot.monster_id]
    #
    #         # TODO: this might need mapping due to na/jp skew for monster_no
    #         monster_id = slot.monster_id
    #         monster_id = monster_id % 10000 if monster_id > 9999 else monster_id
    #
    #         if monster_id <= 0:
    #             raise Exception('Bad monster ID', slot.monster_id, card.card_id, card.base_id)
    #
    #         monster = existing_id_to_monster.get(monster_id)
    #         if not monster:
    #             monster = dbdungeon.DungeonMonster()
    #             monster.monster_no = monster_id
    #             sub_dungeon.resolved_dungeon_monsters.append(monster)
    #
    #         enemy_data = card.enemy()
    #         enemy_level = slot.monster_level
    #
    #         # TODO: fix
    #         monster.amount = 1
    #
    #         modifiers = jp_dungeon_floor.modifiers_clean
    #         monster.atk = int(round(modifiers['atk'] * enemy_data.atk.value_at(enemy_level)))
    #         monster.defense = int(
    #             round(modifiers['def'] * enemy_data.defense.value_at(enemy_level)))
    #         monster.hp = int(round(modifiers['hp'] * enemy_data.hp.value_at(enemy_level)))
    #         monster.turn = enemy_data.turns
    #
    #         monster.tsd_seq = sub_dungeon.tsd_seq
    #         monster.floor = stage.stage_idx
    #
    #         monster.drop_no = 0
    #         if slot.drops:
    #             monster_drops = set()
    #             other_drops = set()
    #             for drop in slot.drops:
    #                 if drop in monster_tree[monster_id]:
    #                     # Drop is an evo of the current monster
    #                     monster_drops.add(drop)
    #                 else:
    #                     # Drop is an alternate, like collab mats
    #                     other_drops.add(drop)
    #
    #             if len(monster_drops) > 1:
    #                 raise Exception('expected at most one monster drop', monster_drops)
    #
    #             # Sort the other drops for indexing purposes
    #             other_drops = list(sorted(other_drops))
    #
    #             if monster_drops:
    #                 monster.drop_no = next(iter(monster_drops))
    #             elif other_drops:
    #                 # We need drop_no to be set; since the monster didn't drop itself, set the
    #                 # first other drop
    #                 monster.drop_no = other_drops.pop(0)
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
    #
    #             if existing_drops:
    #                 raise Exception('unmatched drop records remain:', existing_drops)
    #
    #         monster.order_idx = slot.order
    #         monster.comment_kr = slot.comment
    #         monster.comment_jp = slot.comment
    #         monster.comment_us = slot.comment
    #
    #         monster.tstamp = int(time.time()) * 1000
