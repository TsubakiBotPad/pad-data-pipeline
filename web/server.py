import argparse

from sanic import Sanic
from sanic.exceptions import ServerError
from sanic.response import json

import json as base_json

from sanic_compress import Compress

from data.utils import load_from_db


def parse_args():
    parser = argparse.ArgumentParser(description="DadGuide backend server", add_help=False)
    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--db_config", help="JSON database info")
    return parser.parse_args()


app = Sanic()
Compress(app)

db_config = None

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


def main(args):
    with open(args.db_config) as f:
        global db_config
        db_config = base_json.load(f)

    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main(parse_args())
