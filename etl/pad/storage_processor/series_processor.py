import json
import logging
import os
from collections import defaultdict

from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.monster import MonsterWithSeries
from pad.storage.series import Series

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

logger = logging.getLogger('processor')

class SeriesProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        with open(os.path.join(__location__, 'series.json')) as f:
            self.series = json.load(f)
        self.data = data

    def pre_process(self, db: DbWrapper):
        for raw in self.series:
            item = Series.from_json(raw)
            db.insert_or_update(item)

    def post_process(self, db: DbWrapper):
        self._try_ancestor(db)
        self._try_group(db)

    def _try_ancestor(self, db: DbWrapper):
        # For monsters with no series, try applying the series of the ancestor.
        monster_id_to_series_id = db.load_to_key_value('monster_id', 'series_id', 'monsters')
        monster_id_to_ancestor_id = db.load_to_key_value('to_id', 'from_id', 'evolutions')
        for monster_id, series_id in monster_id_to_series_id.items():
            if series_id != 0:
                # Series already set.
                continue

            ancestor_id = monster_id_to_ancestor_id.get(monster_id)
            if ancestor_id is None:
                # Monster had no ancestor to look up the series of.
                continue

            ancestor_series_id = monster_id_to_series_id[ancestor_id]
            if ancestor_series_id == 0:
                # Ancestor also has no series.
                continue

            # Apply the ancestor series to the current monster
            item = MonsterWithSeries(monster_id=monster_id, series_id=ancestor_series_id)
            db.insert_or_update(item)

    def _try_group(self, db: DbWrapper):
        # Try to infer the series of a monster via the series of monsters in its group.
        monster_id_to_series_id = db.load_to_key_value('monster_id', 'series_id', 'monsters')

        # Partition existing DadGuide monster series by PAD group ID.
        group_id_to_series_ids = defaultdict(set)
        for csc in self.data.ownable_cards:
            monster_id = csc.monster_id
            series_id = monster_id_to_series_id.get(monster_id)
            if series_id is None:
                monster_id_to_series_id[monster_id] = 0
                logger.warning('Series was null for monster %d', monster_id)
                continue
            if series_id == 0:
                # No useful data from this card
                continue

            group_id = csc.jp_card.card.group_id
            group_id_to_series_ids[group_id].add(series_id)

        # Now loop through again and see if we can apply any series via group mapping.
        for csc in self.data.ownable_cards:
            monster_id = csc.monster_id
            series_id = monster_id_to_series_id[monster_id]
            if series_id != 0:
                # Series already set.
                continue

            group_id = csc.jp_card.card.group_id
            possible_series = group_id_to_series_ids[group_id]
            if len(possible_series) == 1:
                group_series_id = list(possible_series)[0]
                item = MonsterWithSeries(monster_id=monster_id, series_id=group_series_id)
                db.insert_or_update(item)
