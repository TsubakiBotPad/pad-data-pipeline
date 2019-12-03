import os
from typing import List, Optional

from google.protobuf import text_format

from dadguide_proto.enemy_skills_pb2 import BehaviorItem, LevelBehavior, BehaviorGroup, MonsterBehavior, \
    MonsterBehaviorWithOverrides, Behavior
from pad.raw.enemy_skills.enemy_skill_info import EsInstance
from pad.raw.enemy_skills.enemy_skillset_processor import ProcessedSkillset, Moveset, HpActions, TimedSkillGroup


# Note for dadguide display:
# def hp_title(hp: int) -> str:
#     if use_hp_full_output and hp == 100:
#         return 'When HP is full'
#     elif use_hp_full_output and hp == 99:
#         return 'When HP is not full'
#     elif not skill_output and hp == 100:
#         return ''
#     elif (hp + 1) % 5 == 0:
#         return 'HP < {}'.format(hp + 1)
#     elif hp == 0:
#         return 'Enemy is defeated'
#     else:
#         return 'HP <= {}'.format(hp)


# for idx, repeating_set in enumerate(hp_action.repeating):
#     if len(hp_action.repeating) > 1:
#         turn = repeating_set.turn
#         if idx == 0:
#             title = 'Execute repeatedly. Turn {}'.format(turn)
#         elif idx == len(hp_action.repeating) - 1:
#             title = 'Loop to 1 after. Turn {}'.format(turn)
#         else:
#             title = 'Turn {}'.format(turn)
#         if repeating_set.end_turn:
#             title += '-{}'.format(repeating_set.end_turn)


def behavior_to_proto(instance: EsInstance) -> BehaviorItem:
    item = BehaviorItem()
    item_behavior = item.behavior
    item_condition = item_behavior.condition

    item_behavior.enemy_skill_id = instance.enemy_skill_id
    item_condition.hp_threshold = 100
    item_condition.use_chance = 100

    cond = instance.condition
    if cond is not None:
        item_condition.hp_threshold = cond.hp_threshold or 100
        item_condition.use_chance = cond.use_chance()
        item_condition.global_one_time = cond.forced_one_time or False
        item_condition.trigger_enemies_remaining = cond.enemies_remaining or 0
        item_condition.if_defeated = cond.on_death or False
        item_condition.if_attributes_available = len(cond.condition_attributes) > 0
        item_condition.trigger_monsters[:] = cond.cards_on_team
        item_condition.trigger_combos = cond.combos_made or 0

    return item


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


def add_behavior_group_from_behaviors(group_list, group_type, items: List[EsInstance]) -> BehaviorGroup:
    items = list(filter(None, items))  # Ensure there are no nulls in the list
    if not items:
        return
    bg = group_list.add()
    if isinstance(bg, BehaviorItem):
        # This method accepts a Union[List[BehaviorGroup], List[BehaviorItem]]
        bg = bg.group
    bg.group_type = group_type
    for item in items:
        bg.children.append(behavior_to_proto(item))
    return bg


def add_behavior_group_from_moveset(group_list, group_type, moveset: Moveset) -> BehaviorGroup:
    bg = group_list.add()
    bg.group_type = group_type

    add_behavior_group_from_behaviors(bg.children, BehaviorGroup.DISPEL_PLAYER, [moveset.dispel_action])
    add_behavior_group_from_behaviors(bg.children, BehaviorGroup.MONSTER_STATUS, [moveset.status_action])

    for action in moveset.hp_actions:
        hg = bg.children.add().group
        hg.group_type = BehaviorGroup.STANDARD
        hg.condition.hp_threshold = action.hp

        for time_action in action.timed:
            tg = hg.children.add().group
            tg.condition.trigger_turn = time_action.turn
            if time_action.end_turn:
                tg.condition.trigger_turn_end = time_action.end_turn
            add_behavior_group_from_behaviors(tg.children, BehaviorGroup.STANDARD, time_action.skills)

        for repeat_action in action.repeating:
            rg = hg.children.add().group
            rg.condition.repeats_every = repeat_action.interval
            add_behavior_group_from_behaviors(rg.children, BehaviorGroup.STANDARD, repeat_action.skills)

    return bg


def flatten_skillset(level: int, skillset: ProcessedSkillset) -> LevelBehavior:
    result = LevelBehavior()
    result.level = level

    add_behavior_group_from_behaviors(result.groups, BehaviorGroup.PASSIVE, skillset.base_abilities)
    add_behavior_group_from_behaviors(result.groups, BehaviorGroup.PREEMPT, skillset.preemptives)
    add_behavior_group_from_behaviors(result.groups, BehaviorGroup.DEATH, skillset.death_actions)

    add_behavior_group_from_moveset(result.groups, BehaviorGroup.STANDARD, skillset.moveset)

    for es_moveset in skillset.enemy_remaining_movesets:
        es_bg = add_behavior_group_from_moveset(result.groups, BehaviorGroup.REMAINING, es_moveset)
        es_bg.condition.trigger_enemies_remaining = es_moveset.count

    return result


def clean_monster_behavior(o: MonsterBehavior) -> MonsterBehavior:
    r = MonsterBehavior()
    r.monster_id = o.monster_id
    r.approved = o.approved
    for l in o.levels:
        r.levels.append(clean_level_behavior(l))
    return r


def clean_level_behavior(o: LevelBehavior) -> LevelBehavior:
    r = LevelBehavior()
    r.level = o.level
    for g in o.groups:
        g = clean_behavior_group(g)
        if g and g.children:
            r.groups.append(g)

    # Even if the LevelBehavior is empty we shouldn't remove it, although this
    # seems like an unlikely case.
    return r


def clean_behavior_group(o: BehaviorGroup) -> Optional[BehaviorGroup]:
    r = BehaviorGroup()
    r.group_type = o.group_type
    if o.HasField('condition'):
        r.condition.CopyFrom(o.condition)

    for c in o.children:
        c = clean_behavior_item(c)
        if c:
            r.children.append(c)

    # Just strip empty groups entirely
    if not o.children:
        return None

    return r


def clean_behavior_item(o: BehaviorItem) -> Optional[BehaviorItem]:
    r = BehaviorItem()

    if o.HasField('group'):
        g = clean_behavior_group(o.group)
        if not g:
            return None
        r.group.CopyFrom(g)
    elif o.HasField('behavior'):
        r.behavior.CopyFrom(clean_behavior(o.behavior))

    return r


def clean_behavior(o: Behavior) -> Behavior:
    # No cleanup for behaviors yet
    return o


def safe_save_to_file(file_path: str, obj: MonsterBehavior) -> MonsterBehaviorWithOverrides:
    mbwo = load_from_file(file_path)
    mbwo.monster_id = obj.monster_id
    del mbwo.levels[:]
    mbwo.levels.extend(obj.levels)

    msg_str = text_format.MessageToString(mbwo, as_utf8=True, indent=2)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(msg_str)

    return mbwo


def load_from_file(file_path: str) -> MonsterBehaviorWithOverrides:
    mbwo = MonsterBehaviorWithOverrides()
    if os.path.exists(file_path):
        with open(file_path, encoding='utf-8') as f:
            data = f.read()
        text_format.Merge(data, mbwo)
    return mbwo
