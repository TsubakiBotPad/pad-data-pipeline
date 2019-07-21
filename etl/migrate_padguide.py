"""
"""
import argparse
import json
import logging

from pad.common.shared_types import Server
from pad.db.db_util import DbWrapper
from pad.raw_processor import merged_database, crossed_data
from pad.storage.series import Series

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

logger = logging.getLogger('database')
logger.setLevel(logging.DEBUG)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def parse_args():
    parser = argparse.ArgumentParser(description="Migrates PadGuide data to DadGuide.", add_help=False)
    parser.register('type', 'bool', str2bool)

    inputGroup = parser.add_argument_group("Input")
    inputGroup.add_argument("--doupdates", default=False,
                            action="store_true", help="Enables actions")
    inputGroup.add_argument("--db_config", required=True, help="JSON database info")
    inputGroup.add_argument("--input_dir", required=True,
                            help="Path to a folder where the input data is")

    helpGroup = parser.add_argument_group("Help")
    helpGroup.add_argument("-h", "--help", action="help",
                           help="Displays this help message and exits.")
    return parser.parse_args()


def load_data(args):
    dry_run = not args.doupdates

    input_dir = args.input_dir

    logger.info('Loading data')
    jp_database = merged_database.Database(Server.jp, input_dir)
    jp_database.load_database()

    na_database = merged_database.Database(Server.na, input_dir)
    na_database.load_database()

    kr_database = merged_database.Database(Server.kr, input_dir)
    kr_database.load_database()

    cs_database = crossed_data.CrossServerDatabase(jp_database, na_database, kr_database)

    logger.info('Connecting to database')
    with open(args.db_config) as f:
        db_config = json.load(f)

    db_wrapper = DbWrapper(dry_run)
    db_wrapper.connect(db_config)

    do_migration(cs_database, db_wrapper)


def do_migration(csd: crossed_data.CrossServerDatabase, db: DbWrapper):
    get_series_sql = ('SELECT tsr_seq AS series_id, name_jp, name_us AS name_na, name_kr'
                      ' FROM padguide.series_list'
                      ' WHERE del_yn = 0')

    data = db.fetch_data(get_series_sql)

    for row in data:
        series_id = row['series_id']
        if series_id == 42:
            # Not importing 42 (premium) which was used as the old unsorted
            continue

        item = Series(series_id=series_id,
                      name_jp=row['name_jp'],
                      name_na=row['name_na'],
                      name_kr=row['name_kr'])
        db.insert_or_update(item)

    monsterno_seriesid_map = db.load_to_key_value('monster_no', 'tsr_seq', 'padguide.monster_info_list')
    monsterno_nameoverride_map = db.load_to_key_value('monster_no', 'tm_name_us_override', 'padguide.monster_list')
    monsterno_regdate_map = db.load_to_key_value('monster_no', 'reg_date', 'padguide.monster_list')

    for csc in csd.ownable_cards:
        if csc.monster_id > 9999:
            continue  # Just skip voltron handle it separately.

        if csc.jp_card.server != Server.jp:
            continue  # Safety check

        # Since this is a JP card for sure, monster_id == JP monster_no
        monster_id = csc.monster_id
        monster_no = jp_id_to_monster_no(monster_id)

        # Series processing
        series_id = monsterno_seriesid_map[monster_no]
        if series_id == 42:
            series_id = 0  # Map premium to unsorted

        update_sql = 'UPDATE monsters SET series_id={} WHERE monster_id={}'.format(series_id, monster_id)
        db.insert_item(update_sql)

        # Reg Date processing
        reg_date = monsterno_regdate_map[monster_no]
        update_sql = "UPDATE monsters SET reg_date='{}' WHERE monster_id={}".format(reg_date.date().isoformat(),
                                                                                    monster_id)
        db.insert_item(update_sql)

        # NA name override processing
        name_override = monsterno_nameoverride_map.get(monster_no, None)
        if name_override:
            name_override = name_override.replace("'", "''")
            update_sql = "UPDATE monsters SET name_na_override='{}' WHERE monster_id={}".format(name_override,
                                                                                                monster_id)
            db.insert_item(update_sql)


def jp_id_to_monster_no(jp_id):
    jp_id = int(jp_id)

    # Batman 2
    if between(jp_id, 1049, 1058):
        return adjust(jp_id, 1049, 9900)

    # Didn't match an exception, same card ID
    return jp_id


def between(n, bottom, top):
    return bottom <= n <= top


def adjust(n, local_bottom, remote_bottom):
    return n - local_bottom + remote_bottom


if __name__ == '__main__':
    args = parse_args()
    load_data(args)

