from ..common import pad_util


class PlayerDataResponse(pad_util.Printable):
    def __init__(self, data):
        self.cur_deck_id = data['curDeck']  # int
        self.decksb = data['decksb']
        self.cards = [CardEntry(c) for c in data['card']]
        self.friends = [FriendEntry(f) for f in data['friends']]
        self.cards_by_uuid = {c.card_uuid: c for c in self.cards}
        self.egg_data = data['egatya3']

        gmsg = data['gmsg'].replace('ihttps', 'https')
        self.gacha_url = gmsg[:gmsg.rfind('/')] + '/prop.php'

    def get_deck_count(self):
        if 'decks' in self.decksb:
            return len(self.decksb['decks'])
        else:
            return len(self.decksb)

    def get_current_deck(self):
        if 'decks' in self.decksb:
            return self.decksb['decks'][self.cur_deck_id]
        else:
            cur_deck_str = str(self.cur_deck_id).zfill(2)
            cur_decksb_str = 's{}'.format(cur_deck_str)
            return self.decksb[cur_decksb_str]

    def get_current_deck_uuids(self):
        return self.get_current_deck()[:5]

    def get_deck_and_inherits(self):
        deck_and_inherits = []
        for card_uuid in self.get_current_deck_uuids():
            if card_uuid == 0:
                deck_and_inherits.append(0)
                deck_and_inherits.append(0)
                continue

            card = self.cards_by_uuid[card_uuid]
            deck_and_inherits.append(card.card_id)
            if card.assist_uuid == 0:
                deck_and_inherits.append(0)
            else:
                assist_card = self.cards_by_uuid[card.assist_uuid]
                deck_and_inherits.append(assist_card.card_id)
        return deck_and_inherits

    def map_card_ids_to_uuids(self, card_ids):
        results = [0] * 5
        for idx, card_id in enumerate(card_ids):
            if card_id == 0:
                continue

            for c in self.cards:
                # Ensure the card id matches and the UUID isn't already used
                if int(c.card_id) == int(card_id) and c.card_uuid not in results:
                    results[idx] = c.card_uuid
                    break
            if not results[idx]:
                raise ValueError('could not find uuid for', card_id)
        return results


class RecommendedHelpersResponse(pad_util.Printable):
    def __init__(self, data):
        print(data)
        self.helpers = [FriendEntry(f) for f in data['helpers']]


class CardEntry(pad_util.Printable):
    def __init__(self, row_values):
        self.card_uuid = row_values[0]
        self.exp = row_values[1]
        self.level = row_values[2]
        self.skill_level = row_values[3]
        self.feed_count = row_values[4]
        self.card_id = row_values[5]
        self.hp_plus = row_values[6]
        self.atk_plus = row_values[7]
        self.rcv_plus = row_values[8]
        self.awakening_count = row_values[9]
        self.latents = row_values[10]
        self.assist_uuid = row_values[11]
        self.unknown_12 = row_values[12]  # 0 in example
        self.super_awakening_id = row_values[13]
        self.unknown_14 = row_values[14]  # 0 in example

    def __str__(self):
        return str(self.__dict__)


class FriendEntry(pad_util.Printable):
    BASE_SIZE = 16

    def __init__(self, row_values):
        self.base_values = row_values[0:FriendEntry.BASE_SIZE]
        self.user_intid = row_values[1]
        self.leader_1 = FriendLeader(
            row_values[FriendEntry.BASE_SIZE + 0 * FriendLeader.SIZE: FriendEntry.BASE_SIZE + 1 * FriendLeader.SIZE])
        self.leader_2 = FriendLeader(
            row_values[FriendEntry.BASE_SIZE + 1 * FriendLeader.SIZE: FriendEntry.BASE_SIZE + 2 * FriendLeader.SIZE])

        if len(row_values) > FriendEntry.BASE_SIZE + 2 * FriendLeader.SIZE + 2:
            self.leader_3 = FriendLeader(
                row_values[
                FriendEntry.BASE_SIZE + 2 * FriendLeader.SIZE: FriendEntry.BASE_SIZE + 3 * FriendLeader.SIZE])
        else:
            self.leader_3 = None

    def __str__(self):
        return str(self.__dict__)


class FriendLeader(pad_util.Printable):
    SIZE = 15

    def __init__(self, row_values):
        self.monster_id = row_values[0]
        self.monster_level = row_values[1]
        self.skill_level = row_values[2]
        self.hp_plus = row_values[3]
        self.atk_plus = row_values[4]
        self.rcv_plus = row_values[5]
        self.awakening_count = row_values[6]
        self.latents = row_values[7]
        self.assist_monster_id = row_values[8]
        self.assist_unknown_8 = row_values[9]  # 1 in examples
        self.assist_monster_level = row_values[10]
        self.assist_unknown_11 = row_values[11]  # 0 in examples
        self.assist_awakening_count = row_values[12]
        self.unknown_13 = row_values[13]  # 0 in examples
        self.super_awakening_id = row_values[14]

    def __str__(self):
        return str(self.__dict__)
