import argparse
import binascii
import json as base_json
import os

import pymysql
from sanic import Sanic
from sanic.exceptions import ServerError
from sanic.response import json, text
from sanic_compress import Compress
from sanic_cors import CORS

from data.utils import load_from_db
from pad.db.db_util import DbWrapper
from pad.raw.enemy_skills import enemy_skill_proto


def parse_args():
    parser = argparse.ArgumentParser(description="DadGuide backend server", add_help=False)
    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--db_config", help="JSON database info")
    input_group.add_argument("--es_dir", help="ES dir base")
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


@app.route('/dadguide/admin/randomMonsters')
async def serve_random_monsters(request):
    sql = '''
        select m.monster_id as monster_id, m.name_na as name
        from monsters m
        inner join encounters e
        on m.monster_id = e.enemy_id
        inner join dungeons d
        using (dungeon_id)
        inner join enemy_data ed
        using (enemy_id)
        where ed.status = 0
        and d.dungeon_type != 0
        order by rand()
        limit 20
    '''
    data = db_wrapper.fetch_data(sql)
    return json({'monsters': data})


@app.route('/dadguide/admin/monsterInfo')
async def serve_monster_info(request):
    monster_id = int(request.args.get('id'))
    sql = '''
        select m.monster_id as monster_id, m.name_na as name
        from monsters m
        where monster_id = {}
    '''.format(monster_id)
    monster_data = db_wrapper.fetch_data(sql)[0]
    sql = '''
        select
            d.name_na as dungeon_name, d.icon_id as dungeon_icon_id,
            sd.name_na as sub_dungeon_name,
            e.amount as amount, e.turns as turns, e.level as level,
            e.hp as hp, e.atk as atk, e.defence as defence
        from encounters e
        inner join dungeons d
        using (dungeon_id)
        inner join sub_dungeons sd
        using (sub_dungeon_id)
        where enemy_id = {}
        and dungeon_type != 0
    '''.format(monster_id)
    encounters = []
    encounter_data = db_wrapper.fetch_data(sql)
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
    return json({
        'monster': monster_data,
        'encounters': encounters,
    })


@app.route('/dadguide/admin/rawEnemyData')
async def serve_raw_enemy_data(request):
    monster_id = int(request.args.get('id'))
    data_dir = os.path.join(es_dir, 'behavior_raw')
    monster_file = os.path.join(data_dir, '{}.txt'.format(monster_id))
    with open(monster_file) as f:
        return text(f.read())


@app.route('/dadguide/admin/parsedEnemyData')
async def serve_parsed_enemy_data(request):
    monster_id = int(request.args.get('id'))
    data_dir = os.path.join(es_dir, 'behavior_text')
    monster_file = os.path.join(data_dir, '{}.txt'.format(monster_id))
    with open(monster_file) as f:
        return text(f.read())


@app.route('/dadguide/admin/enemyProto')
async def serve_enemy_proto(request):
    monster_id = int(request.args.get('id'))
    data_dir = os.path.join(es_dir, 'behavior_data')
    monster_file = os.path.join(data_dir, '{}.textproto'.format(monster_id))
    with open(monster_file) as f:
        return text(f.read())


@app.route('/dadguide/admin/enemyProtoEncoded')
async def serve_enemy_proto_encoded(request):
    monster_id = int(request.args.get('id'))
    data_dir = os.path.join(es_dir, 'behavior_data')
    monster_file = os.path.join(data_dir, '{}.textproto'.format(monster_id))
    mbwo = enemy_skill_proto.load_from_file(monster_file)
    v = mbwo.SerializeToString()
    return text(binascii.hexlify(bytearray(v)).decode('ascii'))


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

    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main(parse_args())
