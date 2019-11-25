///
//  Generated code. Do not modify.
//  source: enemy_skills.proto
//
// @dart = 2.3
// ignore_for_file: camel_case_types,non_constant_identifier_names,library_prefixes,unused_import,unused_shown_name,return_of_invalid_type

const MonsterBehavior$json = const {
  '1': 'MonsterBehavior',
  '2': const [
    const {'1': 'groups', '3': 1, '4': 3, '5': 11, '6': '.dadguide_proto.BehaviorGroup', '10': 'groups'},
  ],
};

const BehaviorGroup$json = const {
  '1': 'BehaviorGroup',
  '2': const [
    const {'1': 'group_type', '3': 1, '4': 1, '5': 14, '6': '.dadguide_proto.BehaviorGroup.GroupType', '10': 'groupType'},
    const {'1': 'condition', '3': 2, '4': 1, '5': 11, '6': '.dadguide_proto.Condition', '10': 'condition'},
    const {'1': 'children', '3': 3, '4': 3, '5': 11, '6': '.dadguide_proto.BehaviorItem', '10': 'children'},
  ],
  '4': const [BehaviorGroup_GroupType$json],
};

const BehaviorGroup_GroupType$json = const {
  '1': 'GroupType',
  '2': const [
    const {'1': 'UNSPECIFIED', '2': 0},
    const {'1': 'PASSIVE', '2': 1},
    const {'1': 'PREEMPT', '2': 2},
    const {'1': 'DISPEL_PLAYER', '2': 3},
    const {'1': 'MONSTER_STATUS', '2': 4},
    const {'1': 'REMAINING', '2': 5},
    const {'1': 'STANDARD', '2': 6},
    const {'1': 'DEATH', '2': 7},
  ],
};

const BehaviorItem$json = const {
  '1': 'BehaviorItem',
  '2': const [
    const {'1': 'group', '3': 2, '4': 1, '5': 11, '6': '.dadguide_proto.BehaviorGroup', '9': 0, '10': 'group'},
    const {'1': 'behavior', '3': 3, '4': 1, '5': 11, '6': '.dadguide_proto.Behavior', '9': 0, '10': 'behavior'},
  ],
  '8': const [
    const {'1': 'value'},
  ],
};

const Behavior$json = const {
  '1': 'Behavior',
  '2': const [
    const {'1': 'condition', '3': 1, '4': 1, '5': 11, '6': '.dadguide_proto.Condition', '10': 'condition'},
    const {'1': 'enemy_skill_id', '3': 2, '4': 1, '5': 5, '10': 'enemySkillId'},
  ],
};

const Condition$json = const {
  '1': 'Condition',
  '2': const [
    const {'1': 'hp_threshold', '3': 1, '4': 1, '5': 5, '10': 'hpThreshold'},
    const {'1': 'use_chance', '3': 2, '4': 1, '5': 5, '10': 'useChance'},
    const {'1': 'repeats_every', '3': 3, '4': 1, '5': 5, '10': 'repeatsEvery'},
    const {'1': 'global_one_time', '3': 8, '4': 1, '5': 8, '10': 'globalOneTime'},
    const {'1': 'enemies_remaining', '3': 4, '4': 1, '5': 5, '10': 'enemiesRemaining'},
    const {'1': 'on_death', '3': 5, '4': 1, '5': 8, '10': 'onDeath'},
    const {'1': 'orb_limited', '3': 6, '4': 1, '5': 8, '10': 'orbLimited'},
    const {'1': 'trigger_monsters', '3': 7, '4': 3, '5': 5, '10': 'triggerMonsters'},
  ],
};

