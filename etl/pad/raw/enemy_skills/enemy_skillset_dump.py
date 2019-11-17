import os
from typing import TextIO

import yaml

from pad.raw.enemy_skills import debug_utils
from pad.raw.enemy_skills.enemy_skill_info import *
from pad.raw.enemy_skills.enemy_skillset_processor import ProcessedSkillset, Moveset, HpActions, TimedSkillGroup

_DATA_DIR = None


def set_data_dir(data_dir: str):
    if not os.path.isdir(data_dir):
        raise ValueError('Not a directory:', data_dir)
    global _DATA_DIR
    _DATA_DIR = data_dir


def data_dir() -> str:
    if not _DATA_DIR:
        raise ValueError('You must set the data dir before loading ES info')
    return _DATA_DIR


class RecordType(Enum):
    """Describes the type of record being stored.

    Has no practical use for DadGuide but it might be useful for other apps.
    """
    # Resist, resolve
    PASSIVE = 1
    # Actions that happen on the first turn
    PREEMPT = 2
    # Description-only visual separation aids
    DIVIDER = 3
    # Any kind of action, could be multiple enemy skills compounded into one
    ACTION = 4
    # An action that increases enemy damage
    ENRAGE = 5
    # Generic operator-supplied text placeholder, probably description-only
    TEXT = 6


class SkillRecord(yaml.YAMLObject):
    """A skill line item, placeholder, or other text."""
    yaml_tag = u'!SkillRecord'

    def __init__(self, record_type=RecordType.TEXT, name_en='', name_jp='', desc_en='', desc_jp='', min_atk_pct=None,
                 max_atk_pct=None, usage_pct=100, one_time=0):
        self.record_type_name = record_type.name
        # For actions, the name that is displayed in-game.
        # For dividers, contains the divider text.
        self.name_en = name_en
        self.name_jp = name_jp
        # A description of what occurs when this skill is triggered.
        self.desc_en = desc_en
        self.desc_jp = desc_jp
        # None if no attack, or the damage % expressed as an integer.
        # e.g. 100 for one hit with normal damage, 200 for two hits with normal damage,
        # 300 for one hit with 3x damage.
        self.max_atk_pct = min_atk_pct
        self.max_atk_pct = max_atk_pct
        # Likelihood of this action occurring, 0 < usage_pct <= 100.
        self.usage_pct = usage_pct
        # If the action only executes once.
        self.one_time = one_time


class SkillRecordListing(yaml.YAMLObject):
    """Group of skills that explain how an enemy behaves.

    Level is used to distinguish between different sets of skills based on the specific dungeon.
    """
    yaml_tag = u'!SkillRecordListing'

    def __init__(self, level: int, records: List[SkillRecord], overrides: List[SkillRecord] = None):
        self.level = level
        self.records = records
        self.overrides = overrides or []


class EntryInfo(yaml.YAMLObject):
    """Extra info about the entry."""
    yaml_tag = u'!EntryInfo'

    def __init__(self,
                 monster_id: int, monster_name_en: str, monster_name_jp: str,
                 reviewed_by='unreviewed', comments: str = None):
        self.monster_id = monster_id
        self.monster_name_en = monster_name_en
        self.monster_name_jp = monster_name_jp
        self.reviewed_by = reviewed_by
        self.comments = comments
        self.warnings = []  # List[str]


class EnemySummary(object):
    """Describes all the variations of an enemy."""

    def __init__(self, info: EntryInfo = None, data: List[SkillRecordListing] = None):
        self.info = info
        self.data = data or []

    def data_for_level(self, level: int) -> Optional[SkillRecordListing]:
        if not self.data:
            return None

        viable_levels = [d.level for d in self.data if level >= d.level]
        if not viable_levels:
            return None

        selected_level = min(viable_levels)
        return next(filter(lambda d: d.level == selected_level, self.data))


def behavior_to_skillrecord(record_type: RecordType, instance: EsInstance, note='') -> SkillRecord:
    action = instance.behavior
    name = action.name
    jp_name = name
    description = action.description()
    min_damage = None
    max_damage = None
    usage_pct = 100
    one_time = 0

    if issubclass(type(action), ESPassive):
        name = 'Ability'
        jp_name = name

    if type(action) in [ESPreemptive, ESAttackPreemptive]:
        name = 'Preemptive'
        jp_name = name

    elif record_type == RecordType.PREEMPT:
        description += ' (Preemptive)'

    attack = getattr(action, 'attack', None)
    if attack is not None:
        min_damage = attack.min_damage_pct()
        max_damage = attack.max_damage_pct()

    cond = instance.condition
    if cond is not None:
        usage_pct = cond.use_chance()
        if cond.one_time:
            one_time = cond.one_time
        elif cond.forced_one_time:
            one_time = cond.forced_one_time

    if note:
        description += ' ({})'.format(note)

    return SkillRecord(record_type=record_type,
                       name_en=name,
                       name_jp=jp_name,
                       desc_en=description,
                       desc_jp=description,
                       max_atk_pct=max_damage,
                       min_atk_pct=min_damage,
                       usage_pct=usage_pct,
                       one_time=one_time)


def create_divider(divider_text: str) -> SkillRecord:
    return SkillRecord(record_type=RecordType.DIVIDER, name_en=divider_text, name_jp=divider_text, desc_en='',
                       desc_jp='', max_atk_pct=None, min_atk_pct=None, usage_pct=None, one_time=None)


def special_adjust_enemy_remaining(skillset: ProcessedSkillset):
    # Special case processing for simple enemy remains movesets. A lot of earlier monsters
    # use this for enrage, we don't want to dump an entirely new section for that, so instead
    # merge it into the normal moveset with a special qualifier.
    one_moveset = len(skillset.enemy_remaining_movesets) == 1
    if not one_moveset:
        return

    es_moveset = skillset.enemy_remaining_movesets[0]
    count_of_one = es_moveset.count == 1
    no_repeating_actions = not any(map(lambda x: x.repeating, es_moveset.hp_actions))
    # only_singular_timed_actions = all(map(lambda x: len([z.skills for z in x.timed]) == 1, es_moveset.hp_actions))
    # This might be wrong?
    only_singular_timed_actions = all(map(lambda x: len(x.timed) == 1, es_moveset.hp_actions))
    if not (count_of_one and no_repeating_actions and only_singular_timed_actions):
        return

    skillset.enemy_remaining_movesets.clear()
    for action in es_moveset.hp_actions:
        found_action = None
        # First try to find an existing HP bucket to insert into.
        for primary_action in skillset.moveset.hp_actions:
            if primary_action.hp == action.hp:
                found_action = primary_action
                break

        # If no bucket exists, insert one and sort the array.
        if not found_action:
            found_action = HpActions(action.hp, [], [])
            skillset.moveset.hp_actions.append(found_action)
            skillset.moveset.hp_actions.sort(key=lambda x: x.hp, reverse=True)

        # If there are no timed skills (maybe because we just created the bucket)
        # or there were timed skills but not for turn 1 (unusual) insert a new
        # skill group for it.
        if not found_action.timed or found_action.timed[0].turn != 1:
            new_timed_skills = TimedSkillGroup(1, action.hp, [])
            found_action.timed.insert(0, new_timed_skills)

        # Insert the skills at the highest priority and add a note.
        for idx, skill in enumerate(action.timed[0].skills):
            found_action.timed[0].skills.insert(idx, skill)
            found_action.timed[0].notes[idx] = 'When 1 enemy remains'


def flatten_skillset(level: int, skillset: ProcessedSkillset) -> SkillRecordListing:
    records = []  # List[SkillRecord]

    for item in skillset.base_abilities:
        records.append(behavior_to_skillrecord(RecordType.PASSIVE, item))

    for item in skillset.preemptives:
        records.append(behavior_to_skillrecord(RecordType.PREEMPT, item))

    def process_moveset(moveset: Moveset):
        # Keeps track of when we output our first non-preempt/ability item.
        # Used to simplify the output of the first item in some cases.
        skill_output = False
        if moveset.status_action:
            skill_output = True
            records.append(create_divider('When afflicted by delay/poison'))
            records.append(behavior_to_skillrecord(RecordType.ACTION, moveset.status_action))

        if moveset.dispel_action:
            skill_output = True
            records.append(create_divider('When player has any buff'))
            records.append(behavior_to_skillrecord(RecordType.ACTION, moveset.dispel_action))

        hp_checkpoints = [hp_action.hp for hp_action in moveset.hp_actions]
        use_hp_full_output = 100 in hp_checkpoints and 99 in hp_checkpoints

        def hp_title(hp: int) -> str:
            if use_hp_full_output and hp == 100:
                return 'When HP is full'
            elif use_hp_full_output and hp == 99:
                return 'When HP is not full'
            elif not skill_output and hp == 100:
                return ''
            elif (hp + 1) % 5 == 0:
                return 'HP < {}'.format(hp + 1)
            elif hp == 0:
                return 'Enemy is defeated'
            else:
                return 'HP <= {}'.format(hp)

        for hp_action in moveset.hp_actions:
            title = hp_title(hp_action.hp)
            skill_output = True
            print_late_hp = False
            if title:
                records.append(create_divider(title))
            else:
                print_late_hp = len(hp_action.timed)

            # TODO: maybe we need special handling for 'always use turn x' commands?
            for item in hp_action.timed:
                title = 'Turn {}'.format(item.turn)
                if item.end_turn:
                    title += '-{}'.format(item.end_turn)
                records.append(create_divider(title))
                for idx, skill in enumerate(item.skills):
                    note = item.notes.get(idx, '')
                    records.append(behavior_to_skillrecord(RecordType.ACTION, skill, note=note))

            # Considers a situation where we printed turn info but no hp title, we
            # want to dump one here
            if hp_action.repeating and print_late_hp:
                title = hp_title(hp_action.hp)
                records.append(create_divider(title))

            for idx, repeating_set in enumerate(hp_action.repeating):
                if len(hp_action.repeating) > 1:
                    turn = repeating_set.turn
                    if idx == 0:
                        title = 'Execute repeatedly. Turn {}'.format(turn)
                    elif idx == len(hp_action.repeating) - 1:
                        title = 'Loop to 1 after. Turn {}'.format(turn)
                    else:
                        title = 'Turn {}'.format(turn)
                    if repeating_set.end_turn:
                        title += '-{}'.format(repeating_set.end_turn)
                    records.append(create_divider(title))

                for skill in repeating_set.skills:
                    records.append(behavior_to_skillrecord(RecordType.ACTION, skill))

    special_adjust_enemy_remaining(skillset)

    process_moveset(skillset.moveset)

    for er_moveset in skillset.enemy_remaining_movesets:
        records.append(create_divider("When {} enemy remains".format(er_moveset.count)))
        process_moveset(er_moveset)

    for item in skillset.death_actions:
        # We ignore death cries, and only output 'useful' skillsets on death
        if type(item) == ESSkillSetOnDeath and item.has_action():
            records.append(create_divider("On death"))
            records.append(behavior_to_skillrecord(RecordType.ACTION, item))

    return SkillRecordListing(level=level, records=records)


def load_summary(monster_id: int) -> Optional[EnemySummary]:
    """Load an EnemySummary from disk, returning None if no data is available (probably an error)."""
    file_path = _file_by_id(monster_id)
    if not os.path.exists(file_path):
        return None

    with open(file_path, encoding='utf-8') as f:
        line = _consume_comments(f)

        entry_info_data = []
        while not line.startswith('#'):
            entry_info_data.append(line)
            line = f.readline()

        all_listings = []
        while line:
            line = _consume_comments(f, initial_line=line)

            cur_listing_data = []
            while line and not line.startswith('#'):
                cur_listing_data.append(line)
                line = f.readline()

            if cur_listing_data:
                all_listings.append(cur_listing_data)

    enemy_info = yaml.load(''.join(entry_info_data), Loader=yaml.Loader)
    enemy_info.warnings = []
    enemy_summary = EnemySummary(enemy_info)
    enemy_summary.data = [yaml.load(''.join(x), Loader=yaml.Loader) for x in all_listings]

    return enemy_summary


def _consume_comments(f: TextIO, initial_line=None) -> str:
    line = initial_line or f.readline()
    while line and line.startswith('#'):
        line = f.readline()
    return line


def load_and_merge_summary(enemy_summary: EnemySummary) -> EnemySummary:
    """Loads any stored data from disk and merges with the supplied summary."""
    saved_summary = load_summary(enemy_summary.info.monster_id)
    if saved_summary is None:
        return enemy_summary

    # Merge any new items into the stored summary.
    for attr, new_value in enemy_summary.info.__dict__.items():
        stored_value = getattr(saved_summary.info, attr)
        if new_value is not None and stored_value is None:
            setattr(saved_summary.info, attr, new_value)

    listings_by_level = {x.level: x for x in saved_summary.data}
    overrides_exist = any(map(lambda x: len(x.overrides), saved_summary.data))

    # Update stored data with newly computed data.
    for computed_listing in enemy_summary.data:
        stored_listing = listings_by_level.get(computed_listing.level, None)
        if stored_listing is None:
            # No existing data was found.
            stored_listing = computed_listing
            saved_summary.data.append(computed_listing)
        else:
            # Found existing data so just update the computed part
            stored_listing.records = computed_listing.records

        # There were overrides in general but not on this item (probably because it is new).
        if overrides_exist and not stored_listing.overrides:
            saved_summary.info.warnings.append(
                'Override missing for {}'.format(computed_listing.level))

    return saved_summary


def dump_summary_to_file(card: Card, enemy_summary: EnemySummary, enemy_behavior: List[ESAction],
                         unused_behavior: List[ESAction]):
    """Writes the enemy info, actions by level, and enemy behavior to a file."""
    file_path = _file_by_id(enemy_summary.info.monster_id)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('{}\n'.format(_header('Info')))
        f.write('{}\n'.format(yaml.dump(enemy_summary.info, default_flow_style=False, allow_unicode=True)))
        for listing in enemy_summary.data:
            f.write('{}\n'.format(_header('Data @ {}'.format(listing.level))))
            f.write('{}\n'.format(yaml.dump(listing, default_flow_style=False, allow_unicode=True)))

        if unused_behavior:
            f.write('{}\n'.format(_header('Unused Actions')))
            for behavior in unused_behavior:
                behavior_str = debug_utils.simple_dump_obj(behavior)
                behavior_str = behavior_str.replace('\n', '\n# ').rstrip('#').rstrip()
                f.write('# {}\n'.format(behavior_str))

        f.write('{}\n'.format(_header('ES Modifiers')))
        f.write('# [{}] {} - monster size?\n'.format(9, card.unknown_009))
        f.write('# [{}] {} - use new AI\n'.format(52, 'true' if card.use_new_ai else 'false'))
        f.write('# [{}] {} - starting/max counter\n'.format(53, card.enemy_skill_max_counter))
        f.write('# [{}] {} - counter increment\n'.format(54, card.enemy_skill_counter_increment))

        f.write('#\n')

        if enemy_behavior:
            f.write('{}\n'.format(_header('Raw Behavior')))
            for idx, behavior in enumerate(enemy_behavior):
                behavior_str = debug_utils.simple_dump_obj(behavior)
                behavior_str = behavior_str.replace('\n', '\n# ').rstrip('#').rstrip()
                f.write('# [{}] {}\n'.format(idx + 1, behavior_str))


def _header(header_text: str) -> str:
    return '\n'.join([
        '#' * 60,
        '#' * 3 + ' {}'.format(header_text),
        '#' * 60,
    ])


def _file_by_id(monster_id: int):
    return os.path.join(data_dir(), '{}.yaml'.format(monster_id))


def load_summary_as_dump_text(card: Card, monster_level: int, dungeon_atk_modifier: float):
    """Produce a textual description of enemy behavior.

    Loads the enemy summary from disk, identifies the behavior appropriate for the level,
    and converts it into human-friendly output.
    """
    monster_id = card.card_id
    summary = load_summary(monster_id)
    if not summary:
        return 'Basic attacks (1)\n'

    return summary_as_dump_text(summary, card, monster_level, dungeon_atk_modifier)


def summary_as_dump_text(summary: EnemySummary, card: Card, monster_level: int, dungeon_atk_modifier: float):
    skill_data = summary.data_for_level(monster_level)
    if not skill_data:
        return 'Basic attacks (2)\n'

    enemy_info = skill_data.overrides or skill_data.records
    if not enemy_info:
        return 'Basic attacks (3)\n'

    atk = card.enemy().atk.value_at(monster_level)
    atk *= dungeon_atk_modifier
    msg = ''
    for row in enemy_info:
        header = row.name_en
        if row.record_type_name == 'DIVIDER':
            header = '{} {} {}'.format('-' * 5, header, '-' * 5)

        desc = row.desc_en
        if row.max_atk_pct:
            desc = '{} Damage - {}'.format(int(row.max_atk_pct * atk / 100), desc)
        if row.usage_pct not in [100, 0, None]:
            desc += ' ({}% chance)'.format(row.usage_pct)
        if row.one_time and row.record_type_name != 'PREEMPT':
            if card.enemy_skill_counter_increment == 1:
                desc += ' (every {} turns)'.format(row.one_time + 1)
            else:
                desc += ' (1 time use)'
        msg += header + '\n'
        if desc:
            msg += desc + '\n'

    return msg
