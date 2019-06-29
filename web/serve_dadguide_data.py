import argparse
import json

from data.utils import load_from_db


def parse_args():
    parser = argparse.ArgumentParser(description="Echos DadGuide database data", add_help=False)

    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--db_config", help="JSON database info")
    input_group.add_argument("--table", help="Table name")
    input_group.add_argument("--tstamp", help="DadGuide tstamp field limit")
    input_group.add_argument("--plain", action='store_true', help="Print a more readable output")

    return parser.parse_args()


def main(args):
    with open(args.db_config) as f:
        db_config = json.load(f)
    data = load_from_db(db_config, args.table, args.tstamp)

    if args.plain:
        print(json.dumps(data, indent=4, sort_keys=True))
    else:
        print(json.dumps(data))


if __name__ == "__main__":
    args = parse_args()
    main(args)
