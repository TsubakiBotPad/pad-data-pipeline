import argparse
import json as base_json
from typing import Optional

from sanic import Sanic
from sanic import request
from sanic.exceptions import ServerError
from sanic.response import json
from sanic_compress import Compress
from sanic_cors import CORS

from data import utils
from data.utils import load_from_db
from pad.db.db_util import DbWrapper


def parse_args():
    parser = argparse.ArgumentParser(description="DadGuide mobile backend server", add_help=False)
    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--db_config", help="JSON database info")
    input_group.add_argument("--port", default='8001', help="TCP port to listen on")
    return parser.parse_args()


app = Sanic()
Compress(app)
CORS(app)

db_config = None
connection = None
db_wrapper = None  # type: Optional[DbWrapper]

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


@app.route('/dadguide/api/v1/purchases', methods={'POST'})
async def add_purchase(request: request.Request):
    print('got add purchase request')
    data = request.json
    print(data)
    device_id = data.get('device_id', 'missing')
    if device_id == 'missing':
        raise ServerError('device_id required')

    purchase_info = base_json.dumps(data, sort_keys=True, indent=2)
    sql = 'INSERT INTO `dadguide_admin`.`purchases` (`device_id`, `purchase_info`) VALUES (%s, %s)'
    db_wrapper.insert_item(sql, [device_id, purchase_info])

    return json({'status': 'ok'})


def main(args):
    with open(args.db_config) as f:
        global db_config
        db_config = base_json.load(f)

    global connection
    connection = utils.connect(db_config)

    global db_wrapper
    db_wrapper = DbWrapper(False)
    db_wrapper.connect(db_config)

    app.run(host='0.0.0.0', port=int(args.port))


if __name__ == '__main__':
    main(parse_args())
