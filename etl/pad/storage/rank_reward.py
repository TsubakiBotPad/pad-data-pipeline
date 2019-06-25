from pad.db.sql_item import SimpleSqlItem


class RankReward(SimpleSqlItem):
    """Rank reward."""
    TABLE = 'rank_rewards'
    KEY_COL = 'rank'

    @staticmethod
    def from_csv(o):
        return RankReward(rank=int(o[0]),
                          exp=int(o[1]),
                          add_cost=int(o[2]),
                          add_friend=int(o[3]),
                          add_stamina=int(o[4]),
                          cost=int(o[5]),
                          friend=int(o[6]),
                          stamina=int(o[7]))

    def __init__(self,
                 rank: int = None,
                 exp: int = None,
                 add_cost: int = None,
                 add_friend: int = None,
                 add_stamina: int = None,
                 cost: int = None,
                 friend: int = None,
                 stamina: int = None,
                 tstamp: int = None):
        self.rank = rank
        self.exp = exp
        self.add_cost = add_cost
        self.add_friend = add_friend
        self.add_stamina = add_stamina
        self.cost = cost
        self.friend = friend
        self.stamina = stamina
        self.tstamp = tstamp
