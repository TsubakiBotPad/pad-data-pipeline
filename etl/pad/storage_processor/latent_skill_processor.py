import json
import os

from pad.db.db_util import DbWrapper
from pad.raw_processor.crossed_data import CrossServerDatabase
from pad.storage.latent_skill import LatentSkill

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

from pad.storage.monster import LatentTamadra


class LatentSkillProcessor(object):
    def __init__(self, data: CrossServerDatabase):
        self.data = data

        with open(os.path.join(__location__, 'latent_skill.json')) as f:
            self.latent_skills = json.load(f)

    def process(self, db: DbWrapper):
        for raw in self.latent_skills:
            item = LatentSkill.from_json(raw)
            db.insert_or_update(item)

        for csm in self.data.ownable_cards:
            if csm.cur_card.card.latent_on_feed:
                item = LatentTamadra.from_csm(csm)
                db.insert_or_update(item)
