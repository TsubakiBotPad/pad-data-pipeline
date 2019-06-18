from pad.common import pad_util
from pad.common.shared_types import JsonType

# The typical JSON file name for this data.
FILE_NAME = 'egg_machines.json'

# TODO: Need to move the garbage parser from the API stuff
# into here, it shouldn't be doing all that work.


# TODO: Should load a real object
def load_data(data_dir=None, json_file: str = None) -> JsonType:
    """Load MonsterSkill objects from the PAD json file."""
    data_json = pad_util.load_raw_json(data_dir, json_file, FILE_NAME)
    return data_json
