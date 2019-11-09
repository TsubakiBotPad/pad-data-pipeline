from pad.raw.skills.en_skill_common import EnBaseTextConverter
from pad.raw.skills.leader_skill_text import LsTextConverter


class EnLsTextConverter(LsTextConverter, EnBaseTextConverter):
    _COLLAB_MAP = {
        0: '',
        1: 'Ragnarok Online Collab',
        2: 'Taiko no Tatsujin Collab',
        3: 'ECO Collab',
        5: 'Gunma\'s Ambition Collab',
        6: 'Final Fantasy Crystal Defender Collab',
        7: 'Famitsu Collab',
        8: 'Princess Punt Sweet Collab',
        9: 'Android Collab',
        10: 'Batman Collab',
        11: 'Capybara-san Collab',
        12: 'GungHo Collab',
        13: 'GungHo Collab',
        14: 'Evangelion Collab',
        15: 'Seven Eleven Collab',
        16: 'Clash of Clan Collab',
        17: 'Groove Coaster Collab',
        18: 'RO ACE Collab',
        19: 'Dragon\'s Dogma Collab',
        20: 'Takaoka City Collab',
        21: 'Monster Hunter 4G Collab',
        22: 'Shinrabansho Choco Collab',
        23: 'Thirty One Icecream Collab',
        24: 'Angry Bird Collab',
        26: 'Hunter x Hunter Collab',
        27: 'Hello Kitty Collab',
        28: 'PAD Battle Tournament Collab',
        29: 'BEAMS Collab',
        30: 'Dragon Ball Z Collab',
        31: 'Saint Seiya Collab',
        32: 'GungHo Collab',
        33: 'GungHo Collab',
        34: 'GungHo Collab',
        35: 'Gungho Collab',
        36: 'Bikkuriman Collab',
        37: 'Angry Birds Collab',
        38: 'DC Universe Collab',
        39: 'Sangoku Tenka Trigger Collab',
        40: 'Fist of the North Star Collab',
        41: 'Chibi Series',
        44: 'Chibi Keychain Series',
        45: 'Final Fantasy Collab',
        46: 'Ghost in Shell Collab',
        47: 'Duel Masters Collab',
        48: 'Attack on Titans Collab',
        49: 'Ninja Hattori Collab',
        50: 'Shounen Sunday Collab',
        51: 'Crows Collab',
        52: 'Bleach Collab',
        53: 'DC Universe Collab',
        55: 'Ace Attorney Collab',
        56: 'Kenshin Collab',
        57: 'Pepper Collab',
        58: 'Kinnikuman Collab',
        59: 'Napping Princess Collab',
        60: 'Magazine All-Stars Collab',
        61: 'Monster Hunter Collab',
        62: 'Special edition MP series',
        64: 'DC Universe Collab',
        65: 'Full Metal Alchemist Collab',
        66: 'King of Fighters \'98 Collab',
        67: 'Yu Yu Hakusho Collab',
        68: 'Persona Collab',
        69: 'Coca Cola Collab',
        70: 'Magic: The Gathering Collab',
        71: 'GungHo Collab',
        72: 'GungHo Collab',
        74: 'Power Pro Collab',
        76: 'Sword Art Online Collab',
        77: 'Kamen Rider Collab',
        78: 'Yo-kai Watch World Collab',
        83: 'Shaman King Collab',
        85: 'Samurai Spirits',
        86: 'Power Rangers',
        10001: 'Dragonbounds & Dragon Callers',
    }

    def get_collab_name(self, collab_id):
        if collab_id not in self._COLLAB_MAP:
            print('Missing collab name for', collab_id)
        return self._COLLAB_MAP.get(collab_id, '<not populated:{}>'.format(collab_id))

    def collab_bonus_text(self, bonus, name):
        return '{} when all cards are from {}'.format(bonus, name)

    def multi_mass_match_text(self, atk, bonus_combo, min_match, num_attr):
        if atk not in [0, 1]:
            skill_text = self.fmt_multiplier_text(1, atk, 1) + ' and increase '
        else:
            skill_text = 'Increase '
        skill_text += 'combo by {} when matching {} or more connected'.format(
            bonus_combo,
            min_match
        )
        skill_text += self.fmt_multi_attr(num_attr, conjunction='and') + ' orbs at once'
        return skill_text

    def l_match_text(self, mult_text, reduct_text, attr):
        if mult_text:
            skill_text = mult_text
            if reduct_text:
                skill_text += ' and ' + reduct_text
        elif reduct_text:
            skill_text = mult_text
        else:
            skill_text = '???'
        skill_text += ' when matching 5' + attr + ' orbs in L shape'
        return skill_text
