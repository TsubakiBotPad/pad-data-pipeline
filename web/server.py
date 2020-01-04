import argparse
import binascii
import json as base_json
import os
import string

import pymysql
from sanic import Sanic
from sanic.exceptions import ServerError
from sanic.response import json, text
from sanic_compress import Compress
from sanic_cors import CORS

from dadguide_proto.enemy_skills_pb2 import MonsterBehaviorWithOverrides
from data.utils import load_from_db
from pad.db.db_util import DbWrapper
from pad.raw.enemy_skills import enemy_skill_proto


def parse_args():
    parser = argparse.ArgumentParser(description="DadGuide backend server", add_help=False)
    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--db_config", help="JSON database info")
    input_group.add_argument("--es_dir", help="ES dir base")
    input_group.add_argument("--web_dir", help="Admin app web directory")
    return parser.parse_args()


app = Sanic()
Compress(app)
CORS(app)

db_config = None
connection = None
db_wrapper = None  # type: DbWrapper
es_dir = None  # type: str

VALID_TABLES = [
    'active_skills',
    'awakenings',
    'awoken_skills',
    'd_attributes',
    'd_event_types',
    'drops',
    'dungeons',
    'dungeon_type',
    'encounters',
    'evolutions',
    'leader_skills',
    'monsters',
    'news',
    'rank_rewards',
    'schedule',
    'series',
    'skill_condition',
    'sub_dungeons',
    'timestamps'
]


@app.route('/dadguide/api/serve')
async def serve_table(request):
    table = request.args.get('table')
    if table is None:
        raise ServerError('table required')
    if table not in VALID_TABLES:
        raise ServerError('unexpected table')
    tstamp = request.args.get('tstamp')
    if tstamp is None and table != 'timestamps':
        raise ServerError('tstamp required')
    if tstamp is not None and not tstamp.isnumeric():
        raise ServerError('tstamp must be a number')

    data = load_from_db(db_config, table, tstamp)
    return json(data)


@app.route('/dadguide/admin/state')
async def serve_state(request):
    dungeons = db_wrapper.get_single_value('select count(*) from dungeons', int)
    monsters = db_wrapper.get_single_value('select count(*) from monsters', int)
    encountered_monsters = db_wrapper.get_single_value('select count(distinct enemy_id) from encounters', int)
    all_statuses = db_wrapper.fetch_data('''
        select enemy_data.status as status, count(distinct enemy_id) as count
        from enemy_data
        group by 1
    ''')
    encountered_statuses = db_wrapper.fetch_data('''
        select enemy_data.status as status, count(distinct enemy_id) as count
        from encounters
        inner join enemy_data
        using (enemy_id)
        inner join sub_dungeons
        using (sub_dungeon_id)
        where technical is true
        group by 1
    ''')

    def status_mapping(data):
        mapping = {x['status']: x['count'] for x in data}
        return {
            'not_approved': mapping.get(0, 0),
            'approved_as_is': mapping.get(1, 0),
            'needs_reapproval': mapping.get(2, 0),
            'approved_with_changes': mapping.get(3, 0),
        }

    return json({
        'dungeons': dungeons,
        'monsters': monsters,
        'encountered_monsters': encountered_monsters,
        'all_status_counts': status_mapping(all_statuses),
        'encountered_status_counts': status_mapping(encountered_statuses),
    })


MONSTERS_SQL = '''
    select m.monster_id as monster_id, e.enemy_id as enemy_id, m.name_na as name
    from monsters m
    inner join encounters e
    on m.monster_id = (e.enemy_id % 100000)
    inner join dungeons d
    using (dungeon_id)
    inner join enemy_data ed
    using (enemy_id)
    where ed.status = 0
    and d.dungeon_type != 0
    group by 1, 2, 3
    {}
    limit 20
'''

RANDOM_MONSTERS_SQL = MONSTERS_SQL.format('order by rand()')
EASY_MONSTERS_SQL = MONSTERS_SQL.format('order by length(ed.behavior), rand()')


@app.route('/dadguide/admin/randomMonsters')
async def serve_random_monsters(request):
    data = db_wrapper.fetch_data(RANDOM_MONSTERS_SQL)
    return json({'monsters': data})


@app.route('/dadguide/admin/easyMonsters')
async def serve_easy_monsters(request):
    data = db_wrapper.fetch_data(EASY_MONSTERS_SQL)
    return json({'monsters': data})


@app.route('/dadguide/admin/nextMonster')
async def serve_next_monster(request):
    enemy_id = int(request.args.get('id'))
    sql = '''
        select e.enemy_id as enemy_id
        from enemy_data ed
        inner join encounters e
        using (enemy_id)
        inner join dungeons d
        using (dungeon_id)
        inner join sub_dungeons sd
        using (sub_dungeon_id)
        where ed.status = 0
        and d.dungeon_type != 0
        and e.enemy_id > {}
        and sd.technical = true
        group by 1
        order by e.enemy_id asc
        limit 1
    '''.format(enemy_id)
    data = db_wrapper.get_single_value(sql, int)
    return text(data)


@app.route('/dadguide/admin/monsterInfo')
async def serve_monster_info(request):
    enemy_id = int(request.args.get('id'))
    monster_id = enemy_id % 100000
    sql = '''
        select m.monster_id as monster_id, m.name_na as name
        from monsters m
        where monster_id = {}
    '''.format(monster_id)
    monster_data = db_wrapper.fetch_data(sql)[0]
    sql = '''
        select
            d.name_na as dungeon_name, d.icon_id as dungeon_icon_id,
            sd.name_na as sub_dungeon_name, sd.sub_dungeon_id as sub_dungeon_id,
            e.amount as amount, e.turns as turns, e.level as level,
            e.hp as hp, e.atk as atk, e.defence as defence
        from encounters e
        inner join dungeons d
        using (dungeon_id)
        inner join sub_dungeons sd
        using (sub_dungeon_id)
        where enemy_id = {}
        and dungeon_type != 0
        and technical = true
    '''.format(enemy_id)
    encounters = []
    encounter_data = db_wrapper.fetch_data(sql)

    sql = '''
        select enemy_id 
        from enemy_data
        where enemy_id != {}
        and (enemy_id % 100000) = {}
    '''.format(enemy_id, monster_id)
    alt_enemies = [x['enemy_id'] for x in db_wrapper.fetch_data(sql)]

    # Filter out unnecessary dupes
    encounter_data = list({x['sub_dungeon_id']: x for x in encounter_data}.values())
    for x in encounter_data:
        encounters.append({
            'encounter': {
                'amount': x['amount'],
                'turns': x['turns'],
                'level': x['level'],
                'hp': x['hp'],
                'atk': x['atk'],
                'defence': x['defence'],
            },
            'dungeon': {
                'name': x['dungeon_name'],
                'icon_id': x['dungeon_icon_id'],
            },
            'sub_dungeon': {
                'name': x['sub_dungeon_name'],
            },
        })
    monster_data['enemy_id'] = enemy_id
    return json({
        'alt_enemy_ids': alt_enemies,
        'monster': monster_data,
        'encounters': encounters,
    })


@app.route('/dadguide/admin/rawEnemyData')
async def serve_raw_enemy_data(request):
    enemy_id = int(request.args.get('id'))
    data_dir = os.path.join(es_dir, 'behavior_plain')
    monster_file = os.path.join(data_dir, '{}.txt'.format(enemy_id))
    with open(monster_file) as f:
        return text(f.read())


@app.route('/dadguide/admin/parsedEnemyData')
async def serve_parsed_enemy_data(request):
    enemy_id = int(request.args.get('id'))
    data_dir = os.path.join(es_dir, 'behavior_text')
    monster_file = os.path.join(data_dir, '{}.txt'.format(enemy_id))
    with open(monster_file) as f:
        return text(f.read())


@app.route('/dadguide/admin/enemyProto')
async def serve_enemy_proto(request):
    enemy_id = int(request.args.get('id'))
    data_dir = os.path.join(es_dir, 'behavior_data')
    monster_file = os.path.join(data_dir, '{}.textproto'.format(enemy_id))
    with open(monster_file) as f:
        return text(f.read())


@app.route('/dadguide/admin/enemyProtoEncoded')
async def serve_enemy_proto_encoded(request):
    enemy_id = int(request.args.get('id'))
    data_dir = os.path.join(es_dir, 'behavior_data')
    monster_file = os.path.join(data_dir, '{}.textproto'.format(enemy_id))
    mbwo = enemy_skill_proto.load_from_file(monster_file)
    v = mbwo.SerializeToString()
    return text(binascii.hexlify(bytearray(v)).decode('ascii'))


@app.route('/dadguide/admin/saveApprovedAsIs')
async def serve_save_approved_as_is(request):
    enemy_id = int(request.args.get('id'))
    data_dir = os.path.join(es_dir, 'behavior_data')
    monster_file = os.path.join(data_dir, '{}.textproto'.format(enemy_id))
    mbwo = enemy_skill_proto.load_from_file(monster_file)
    del mbwo.level_overrides[:]
    mbwo.level_overrides.extend(mbwo.levels)
    mbwo.status = MonsterBehaviorWithOverrides.APPROVED_AS_IS
    enemy_skill_proto.save_overrides(monster_file, mbwo)
    return text('ok')


@app.route('/dadguide/admin/saveApprovedWithChanges', methods=["POST"])
async def serve_save_approved_with_changes(request):
    enemy_id = int(request.args.get('id'))
    data_dir = os.path.join(es_dir, 'behavior_data')
    monster_file = os.path.join(data_dir, '{}.textproto'.format(enemy_id))
    mbwo = enemy_skill_proto.load_from_file(monster_file)
    del mbwo.level_overrides[:]

    mbwo_input = MonsterBehaviorWithOverrides()
    mbwo_input.ParseFromString(binascii.unhexlify(str(request.body.decode('ascii'))))

    mbwo.level_overrides.extend(mbwo_input.level_overrides)
    mbwo.status = MonsterBehaviorWithOverrides.APPROVED_WITH_CHANGES
    enemy_skill_proto.save_overrides(monster_file, mbwo)

    return text('ok')


@app.route('/dadguide/admin/loadSkill')
async def serve_load_skill(request):
    skill_id = int(request.args.get('id'))
    sql = 'select * from enemy_skills where enemy_skill_id = {}'.format(skill_id)
    results = db_wrapper.get_single_or_no_row(sql)
    return json(fix_json_names(results))


def fix_list_json_names(rows):
    return [fix_json_names(x) for x in rows]


def fix_json_names(row):
    return {to_camel_case(key): val for key, val in row.items()}


def to_camel_case(s):
    return s[0].lower() + string.capwords(s, sep='_').replace('_', '')[1:] if s else s


def main(args):
    with open(args.db_config) as f:
        global db_config
        db_config = base_json.load(f)

    global connection
    connection = pymysql.connect(host=db_config['host'],
                                 user=db_config['user'],
                                 password=db_config['password'],
                                 db=db_config['db'],
                                 charset=db_config['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)

    global db_wrapper
    db_wrapper = DbWrapper(False)
    db_wrapper.connect(db_config)

    global es_dir
    es_dir = args.es_dir

    if args.web_dir:
        app.static('/', os.path.join(args.web_dir, 'index.html'))
        app.static('', args.web_dir)

    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main(parse_args())
