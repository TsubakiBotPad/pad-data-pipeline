from typing import List

from dadguide_proto.enemy_skills_pb2 import MonsterBehavior, BehaviorGroup, Condition, Behavior
from pad.raw.skills.enemy_skill_info import ESSkillSet, ESInstance, ESCountdownMessage, ESDefaultAttack, \
    attribute_bitmap
from pad.raw.enemy_skills.enemy_skillset_processor import ProcessedSkillset, StandardSkillGroup, Moveset, ESUseSkillset
from pad.raw_processor.crossed_data import CrossServerCard
from pad.raw.skills.en.enemy_skill_text import EnESTextConverter

ESTextConverter = EnESTextConverter()


def save_monster_behavior(file_path: str, csc: CrossServerCard, mb: MonsterBehavior):
    output = '#{} - {}'.format(csc.monster_id, csc.na_card.card.name)
    card = csc.cur_card.card
    output += '\nmonster size: {}'.format(card.unknown_009)
    output += '\nnew AI: {}'.format(card.use_new_ai)
    output += '\nstart/max counter: {}'.format(card.enemy_skill_max_counter)
    output += '\ncounter increment: {}'.format(card.enemy_skill_counter_increment)

    library = {x.enemy_skill_id: x.na_skill.behavior for x in csc.enemy_behavior}
    library[-1] = ESCountdownMessage()
    library[-2] = ESDefaultAttack()
    for i in range(0, 10):
        skill = ESUseSkillset(i + 1)
        library[skill.enemy_skill_id] = skill
    output += '\n' + format_monster_behavior(mb, library)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(output)


def format_monster_behavior(mb: MonsterBehavior, library):
    output = 'monster_id: {}'.format(mb.monster_id)
    output += '\napproved: {}'.format(mb.approved)

    for level in mb.levels:
        output += '\n\nlevel: {}'.format(level.level)
        for group in level.groups:
            output += '\n' + format_behavior_group(' ', group, library)

    return output


def format_behavior_group(indent_str, group: BehaviorGroup, library):
    sub_indent_str = indent_str.replace('|', ' ') + '| '
    if group.group_type in [BehaviorGroup.UNSPECIFIED, BehaviorGroup.STANDARD]:
        output = '{}group:'.format(indent_str)
    else:
        output = '{}type: {}'.format(indent_str, BehaviorGroup.GroupType.Name(group.group_type))
    cond_str = format_condition(group.condition)
    if cond_str:
        output += '\n{}condition: {}'.format(indent_str, cond_str)
    for child in group.children:
        if child.HasField('group'):
            output += '\n' + format_behavior_group(sub_indent_str, child.group, library)
        elif child.HasField('behavior'):
            output += '\n' + format_behavior(sub_indent_str, child.behavior, library)
        else:
            raise ValueError('Expected group or behavior')

    return output


def format_condition(cond: Condition):
    converter = EnESTextConverter()
    parts = []
    if cond.skill_set:
        parts.append('SkillSet {}'.format(cond.skill_set))
    if cond.use_chance not in [0, 100]:
        parts.append('{}% chance'.format(cond.use_chance))
    if cond.global_one_time:
        parts.append('one time only')
    if cond.limited_execution:
        parts.append('at most {} times'.format(cond.limited_execution))
    if cond.trigger_enemies_remaining:
        parts.append('when {} enemies remain'.format(cond.trigger_enemies_remaining))
    if cond.if_defeated:
        parts.append('when defeated')
    if cond.if_attributes_available:
        parts.append('when required attributes on board')
    if cond.trigger_monsters:
        parts.append('when {} on team'.format(', '.join(map(str, cond.trigger_monsters))))
    if cond.trigger_combos:
        parts.append('when {} combos last turn'.format(cond.trigger_combos))
    if len(cond.erased_attributes) != 0:
        parts.append('when all {} orbs are matched last turn'.format(
            converter.attributes_to_str(cond.erased_attributes)))
    if cond.if_nothing_matched:
        parts.append('if no other skills matched')
    if cond.damage_done:
        parts.append("when damage done last turn >= {}".format(cond.damage_done))
    if len(cond.attributes_attacked) != 0:
        parts.append(
            "when {} attributes are used to attack".format(converter.attributes_to_str(cond.attributes_attacked)))
    if cond.skills_used:
        parts.append("when {} or more skills are used".format(cond.skills_used))
    if cond.repeats_every:
        if cond.trigger_turn:
            if cond.trigger_turn_end:
                parts.append('execute repeatedly, turn {}-{} of {}'.format(cond.trigger_turn,
                                                                           cond.trigger_turn_end,
                                                                           cond.repeats_every))
            else:
                parts.append('execute repeatedly, turn {} of {}'.format(cond.trigger_turn, cond.repeats_every))
        else:
            parts.append('repeats every {} turns'.format(cond.repeats_every))
    elif cond.trigger_turn_end:
        turn_text = 'turns {}-{}'.format(cond.trigger_turn, cond.trigger_turn_end)
        parts.append(_cond_hp_timed_text(cond.always_trigger_above, turn_text))
    elif cond.trigger_turn:
        turn_text = 'turn {}'.format(cond.trigger_turn)
        parts.append(_cond_hp_timed_text(cond.always_trigger_above, turn_text))

    if not parts and cond.hp_threshold in [100, 0]:
        return None

    if cond.hp_threshold == 101:
        parts.append('when hp is full')
    elif cond.hp_threshold:
        parts.append('hp <= {}'.format(cond.hp_threshold))

    return ', '.join(parts)


def _cond_hp_timed_text(always_trigger_above: int, turn_text: str) -> str:
    text = turn_text
    if always_trigger_above == 1:
        text = 'always {}'.format(turn_text)
    elif always_trigger_above:
        text = '{} while HP > {}'.format(turn_text, always_trigger_above)
    return text


def format_behavior(indent_str, behavior: Behavior, library) -> str:
    skill = library.get(behavior.enemy_skill_id)
    if skill is None:
        return 'unknown ES'
    skill_name = skill.name
    if not skill_name:
        if behavior.child_ids:
            skill_name = ' + '.join([library[x] for x in behavior.child_ids])
        else:
            skill_name = 'unknown_name'
    output = '{}({}:{}) {}'.format(indent_str, skill.enemy_skill_id, skill.type, skill_name)
    if not behavior.child_ids:
        output += '\n{}{}'.format(indent_str, skill.full_description(ESTextConverter))
    for child_id in behavior.child_ids:
        child_skill = library.get(child_id)

        output += '\n{} - ({}:{}) {}'.format(indent_str,
                                             child_skill.enemy_skill_id,
                                             child_skill.type,
                                             child_skill.full_description(ESTextConverter))

    cond_str = format_condition(behavior.condition)
    if cond_str:
        output = '{}condition: {}\n{}'.format(indent_str, cond_str, output)
    return output


def save_behavior_plain(file_path: str, csc: CrossServerCard, behavior: List[ESInstance]):
    output = '#{} - {}'.format(csc.monster_id, csc.na_card.card.name)
    card = csc.cur_card.card
    output += '\nmonster size: {}'.format(card.unknown_009)
    output += '\nnew AI: {}'.format(card.use_new_ai)
    output += '\nstart/max counter: {}'.format(card.enemy_skill_max_counter)
    output += '\ncounter increment: {}'.format(card.enemy_skill_counter_increment)

    for idx, b in enumerate(behavior):
        output += '\n\n#{}: {}'.format(idx + 1, format_behavior_plain(b))

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(output)


def format_behavior_plain(o: ESInstance):
    def fmt_cond(c):
        msg = 'Condition: {} (ai:{} rnd:{})'.format(c.description(ESTextConverter), c._ai, c._rnd)
        if c.one_time:
            msg += ' (cost: {})'.format(c.one_time)
        elif c.forced_one_time:
            msg += ' (one-time only)'
        return msg

    def fmt_action_name(a):
        return '{}({}:{}) -> {}'.format(type(a).__name__, a.type, a.enemy_skill_id, a.name)

    if isinstance(o.behavior, ESSkillSet):
        msg = 'SkillSet:'
        if o.condition and o.condition.description(ESTextConverter):
            msg += '\n\t{}'.format(fmt_cond(o.condition))
        for idx, behavior in enumerate(o.behavior.skills):
            msg += '\n\t[{}] {}'.format(idx, fmt_action_name(behavior))
            msg += '\n\t{}'.format(behavior.full_description(ESTextConverter))
        return msg
    else:
        msg = fmt_action_name(o.behavior)
        if o.condition and (
                o.condition.description(ESTextConverter) or o.condition.one_time or o.condition.forced_one_time):
            msg += '\n{}'.format(fmt_cond(o.condition))

        msg += '\n{}'.format(o.behavior.full_description(ESTextConverter))
        return msg


def extract_used_skills(skillset: ProcessedSkillset, include_preemptive=True) -> List[ESInstance]:
    """Flattens a ProcessedSkillset to a list of actions"""
    results = []

    results.extend(skillset.death_actions)

    if include_preemptive:
        results.extend(skillset.preemptives)

    def sg_extract(l: List[StandardSkillGroup]) -> List[ESInstance]:
        return [item for sublist in l for item in sublist.skills]

    def moveset_extract(moveset: Moveset) -> List[ESInstance]:
        moveset_results = []

        for hp_action in moveset.hp_actions:
            results.extend(sg_extract(hp_action.timed))
            results.extend(sg_extract(hp_action.repeating))

        if moveset.status_action:
            moveset_results.append(moveset.status_action)
        if moveset.dispel_action:
            moveset_results.append(moveset.dispel_action)

        return moveset_results

    results.extend(moveset_extract(skillset.moveset))
    for e_moveset in skillset.enemy_remaining_movesets:
        results.extend(moveset_extract(e_moveset))

    return results
