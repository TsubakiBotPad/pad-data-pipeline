import argparse
import json

import pymysql


def parse_args():
    parser = argparse.ArgumentParser(description="Echos DadGuide database data", add_help=False)

    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--db_config", help="JSON database info")
    input_group.add_argument("--email", help="email to check")

    return parser.parse_args()


def main(args):
    with open(args.db_config) as f:
        db_config = json.load(f)

    connection = pymysql.connect(host=db_config['host'],
                                 user=db_config['user'],
                                 password=db_config['password'],
                                 db='dadguide_admin',
                                 charset=db_config['charset'],
                                 cursorclass=pymysql.cursors.DictCursor)

    sql = 'SELECT * FROM `donors` WHERE email = "{}"'.format(args.email)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        results = list(cursor.fetchall())

    connection.close()

    print(json.dumps({'is_donor': len(results) == 1}))


if __name__ == "__main__":
    args = parse_args()
    main(args)
