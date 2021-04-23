import json
import logging
from typing import List

from datetime import timedelta

from pad.db.db_util import DbWrapper
from pad.raw.bonus import BonusType
from pad.raw_processor import crossed_data
from pad.raw_processor.merged_data import MergedBonus
from pad.storage.schedule import ScheduleEvent

logger = logging.getLogger('processor')
human_fix_logger = logging.getLogger('human_fix')

SUPPORTED_BONUS_TYPES = [
    # Lists dungeons that are open.
    BonusType.dungeon,
    # Might need this to tag tournaments?
    BonusType.tournament_active,
]

WARN_BONUS_TYPES = [
    # Nothing should ever be unknown.
    BonusType.unknown,
]

IGNORED_BONUS_TYPES = [
    # Support these eventually
    BonusType.exp_boost,
    BonusType.coin_boost,
    BonusType.drop_boost,
    BonusType.stamina_reduction,
    BonusType.plus_drop_rate_1,
    BonusType.plus_drop_rate_2,

    # Support these non-dungeon ones eventually
    BonusType.feed_xp_bonus_chance,
    BonusType.feed_skillup_bonus_chance,

    # Probably never need these
    BonusType.send_egg_roll,
    BonusType.pem_event,
    BonusType.rem_event,
    BonusType.pem_cost,  # Consider supporting this if PEM starts changing cost again
    BonusType.multiplayer_announcement,
    BonusType.tournament_text,
    BonusType.dungeon_web_info_link,
    BonusType.exchange_text,
    BonusType.stone_purchase_text,
    BonusType.daily_dragons,
    BonusType.monthly_quest_dungeon,  # This has a dupe dungeon entry.
    BonusType.pad_metadata,
    BonusType.pad_metadata_2,
    BonusType.story_category_text,
    BonusType.normal_announcement,
    BonusType.technical_announcement,
    BonusType.special_dungeon_info_link,
    BonusType.dungeon_unavailable_popup,  # This might be useful if it becomes more common

    # Might need this to tag dungeons as tournaments, even closed ones.
    # Probably happens outside this processor though.
    BonusType.tournament_closed,

    # Needs research if we can extract scores?
    # Probably happens outside this processor though.
    BonusType.score_announcement,

    # These should be handled by the Dungeon processor.
    # Rewards for clearing the dungeon (and other garbage)
    BonusType.dungeon_special_event,
    # Rewards for clearing the sub dungeon (and other garbage)
    BonusType.dungeon_floor_text,
    # Lists multiplayer dungeons with special events active?
    BonusType.multiplayer_dungeon_text,

    # This has a variety of stuff, but mostly +X notifications.
    BonusType.gift_dungeon_with_reward,

    # Not sure what this does; has no text, no dungeon,
    # only a value of 10000, runs for a week, spotted in NA nad JP.
    BonusType.unknown_13,
    BonusType.unknown_14,
    # Not sure what it does, some kind of flag, spotted in JP.
    BonusType.unknown_40,
]


class ScheduleProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.data = data

    def process(self, db: DbWrapper):
        logger.info('loading JP events')
        self._process_schedule(db, self.data.jp_bonuses)
        logger.info('loading NA events')
        self._process_schedule(db, self.data.na_bonuses)
        logger.info('loading KR events')
        self._process_schedule(db, self.data.kr_bonuses)
        logger.info('done loading schedule data')

    def _process_schedule(self, db: DbWrapper, bonuses: List[MergedBonus]):
        for bonus in bonuses:
            bonus_type = bonus.bonus.bonus_info.bonus_type

            if bonus_type in WARN_BONUS_TYPES:
                human_fix_logger.error('Unexpected bonus: %s\n%s', bonus, bonus.bonus.raw)
                continue

            if bonus_type in IGNORED_BONUS_TYPES:
                logger.debug('Ignored bonus: %s', bonus)
                continue

            if bonus_type not in SUPPORTED_BONUS_TYPES:
                human_fix_logger.error('Incorrectly configured bonus: %s', bonus)
                continue

            if bonus.open_duration() > timedelta(days=60):
                logger.debug('Skipping long bonus: %s', bonus)
                continue

            if bonus.dungeon:
                logger.debug('Creating event: %s', bonus)
                event = ScheduleEvent.from_mb(bonus)
                db.insert_or_update(event)
            else:
                human_fix_logger.error('Dungeon with no dungeon attached: %s', bonus)
