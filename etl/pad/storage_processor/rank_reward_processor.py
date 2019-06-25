import csv
import os

from pad.db.db_util import DbWrapper
from pad.storage.rank_reward import RankReward

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class RankRewardProcessor(object):
    def __init__(self):
        with open(os.path.join(__location__, 'rank_reward.csv')) as f:
            reader = csv.reader(f)
            next(reader)
            self.rank_rewards = list(reader)

    def process(self, db: DbWrapper):
        for row in self.rank_rewards:
            item = RankReward.from_csv(row)
            db.insert_or_update(item)
