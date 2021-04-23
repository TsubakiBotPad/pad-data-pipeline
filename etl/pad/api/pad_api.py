"""
Pulls data files for specified account/server.

Requires padkeygen which is not checked in.
Requires dungeon_encoding which is not checked in.
"""
import json
import math
import random
import urllib
from enum import Enum
from typing import Callable

import requests
from fake_useragent import UserAgent
from padtools.servers.server import Server

from pad.api import dungeon_encoding, keygen
from pad.common import pad_util
from pad.raw.wave import WaveResponse
from .player_data import PlayerDataResponse, RecommendedHelpersResponse, FriendEntry, FriendLeader, CardEntry

RESPONSE_CODES = {
    0: 'Okay',
    2: 'Re-login',
    3: 'Unregistered',
    8: 'dungeon not open',
    12: 'That person has too many friends.',
    25: 'Too many friend invites.',
    40: 'Cannot open dungeon due to corrupted data',
    44: 'No score to rank',
    48: 'room not found?',
    53: 'wrong version (update needed)',
    99: 'Maintenance',
    101: 'No connection',
    104: "Can't connect to server?",
    108: '???',
    602: 'room not found',
}


class ServerEndpointInfo(object):
    def __init__(self, server: Server, keygen_fn: Callable[[str, int], str], force_v=None):
        self.server = server
        self.keygen_fn = keygen_fn

        # Gungho messed up the version in the JSON so allowing an override.
        self.force_v = force_v


class ServerEndpoint(Enum):
    NA = ServerEndpointInfo(
        Server('http://patch-na-pad.gungho.jp/base-na-adr.json'), keygen.generate_key_na)
    JA = ServerEndpointInfo(
        Server('http://dl.padsv.gungho.jp/base_adr.json'), keygen.generate_key_jp)
    KR = ServerEndpointInfo(
        Server('http://patch-kr-pad.gungho.jp/base.kr-adr.json'), keygen.generate_key_kr)


class EndpointActionInfo(object):
    def __init__(self, name: str, v_name: str, v_value: int, **extra_args):
        # Name of the action
        self.name = name

        # Name of the version parameter
        self.v_name = v_name

        # Value for the version parameter
        self.v_value = v_value

        # Other random one-off parameters
        self.extra_args = extra_args


class EndpointAction(Enum):
    DOWNLOAD_CARD_DATA = EndpointActionInfo('download_card_data', 'v', 3)
    DOWNLOAD_DUNGEON_DATA = EndpointActionInfo('download_dungeon_data', 'v', 2)
    DOWNLOAD_SKILL_DATA = EndpointActionInfo('download_skill_data', 'ver', 1)
    DOWNLOAD_ENEMY_SKILL_DATA = EndpointActionInfo('download_enemy_skill_data', 'ver', 0)
    DOWNLOAD_LIMITED_BONUS_DATA = EndpointActionInfo('download_limited_bonus_data', 'v', 2)
    GET_PLAYER_DATA = EndpointActionInfo('get_player_data', 'v', 2)
    GET_RECOMMENDED_HELPERS = EndpointActionInfo('get_recommended_helpers', None, None)
    DOWNLOAD_MONSTER_EXCHANGE = EndpointActionInfo('mdatadl', None, None, dtp=0)
    SHOP_ITEM = EndpointActionInfo('shop_item', None, None)
    SAVE_DECKS = EndpointActionInfo('save_decks', None, None, curdeck=0)
    ACHIEVEMENTS = EndpointActionInfo('dl_al', None, None)


def get_headers(host):
    return {
        'User-Agent': 'GunghoPuzzleAndDungeon',
        'Accept-Charset': 'utf-8',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip',
        'Host': host,
        'Connection': 'Keep-Alive',
    }


def generate_entry_data(data_parsed: PlayerDataResponse, friend_leader: FriendLeader, fixed_team=False):
    """Returns a pair of the entry data array and [leader_card_id, friend_card_id]"""
    nonce = math.floor(random.random() * 0x10000)
    nonce_offset = nonce % 0x100
    card_nonce = len(data_parsed.cards) + nonce_offset

    deck_and_inherits = data_parsed.get_deck_and_inherits()

    deck_uuids = data_parsed.get_current_deck_uuids()
    leader = data_parsed.cards_by_uuid[deck_uuids[0]]
    leader_uuid = leader.card_uuid
    deck_uuids_minimal = [u for u in deck_uuids if u != 0]

    if fixed_team:
        return [
            'rk={}'.format(nonce),
            'bm={}'.format(card_nonce),
            'lc={}'.format(leader_uuid),
            'ds={}'.format(','.join(map(str, deck_and_inherits))),
            'dev={}'.format(PadApiClient.DEV),
            'osv={}'.format(PadApiClient.OSV).replace('.', ','),
            'pc={}'.format(','.join(map(str, deck_uuids_minimal))),
            'de={}'.format(1),  # This is always 1?
        ]

    friend_values = [friend_leader.hp_plus, friend_leader.atk_plus, friend_leader.rcv_plus,
                     friend_leader.awakening_count,
                     friend_leader.assist_monster_id, friend_leader.super_awakening_id,
                     friend_leader.assist_awakening_count]

    deck_and_inherits.append(friend_leader.monster_id)
    deck_and_inherits.append(friend_leader.assist_monster_id)

    return [
               'rk={}'.format(nonce),
               'bm={}'.format(card_nonce),
               'c={}'.format(friend_leader.monster_id),
               'l={}'.format(friend_leader.monster_level),
               's={}'.format(friend_leader.skill_level),
               'p={}'.format(','.join(map(str, friend_values))),
               'lc={}'.format(leader_uuid),
               'ds={}'.format(','.join(map(str, deck_and_inherits))),
               'dev={}'.format(PadApiClient.DEV),
               'osv={}'.format(PadApiClient.OSV).replace('.', ','),
               'pc={}'.format(','.join(map(str, deck_uuids_minimal))),
               'de={}'.format(1),  # This is always 1?
           ], [
               deck_and_inherits[0],
               deck_and_inherits[-2],
           ]


def extract_wave_response_from_entry(entry_json) -> WaveResponse:
    """Converts the results of a sneak_dungeon call into wave info."""
    return parse_wave_response(entry_json['e'])


def parse_wave_response(encrypted_wave_data: str) -> WaveResponse:
    wave_decrypted = dungeon_encoding.decodePadDungeon(encrypted_wave_data)
    wave_data = wave_decrypted.split('=')[1]
    wave_data = wave_data.split('&')[0]
    wave_data = wave_data.replace('"w":', '')
    return WaveResponse(json.loads(wave_data))


class PadApiClient(object):
    OSV = '6.0'
    DEV = 'bullhead'

    def __init__(self, endpoint: ServerEndpoint, user_uuid: str, user_intid: str):
        # Server-specific key generation function
        self.keygen_fn = endpoint.value.keygen_fn

        # Server short name, na or ja
        self.server_p = endpoint.name.lower()

        # PadTools server object
        self.server = endpoint.value.server

        # Current version string
        self.server_v = endpoint.value.force_v or self.server.version

        # Stripped version string
        self.server_r = self.server_v.replace('.', '')

        # Base URL to use for API calls
        self.server_api_endpoint = self.server.base['base']

        # Hostname for the base URL to use in the headers
        self.server_host = urllib.parse.urlparse(self.server_api_endpoint).hostname

        # Headers to use in every API call
        self.default_headers = get_headers(self.server_host)

        # The UUID of the user (with dashes) unique to each device transfer
        # 1ab232ac-1235-4789-6dfg-123456789abc
        self.user_uuid = user_uuid

        # The INT ID of the user (just numbers) static for each user
        # 123456789
        self.user_intid = user_intid

        # The result of the login attempt (must attempt to log in first)
        self.login_json = None

        # The current session ID (must be logged in first)
        self.session_id = None

        # Current player data (must have logged in and retrieved player data)
        self.player_data = None

        # List of suggested helpers (must have logged in and retrieved helpers)
        self.recommended_helpers_data = None

        # TODO: add retry/relogin on failure (res:3)

    def login(self):
        login_payload = self.get_login_payload()
        login_url = self.build_url(login_payload)
        print("Login URL {}", login_url)
        self.login_json = self.get_json_results(login_url)
        self.session_id = self.login_json['sid']

    def load_player_data(self):
        self.player_data = PlayerDataResponse(self.action(EndpointAction.GET_PLAYER_DATA))

    def load_helpers(self):
        self.recommended_helpers_data = RecommendedHelpersResponse(
            self.action(EndpointAction.GET_RECOMMENDED_HELPERS))

    def action(self, action: EndpointAction):
        payload = self.get_action_payload(action)
        url = self.build_url(payload)
        action_json = self.get_json_results(url)
        return action_json

    def get_login_payload(self):
        return [
            ('action', 'login'),
            ('t', '1'),
            ('v', self.server_v),
            ('u', self.user_uuid),
            ('i', self.user_intid),
            ('p', self.server_p),
            ('dev', PadApiClient.DEV),
            ('osv', PadApiClient.OSV),
            ('r', self.server_r),
            ('m', '0'),
        ]

    def get_action_payload(self, action: EndpointAction):
        payload = [
            ('action', action.value.name),
            ('pid', self.user_intid),
            ('sid', self.session_id),
        ]

        if action.value.v_name:
            payload.append((action.value.v_name, action.value.v_value))

        for key, val in action.value.extra_args.items():
            payload.append((key, val))

        payload.extend([
            ('r', self.server_r),
            ('m', '0'),
        ])

        return payload

    def overwrite_current_decks(self, card_uuids, self_friend_id=0):
        """Hacky routine to set all decks to the specified IDs and force the current deck to 0.

        card_ids should be list of integers with length=5
        """
        # First map card ID to card UUID
        proto_deck = list(card_uuids)

        # Finish deck entry with team awakening, selected friend, etc
        proto_deck.extend([9, self_friend_id, 0, 0])

        # Create a decks array all with the same thing
        decks = []
        for _ in range(self.player_data.get_deck_count()):
            decks.append(proto_deck)

        post_data = {
            'decksb': json.dumps({'fmt': 1, 'decks': decks})
        }

        payload = self.get_action_payload(EndpointAction.SAVE_DECKS)

        url = self.build_url(payload)
        action_json = self.get_json_results(url, post_data=post_data)
        return action_json

    def get_any_friend(self):
        if self.player_data.friends:
            return self.player_data.friends[0]
        elif self.recommended_helpers_data.helpers:
            return self.recommended_helpers_data.helpers[0]
        else:
            raise Exception('Could not locate a friend to use')

    def get_any_card_except_in_cur_deck(self):
        deck_uuids = self.player_data.get_current_deck_uuids()
        for card in self.player_data.cards:
            if card.card_uuid not in deck_uuids:
                return card
        else:
            raise Exception('No viable card not in current deck')

    def card_entry_to_fake_friend(self, card: CardEntry):
        assist_monster = self.player_data.cards_by_uuid[card.assist_uuid] if card.assist_uuid else None
        data = [
            card.card_id,
            card.level,
            card.skill_level,
            card.hp_plus,
            card.atk_plus,
            card.rcv_plus,
            card.awakening_count,
            card.latents,
            assist_monster.card_id if assist_monster else 0,
            1,
            assist_monster.level if assist_monster else 0,
            0,
            assist_monster.awakening_count if assist_monster else 0,
            0,
            card.super_awakening_id
        ]
        return FriendLeader(data)

    def enter_dungeon(self, dung_id: int, floor_id: int,
                      self_card: CardEntry = None,
                      friend: FriendEntry = None, friend_leader: FriendLeader = None):
        payload, leaders = self.get_entry_payload(
            dung_id, floor_id, self_card, friend, friend_leader)
        url = self.build_url(payload)
        action_json = self.get_json_results(url)
        action_json['entry_leads'] = leaders
        return action_json

    def get_entry_payload(self, dung_id: int, floor_id: int,
                          self_card: CardEntry = None,
                          friend: FriendEntry = None, friend_leader: FriendLeader = None,
                          fixed_team=False):
        """Returns a pair of the entry payload and [leader_card_id, friend_card_id]"""
        cur_ghtime = pad_util.cur_gh_time(self.server_p)
        cur_timestamp = int(cur_ghtime) * 1000 + random.randint(0, 999)
        data = [
            ('action', 'sneak_dungeon'),
            ('pid', self.user_intid),
            ('sid', self.session_id),
            ('dung', dung_id),
            ('floor', floor_id),
            ('time', cur_timestamp),
        ]

        if fixed_team:
            friend = None
            friend_leader = None
        elif self_card:
            data.append(('shelp', self_card.card_uuid))
            friend_leader = self.card_entry_to_fake_friend(self_card)
        elif friend_leader:
            ('helper', friend.user_intid),
        else:
            raise Exception('Must specify one of self_card, friend/friend_leader, fixed_team')

        entry_data, leaders = generate_entry_data(
            self.player_data, friend_leader, fixed_team=fixed_team)
        # TODO: make initial key random
        enc_entry_data = dungeon_encoding.encodePadDungeon('&'.join(entry_data), 0x23)
        data.extend([
            ('e', enc_entry_data),
            ('r', self.server_r),
            ('m', '0'),
        ])

        return data, leaders

    def build_url(self, payload):
        combined_payload = ['{}={}'.format(x[0], x[1]) for x in payload]
        payload_str = '&'.join(combined_payload)
        key = self.keygen_fn(payload_str, n=0)
        final_payload_str = '{}&key={}'.format(payload_str, key)
        return '{}?{}'.format(self.server_api_endpoint, final_payload_str)

    def get_json_results(self, url, post_data=None):
        s = requests.Session()
        if post_data:
            req = requests.Request('POST', url, headers=self.default_headers, data=post_data)
        else:
            req = requests.Request('GET', url, headers=self.default_headers)
        p = req.prepare()
        r = s.send(p)
        result_json = r.json()
        response_code = result_json.get('res', 0)
        if response_code != 0:
            raise Exception(
                'Bad server response: {} ({})'.format(response_code, RESPONSE_CODES.get(response_code, '???')))
        return result_json

    def get_egg_machine_page(self, gtype, grow):
        payload = [
            ('gtype', gtype),
            ('grow', grow),
            ('pid', self.user_intid),
            ('sid', self.session_id),
        ]
        combined_payload = ['{}={}'.format(x[0], x[1]) for x in payload]
        payload_str = '&'.join(combined_payload)
        final_url = '{}?{}'.format(self.player_data.gacha_url, payload_str)

        ua = UserAgent()
        headers = {'User-Agent': ua.chrome}

        s = requests.Session()
        req = requests.Request('GET', final_url, headers=headers)
        p = req.prepare()
        r = s.send(p)
        return r.text
