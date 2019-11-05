import json
import os

from pad.db.db_util import DbWrapper
from pad.storage.skill_tag import ActiveSkillTag, LeaderSkillTag

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class SkillTagProcessor(object):
    def __init__(self):
        with open(os.path.join(__location__, 'skill_tag_active.json')) as f:
            self.active_skill_tags = json.load(f)
        with open(os.path.join(__location__, 'skill_tag_leader.json')) as f:
            self.leader_skill_tags = json.load(f)

    def process(self, db: DbWrapper):
        for raw in self.active_skill_tags:
            item = ActiveSkillTag.from_json(raw)
            db.insert_or_update(item)
        for raw in self.leader_skill_tags:
            item = LeaderSkillTag.from_json(raw)
            db.insert_or_update(item)
