///
//  Generated code. Do not modify.
//  source: enemy_skills.proto
//
// @dart = 2.3
// ignore_for_file: camel_case_types,non_constant_identifier_names,library_prefixes,unused_import,unused_shown_name,return_of_invalid_type

// ignore_for_file: UNDEFINED_SHOWN_NAME,UNUSED_SHOWN_NAME
import 'dart:core' as $core;
import 'package:protobuf/protobuf.dart' as $pb;

class MonsterBehaviorWithOverrides_Status extends $pb.ProtobufEnum {
  static const MonsterBehaviorWithOverrides_Status NOT_APPROVED = MonsterBehaviorWithOverrides_Status._(0, 'NOT_APPROVED');
  static const MonsterBehaviorWithOverrides_Status APPROVED_AS_IS = MonsterBehaviorWithOverrides_Status._(1, 'APPROVED_AS_IS');
  static const MonsterBehaviorWithOverrides_Status NEEDS_REAPPROVAL = MonsterBehaviorWithOverrides_Status._(2, 'NEEDS_REAPPROVAL');
  static const MonsterBehaviorWithOverrides_Status APPROVED_WITH_CHANGES = MonsterBehaviorWithOverrides_Status._(3, 'APPROVED_WITH_CHANGES');

  static const $core.List<MonsterBehaviorWithOverrides_Status> values = <MonsterBehaviorWithOverrides_Status> [
    NOT_APPROVED,
    APPROVED_AS_IS,
    NEEDS_REAPPROVAL,
    APPROVED_WITH_CHANGES,
  ];

  static final $core.Map<$core.int, MonsterBehaviorWithOverrides_Status> _byValue = $pb.ProtobufEnum.initByValue(values);
  static MonsterBehaviorWithOverrides_Status valueOf($core.int value) => _byValue[value];

  const MonsterBehaviorWithOverrides_Status._($core.int v, $core.String n) : super(v, n);
}

class BehaviorGroup_GroupType extends $pb.ProtobufEnum {
  static const BehaviorGroup_GroupType UNSPECIFIED = BehaviorGroup_GroupType._(0, 'UNSPECIFIED');
  static const BehaviorGroup_GroupType PASSIVE = BehaviorGroup_GroupType._(1, 'PASSIVE');
  static const BehaviorGroup_GroupType PREEMPT = BehaviorGroup_GroupType._(2, 'PREEMPT');
  static const BehaviorGroup_GroupType DISPEL_PLAYER = BehaviorGroup_GroupType._(3, 'DISPEL_PLAYER');
  static const BehaviorGroup_GroupType MONSTER_STATUS = BehaviorGroup_GroupType._(4, 'MONSTER_STATUS');
  static const BehaviorGroup_GroupType REMAINING = BehaviorGroup_GroupType._(5, 'REMAINING');
  static const BehaviorGroup_GroupType STANDARD = BehaviorGroup_GroupType._(6, 'STANDARD');
  static const BehaviorGroup_GroupType DEATH = BehaviorGroup_GroupType._(7, 'DEATH');

  static const $core.List<BehaviorGroup_GroupType> values = <BehaviorGroup_GroupType> [
    UNSPECIFIED,
    PASSIVE,
    PREEMPT,
    DISPEL_PLAYER,
    MONSTER_STATUS,
    REMAINING,
    STANDARD,
    DEATH,
  ];

  static final $core.Map<$core.int, BehaviorGroup_GroupType> _byValue = $pb.ProtobufEnum.initByValue(values);
  static BehaviorGroup_GroupType valueOf($core.int value) => _byValue[value];

  const BehaviorGroup_GroupType._($core.int v, $core.String n) : super(v, n);
}

