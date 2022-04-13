import logging

from pad.common import pad_util
from pad.common.pad_util import is_bad_name
from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.monster import AltMonster, Awakening, Evolution, Monster, MonsterWithExtraImageInfo, Transformation
from pad.storage.monster_skill import LeaderSkill, upsert_active_skill_data

logger = logging.getLogger('processor')
human_fix_logger = logging.getLogger('human_fix')


class MonsterProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.data = data

    def process(self, db: DbWrapper):
        logger.info('loading monster data')
        self._process_skills(db)
        self._process_monsters(db)
        self._process_monster_images(db)
        self._process_awakenings(db)
        self._process_evolutions(db)
        logger.info('done loading monster data')

    def _process_skills(self, db: DbWrapper):
        logger.info('loading skills for %s cards', len(self.data.ownable_cards))
        ls_count = 0
        as_count = 0
        for csc in self.data.ownable_cards:
            if csc.leader_skill:
                ls_count += 1
                db.insert_or_update(LeaderSkill.from_css(csc.leader_skill))
            if csc.active_skill:
                as_count += 1
                upsert_active_skill_data(db, csc.active_skill)
        logger.info('loaded %s leader skills and %s active skills', ls_count, as_count)

    def _process_monsters(self, db):
        logger.info('loading monsters')
        for m in self.data.all_cards:
            if 0 < m.monster_id < 19999 and not is_bad_name(m.jp_card.card.name):
                db.insert_or_update(Monster.from_csm(m))
            canonical_id = next((cm.monster_id for cm in self.data.ownable_cards
                                 if cm.monster_id == m.monster_id % 100000), None)
            db.insert_or_update(AltMonster.from_csm(m, canonical_id))

    def _process_monster_images(self, db):
        logger.info('monster images, hq_count=%s, anim_count=%s',
                    len(self.data.hq_image_monster_ids),
                    len(self.data.animated_monster_ids))
        if not self.data.hq_image_monster_ids or not self.data.animated_monster_ids:
            logger.info('skipping image info load')
            return
        for csm in self.data.ownable_cards:
            item = MonsterWithExtraImageInfo(monster_id=csm.monster_id,
                                             has_animation=csm.has_animation,
                                             has_hqimage=csm.has_hqimage)
            db.insert_or_update(item)

    def _process_awakenings(self, db):
        logger.info('loading awakenings')
        for m in self.data.ownable_cards:
            items = Awakening.from_csm(m)
            for item in items:
                try:
                    db.insert_or_update(item)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception:
                    human_fix_logger.fatal('Failed to insert item (probably new awakening): %s',
                                           pad_util.json_string_dump(item, pretty=True))

            sql = f'DELETE FROM {Awakening.TABLE} WHERE monster_id = {m.monster_id} AND order_idx >= {len(items)}'
            deleted_awos = db.update_item(sql)
            if deleted_awos:
                logger.info(f"Deleted {deleted_awos} unused awakenings from monster {m.monster_id}")

    def _process_evolutions(self, db):
        logger.info('loading evolutions')
        for m in self.data.ownable_cards:
            if not m.cur_card.card.ancestor_id:
                continue

            item = Evolution.from_csm(m)
            if item:
                db.insert_or_update(item)

        logger.info('loading transforms')
        for m in self.data.ownable_cards:
            if not (m.cur_card.active_skill and m.cur_card.active_skill.transform_ids):
                continue

            denom = sum(val for val in m.cur_card.active_skill.transform_ids.values())
            for tfid, num in m.cur_card.active_skill.transform_ids.items():
                if tfid is not None:
                    db.insert_or_update(Transformation.from_csm(m, tfid, num, denom))
