import os
from typing import List, Optional, Union

from google.protobuf import text_format

from dadguide_proto.enemy_skills_pb2 import BehaviorItem, LevelBehavior, BehaviorGroup, MonsterBehavior, \
    MonsterBehaviorWithOverrides, Behavior, Condition
from pad.raw.skills.enemy_skill_info import ESInstance
from pad.raw.enemy_skills.enemy_skillset_processor import ProcessedSkillset, Moveset, HpActions, TimedSkillGroup


def behavior_to_proto(instance: ESInstance, is_timed_group=True, cur_hp=100) -> BehaviorItem:
    """Converts an ESInstance into a BehaviorItem.

    is_timed_group is a hack that injects global_one_time for a relatively small group of monsters that
    have a % chance to activate and no increment.
    """
    item = BehaviorItem()
    item_behavior = item.behavior
    item_condition = item_behavior.condition

    item_behavior.enemy_skill_id = instance.enemy_skill_id

    cond = instance.condition
    if cond is not None:
        use_chance = cond.use_chance(hp=cur_hp)
        if use_chance not in [0, 100]:
            item_condition.use_chance = use_chance
        item_condition.global_one_time = cond.forced_one_time or False
        item_condition.trigger_enemies_remaining = cond.enemies_remaining or 0
        item_condition.if_defeated = (cond.on_death and instance.behavior.has_action()) or False
        item_condition.if_attributes_available = len(cond.condition_attributes) > 0
        item_condition.trigger_monsters[:] = cond.cards_on_team
        item_condition.trigger_combos = cond.combos_made or 0

        is_optional = use_chance < 100
        has_flag = (cond.one_time or 0) > 0
        flags_only_decrease = instance.increment == 0 and instance.max_counter > 0
        if not is_timed_group and is_optional and has_flag and flags_only_decrease:
            if instance.max_counter == cond.one_time:
                item_condition.global_one_time = True
            else:
                item_condition.limited_execution = int(instance.max_counter / cond.one_time)

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


def add_behavior_group_from_behaviors(group_list, group_type, items: List[ESInstance],
                                      is_timed_group=False, cur_hp=100) -> BehaviorGroup:
    items = list(filter(None, items))  # Ensure there are no nulls in the list
    if not items:
        return
    bg = group_list.add()
    if isinstance(bg, BehaviorItem):
        # This method accepts a Union[List[BehaviorGroup], List[BehaviorItem]]
        bg = bg.group
    bg.group_type = group_type
    for item in items:
        bg.children.append(behavior_to_proto(item, is_timed_group=is_timed_group, cur_hp=cur_hp))
    return bg


def add_behavior_group_from_moveset(group_list, group_type, moveset: Moveset) -> BehaviorGroup:
    bg = group_list.add()
    bg.group_type = group_type

    add_behavior_group_from_behaviors(bg.children, BehaviorGroup.DISPEL_PLAYER, [moveset.dispel_action])
    add_behavior_group_from_behaviors(bg.children, BehaviorGroup.MONSTER_STATUS, [moveset.status_action])

    before_idx = len(bg.children)
    for action in moveset.hp_actions:
        hg = bg.children.add().group
        hg.group_type = BehaviorGroup.STANDARD
        hg.condition.hp_threshold = action.hp or 1  # Manually adjust '0' HP groups to <1 (resolve triggers)

        for time_action in action.timed:
            if action.hp == 100 and time_action.execute_above_hp == 1:
                # Insert 'always on turn x' at the top
                bg.children.insert(before_idx, BehaviorItem())
                tg = bg.children[before_idx].group
                before_idx += 1
            else:
                tg = hg.children.add().group

            tg.condition.trigger_turn = time_action.turn
            if time_action.end_turn:
                tg.condition.trigger_turn_end = time_action.end_turn
            if time_action.execute_above_hp:
                tg.condition.always_trigger_above = time_action.execute_above_hp
            add_behavior_group_from_behaviors(tg.children, BehaviorGroup.STANDARD, time_action.skills,
                                              is_timed_group=True, cur_hp=action.hp)

        for repeat_action in action.repeating:
            rg = hg.children.add().group
            if repeat_action.interval > 1:
                rg.condition.trigger_turn = repeat_action.turn
                rg.condition.repeats_every = repeat_action.interval
            if repeat_action.end_turn and repeat_action.end_turn != repeat_action.turn:
                rg.condition.trigger_turn_end = repeat_action.end_turn
            add_behavior_group_from_behaviors(rg.children, BehaviorGroup.STANDARD, repeat_action.skills,
                                              cur_hp=action.hp)

    return bg


def flatten_skillset(level: int, skillset: ProcessedSkillset) -> LevelBehavior:
    result = LevelBehavior()
    result.level = level

    bg = add_behavior_group_from_behaviors(result.groups, BehaviorGroup.PASSIVE, skillset.base_abilities)

    def clean_passive(x):
        trigger_enemies_remaining = x.condition.trigger_enemies_remaining
        x.ClearField('condition')
        # This needs to be enabled for things like turn change with remaining enemies.
        if trigger_enemies_remaining:
            x.condition.trigger_enemies_remaining = trigger_enemies_remaining

    # Passives should have no (few) conditions
    visit_tree(bg, clean_passive)

    bg = add_behavior_group_from_behaviors(result.groups, BehaviorGroup.PREEMPT, skillset.preemptives)

    def clean_preempt(x):
        if_attributes_available = x.condition.if_attributes_available
        trigger_monsters = x.condition.trigger_monsters
        use_chance = x.condition.use_chance
        x.ClearField('condition')
        if if_attributes_available:
            x.condition.if_attributes_available = if_attributes_available
        if trigger_monsters:
            x.condition.trigger_monsters.extend(trigger_monsters)
        if use_chance:
            x.condition.use_chance = use_chance

    # Preempts can only have specific conditions
    visit_tree(bg, clean_preempt)

    bg = add_behavior_group_from_behaviors(result.groups, BehaviorGroup.DEATH, skillset.death_actions)

    def clean_on_death(x):
        x.ClearField('condition')

    # Only condition necessary for death is, well, death
    if bg:
        visit_tree(bg, clean_on_death)
        bg.condition.if_defeated = True

    bg = add_behavior_group_from_moveset(result.groups, BehaviorGroup.STANDARD, skillset.moveset)

    def clean_empty_conditions(x):
        # This just ensures we wipe out empty conditions
        pass

    visit_tree(bg, clean_empty_conditions)

    def clean_enemy_remaining(x):
        x.condition.ClearField('trigger_enemies_remaining')

    if not skillset.enemy_remaining_enabled:
        visit_tree(bg, clean_enemy_remaining)

    for es_moveset in skillset.enemy_remaining_movesets:
        es_bg = add_behavior_group_from_moveset(result.groups, BehaviorGroup.REMAINING, es_moveset)
        # Strip enemy remaining tags from individual items
        visit_tree(es_bg, clean_enemy_remaining)
        # Add it to the top level group
        es_bg.condition.trigger_enemies_remaining = es_moveset.count

    return result


def visit_tree(bg_or_behavior, fn):
    """Recursively apply a function to a tree of behavior.

    Simplifies applying various cleanup operations to an entire tree.
    """
    if not bg_or_behavior:
        return
    fn(bg_or_behavior)

    # Try not to export empty nodes
    if bg_or_behavior.condition == Condition():
        bg_or_behavior.ClearField('condition')

    if hasattr(bg_or_behavior, 'children'):
        for c in bg_or_behavior.children:
            visit_tree(_group_or_behavior(c), fn)


def _group_or_behavior(o: BehaviorItem) -> Union[BehaviorGroup, Behavior]:
    return o.group if o.HasField('group') else o.behavior


def clean_monster_behavior(o: MonsterBehavior) -> MonsterBehavior:
    r = MonsterBehavior()
    r.monster_id = o.monster_id
    r.approved = o.approved
    for level in o.levels:
        r.levels.append(clean_level_behavior(level))
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
    if not r.children:
        return None

    # If this group has only one child, and its child is a group, merge up.
    if len(r.children) == 1 and r.children[0].HasField('group'):
        child = r.children[0].group

        # Set the grandchildren as children
        del r.children[:]
        r.children.extend(child.children)

        # If a condition is present, combine it.
        if child.HasField('condition'):
            r.condition.MergeFrom(child.condition)

    # Removed this - it was pushing up unnecessary stuff.
    #
    # If this group has exactly one child behavior, merge the condition up.
    # if len(r.children) == 1 and r.children[0].HasField('behavior'):
    #     child = r.children[0].behavior
    #     if child.HasField('condition'):
    #         r.condition.MergeFrom(child.condition)
    #         child.ClearField('condition')

    # If this group has two subgroups, the first has hp = 100 and second has hp = 99, update the first HP to 101, which
    # is a special case indicating 'when HP is full'.
    if (len(r.children) > 1 and
            r.children[0].group.condition.hp_threshold == 100 and
            r.children[1].group.condition.hp_threshold == 99):
        r.children[0].group.condition.hp_threshold = 101

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


def add_unused(skills: List[ESInstance], result: LevelBehavior):
    """Add the leftover skills as a new group to behaviors at the end."""
    bg = result.groups.add()
    bg.group_type = BehaviorGroup.UNKNOWN_USE

    for item in skills:
        bg.children.append(behavior_to_proto(item, is_timed_group=False, cur_hp=100))


def safe_save_to_file(file_path: str, obj: MonsterBehavior) -> MonsterBehaviorWithOverrides:
    mbwo = load_from_file(file_path)
    mbwo.monster_id = obj.monster_id
    del mbwo.levels[:]
    mbwo.levels.extend(obj.levels)

    if mbwo.status == MonsterBehaviorWithOverrides.APPROVED_AS_IS:
        old_text = [x.SerializeToString() for x in mbwo.levels]
        new_text = [x.SerializeToString() for x in mbwo.level_overrides]
        if old_text != new_text:
            mbwo.status = MonsterBehaviorWithOverrides.NEEDS_REAPPROVAL

    save_overrides(file_path, mbwo)
    return mbwo


def save_overrides(file_path: str, mbwo: MonsterBehaviorWithOverrides):
    msg_str = text_format.MessageToString(mbwo, as_utf8=True, indent=2)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(msg_str)


def load_from_file(file_path: str) -> MonsterBehaviorWithOverrides:
    mbwo = MonsterBehaviorWithOverrides()
    if os.path.exists(file_path):
        with open(file_path, encoding='utf-8') as f:
            data = f.read()
        text_format.Merge(data, mbwo, allow_unknown_field=True)
    return mbwo
