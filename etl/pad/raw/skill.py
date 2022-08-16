"""
Parses monster skill (leader/active) data.
"""

from typing import List

from pad.common import pad_util
from pad.common.shared_types import SkillId

# The typical JSON file name for this data.
FILE_NAME = 'download_skill_data.json'


class MonsterSkill(pad_util.Printable):
    """Leader/active skill info for a player-ownable monster."""

    def __init__(self, skill_id: int, raw: List):
        self.skill_id = SkillId(skill_id)

        # Skill name text.
        self.name: str = raw[0]

        # Skill description text (may include formatting).
        self.description: str = raw[1]

        # Skill description text (no formatting).
        self.clean_description = pad_util.strip_colors(
            self.description).replace('\n', ' ').replace('^p', '')

        # Encodes the type of skill (requires parsing other_fields).
        self.skill_type: int = int(raw[2])

        # If an active skill, number of levels to max.
        self.levels: int = int(raw[3]) or None

        # If an active skill, maximum cooldown.
        self.cooldown_turns_max: int = int(raw[4]) if self.levels else None

        # If an active skill, minimum cooldown.
        self.cooldown_turns_min: int = self.cooldown_turns_max - (self.levels - 1) if self.levels else None

        # Unknown field.
        self.unknown_005 = raw[5]

        # Fields used in coordination with skill_type.
        self.data: List[int] = raw[6:]

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return 'Skill(%s, %r)' % (self.skill_id, self.name)


def load_skill_data(data_dir=None, json_file: str = None) -> List[MonsterSkill]:
    """Load MonsterSkill objects from the PAD json file."""
    data_json = pad_util.load_raw_json(data_dir, json_file, FILE_NAME)
    return [MonsterSkill(i, ms) for i, ms in enumerate(data_json['skill'])]
