import argparse
import json
import re
import urllib.request
from typing import Optional

import padtools
import pymysql
from padtexturetool.texture_reader import decrypt_and_decompress_binary_blob

parser = argparse.ArgumentParser(description="Parses PAD DMSG files", add_help=False)

input_group = parser.add_argument_group("Input")
input_group.add_argument("--server", required=True, help="na or jp")
input_group.add_argument("--db_config", help="JSON database info")

help_group = parser.add_argument_group("Help")
help_group.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()

server = args.server.lower()

extras = []
if server == 'na':
    extras = padtools.regions.north_america.server.extras  # noqa
elif server == 'jp':
    extras = padtools.regions.japan.server.extras  # noqa  TODO: Don't require these
else:
    print('invalid server:', server)
    exit(1)


def readint(data, off, sz=4):
    return int.from_bytes(data[off:off + sz], 'little')


def readstr(data, off, sz=None, encoding='utf8'):
    # If size is None, read until \0.
    if sz is not None:
        return data[off:off + sz].rstrip(b'\0').decode(encoding)
    stop = data.find(b'\0', off)
    return data[off:stop].rstrip(b'\0').decode(encoding)


def parse_dmsg(dmsg: bytes):
    assert readstr(dmsg, 0, 4) == 'DMSG'
    colct = readint(dmsg, 4, 2)
    rowct = readint(dmsg, 6, 2)
    table = []

    def getstr(i, j):
        offset = readint(dmsg, 8 + 4 * (i * colct + j))
        if not offset:
            return ''
        return readstr(dmsg, offset)

    table = [[getstr(i, j) for j in range(colct)] for i in range(rowct)]
    return table


name_svr = 'name_en' if server == 'na' else 'name_ja' if server == 'jp' else None

with open(args.db_config) as f:
    db_config = json.load(f)

db = pymysql.connect(**db_config, autocommit=True)
cur = db.cursor()


def insert_or_replace_into(data: dict, table: str, id_col: str):
    updates = []
    update_repls = ()
    for key, val in list(data.items()):
        if val == '-':
            del data[key]
            continue
        if key != id_col:
            updates.append(f'{key}=%s')
            update_repls += (val,)

    if updates:
        query = (f"INSERT INTO {table} ({', '.join(data)}, tstamp)"
                 f"  VALUES ({', '.join('%s' for _ in data)}, UNIX_TIMESTAMP())"
                 f"  ON DUPLICATE KEY UPDATE {', '.join(updates)};")
        cur.execute(query, (*data.values(),) + update_repls)


# Skin Data
def bgm_name_to_id(name: str) -> Optional[int]:
    if (match := re.match(r'bgm_0*(\d+)', name)):
        return int(match.group(1))
    return None


skindata = next((e for e in extras if e.file_name == 'skindata.bin'))

with urllib.request.urlopen(skindata.url) as resp:
    skindata = resp.read()
skindata = parse_dmsg(decrypt_and_decompress_binary_blob(skindata))

for row in skindata:
    if float(row[0]) >= 10000:  # GH sucks and sometimes likes to give these as floats
        if bgm_name_to_id(row[11]):
            insert_or_replace_into({'bgm_id': bgm_name_to_id(row[11]), name_svr: row[10].replace('\n', '')},
                                   'bgms', 'bgm_id')
        if bgm_name_to_id(row[13]):
            insert_or_replace_into({'bgm_id': bgm_name_to_id(row[13]), name_svr: row[12].replace('\n', '')},
                                   'bgms', 'bgm_id')
        insert_or_replace_into({
            'bgm_set_id': float(row[0]),
            name_svr: row[1].replace('\n', ''),
            'route_bgm_id': bgm_name_to_id(row[11]),
            'boss_bgm_id': bgm_name_to_id(row[13]),
            'unused': float(row[8] or '0')
        }, 'bgm_sets', 'bgm_set_id')

cur.close()
db.close()
