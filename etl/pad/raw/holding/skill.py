"""
Parses monster skill (leader/active) data.
"""

import json
import os
from typing import List, Any

from pad.common import pad_util
from pad.common.pad_util import Printable
from pad.common.shared_types import SkillId

# The typical JSON file name for this data.
FILE_NAME = 'download_skill_data.json'


class MonsterSkill(Printable):
    """Leader/active skill info for a player-ownable monster."""

    def __init__(self, skill_id: int, raw: List[Any]):
        self.skill_id = SkillId(skill_id)

        # Skill name text.
        self.name = str(raw[0])

        # Skill description text (may include formatting).
        self.description = str(raw[1])

        # Skill description text (no formatting).
        self.clean_description = pad_util.strip_colors(
            self.description).replace('\n', ' ').replace('^p', '')

        # Encodes the type of skill (requires parsing other_fields).
        self.skill_type = int(raw[2])

        # If an active skill, number of levels to max.
        levels = int(raw[3])
        self.levels = levels if levels else None

        # If an active skill, maximum cooldown.
        self.turn_max = int(raw[4]) if self.levels else None

        # If an active skill, minimum cooldown.
        self.turn_min = self.turn_max - (self.levels - 1) if levels else None

        # Unknown field.
        self.unknown_005 = raw[5]

        # Fields used in coordination with skill_type.
        self.other_fields = raw[6:]

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return 'Skill(%s, %r)' % (self.skill_id, self.name)


def load_skill_data(data_dir=None, skill_json_file: str = None) -> List[MonsterSkill]:
    """Load MonsterSkill objects from the PAD json file."""
    if skill_json_file is None:
        skill_json_file = os.path.join(data_dir, FILE_NAME)

    with open(skill_json_file) as f:
        skill_json = json.load(f)

    return [MonsterSkill(i, ms) for i, ms in enumerate(skill_json['skill'])]


def load_raw_skill_data(data_dir=None, skill_json_file: str = None) -> object:
    """Load raw PAD json file."""
    # Temporary hack
    if skill_json_file is None:
        skill_json_file = os.path.join(data_dir, FILE_NAME)

    with open(skill_json_file) as f:
        skill_json = json.load(f)

    return skill_json
