import logging

from pad.common import pad_util
from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.monster import LeaderSkill, ActiveSkill, Monster, Awakening, Evolution, MonsterWithExtraImageInfo, \
    AltMonster

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
            card_ls = csc.leader_skill
            if card_ls:
                ls_count += 1
                db.insert_or_update(LeaderSkill.from_css(card_ls))
            card_as = csc.active_skill
            if card_as:
                as_count += 1
                db.insert_or_update(ActiveSkill.from_css(card_as))

        logger.info('loaded %s leader skills and %s active skills', ls_count, as_count)

    def _process_monsters(self, db):
        logger.info('loading %s monsters', len(self.data.ownable_cards))
        for m in self.data.all_cards:
            if 0 < m.monster_id < 19999:
                item = Monster.from_csm(m)
                db.insert_or_update(item)
            item = AltMonster.from_csm(m)
            db.insert_or_update(item)

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

            sql = 'SELECT COUNT(*) FROM {} WHERE monster_id = {}'.format(Awakening.TABLE, m.monster_id)
            stored_awakening_count = db.get_single_value(sql, op=int)
            if len(items) < stored_awakening_count:
                human_fix_logger.error('Incorrect awakening count for %s, got %s wanted %s',
                                       m.monster_id, stored_awakening_count, len(items))

    def _process_evolutions(self, db):
        logger.info('loading evolutions')
        for m in self.data.ownable_cards:
            if not m.cur_card.card.ancestor_id:
                continue

            item = Evolution.from_csm(m)
            if item:
                db.insert_or_update(item)
