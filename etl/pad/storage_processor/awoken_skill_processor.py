import json
import os

from pad.db.db_util import DbWrapper
from pad.storage.awoken_skill import AwokenSkill

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class AwakeningProcessor(object):
    def __init__(self):
        with open(os.path.join(__location__, 'awoken_skill.json')) as f:
            self.awoken_skills = json.load(f)

    def process(self, db: DbWrapper):
        for raw in self.awoken_skills:
            item = AwokenSkill.from_json(raw)
            db.insert_or_update(item)
