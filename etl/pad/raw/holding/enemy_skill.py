import csv
import json
import os
from io import StringIO
from typing import List, Any

from pad.common import pad_util

FILE_NAME = 'download_enemy_skill_data.json'


class EnemySkill(pad_util.Printable):

    def __init__(self, raw: List[Any]):
        self.enemy_skill_id = int(raw[0])
        self.name = raw[1]
        self.type = int(raw[2])
        self.flags = int(raw[3], 16)  # 16bitmap for params
        self.params = [None] * 16
        offset = 0
        p_idx = 4
        while offset < self.flags.bit_length():
            if (self.flags >> offset) & 1 != 0:
                p_value = raw[p_idx]
                self.params[offset] = int(p_value) if p_value.lstrip('-').isdigit() else p_value
                p_idx += 1
            offset += 1


def load_enemy_skill_data(data_dir: str = None, card_json_file: str = None) -> List[EnemySkill]:
    if card_json_file is None:
        card_json_file = os.path.join(data_dir, FILE_NAME)
    with open(card_json_file) as f:
        enemy_skill_json = json.load(f)
    es = enemy_skill_json['enemy_skills']
    es = es.replace("',", "#,").replace(",'", ",#").replace("'\n", "#\n")
    csv_lines = csv.reader(StringIO(es), quotechar="#", delimiter=',')
    return [EnemySkill(x) for x in csv_lines if x[0] != 'c']
