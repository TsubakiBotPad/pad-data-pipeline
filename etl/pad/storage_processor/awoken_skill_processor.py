import json

from pad.db.db_util import DbWrapper
from pad.storage.awoken_skill import AwokenSkill


class AwakeningProcessor(object):
    def __init__(self):
        with open('awoken_skill.json') as f:
            self.awoken_skills = json.load(f)

    def process(self, db: DbWrapper):
        for raw in self.awoken_skills:
            item = AwokenSkill.from_json(raw)
            db.insert_or_update(item)