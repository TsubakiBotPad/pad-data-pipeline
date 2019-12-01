///
//  Generated code. Do not modify.
//  source: enemy_skills.proto
//
// @dart = 2.3
// ignore_for_file: camel_case_types,non_constant_identifier_names,library_prefixes,unused_import,unused_shown_name,return_of_invalid_type

import 'dart:core' as $core;

import 'package:protobuf/protobuf.dart' as $pb;

import 'enemy_skills.pbenum.dart';

export 'enemy_skills.pbenum.dart';

class MonsterBehaviorWithOverrides extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo('MonsterBehaviorWithOverrides', package: const $pb.PackageName('dadguide_proto'), createEmptyInstance: create)
    ..a<$core.int>(1, 'monsterId', $pb.PbFieldType.O3)
    ..pc<LevelBehavior>(2, 'levels', $pb.PbFieldType.PM, subBuilder: LevelBehavior.create)
    ..pc<LevelBehavior>(3, 'levelOverrides', $pb.PbFieldType.PM, subBuilder: LevelBehavior.create)
    ..e<MonsterBehaviorWithOverrides_Status>(4, 'status', $pb.PbFieldType.OE, defaultOrMaker: MonsterBehaviorWithOverrides_Status.NOT_APPROVED, valueOf: MonsterBehaviorWithOverrides_Status.valueOf, enumValues: MonsterBehaviorWithOverrides_Status.values)
    ..hasRequiredFields = false
  ;

  MonsterBehaviorWithOverrides._() : super();
  factory MonsterBehaviorWithOverrides() => create();
  factory MonsterBehaviorWithOverrides.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory MonsterBehaviorWithOverrides.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  MonsterBehaviorWithOverrides clone() => MonsterBehaviorWithOverrides()..mergeFromMessage(this);
  MonsterBehaviorWithOverrides copyWith(void Function(MonsterBehaviorWithOverrides) updates) => super.copyWith((message) => updates(message as MonsterBehaviorWithOverrides));
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static MonsterBehaviorWithOverrides create() => MonsterBehaviorWithOverrides._();
  MonsterBehaviorWithOverrides createEmptyInstance() => create();
  static $pb.PbList<MonsterBehaviorWithOverrides> createRepeated() => $pb.PbList<MonsterBehaviorWithOverrides>();
  @$core.pragma('dart2js:noInline')
  static MonsterBehaviorWithOverrides getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<MonsterBehaviorWithOverrides>(create);
  static MonsterBehaviorWithOverrides _defaultInstance;

  @$pb.TagNumber(1)
  $core.int get monsterId => $_getIZ(0);
  @$pb.TagNumber(1)
  set monsterId($core.int v) { $_setSignedInt32(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasMonsterId() => $_has(0);
  @$pb.TagNumber(1)
  void clearMonsterId() => clearField(1);

  @$pb.TagNumber(2)
  $core.List<LevelBehavior> get levels => $_getList(1);

  @$pb.TagNumber(3)
  $core.List<LevelBehavior> get levelOverrides => $_getList(2);

  @$pb.TagNumber(4)
  MonsterBehaviorWithOverrides_Status get status => $_getN(3);
  @$pb.TagNumber(4)
  set status(MonsterBehaviorWithOverrides_Status v) { setField(4, v); }
  @$pb.TagNumber(4)
  $core.bool hasStatus() => $_has(3);
  @$pb.TagNumber(4)
  void clearStatus() => clearField(4);
}

class MonsterBehavior extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo('MonsterBehavior', package: const $pb.PackageName('dadguide_proto'), createEmptyInstance: create)
    ..a<$core.int>(1, 'monsterId', $pb.PbFieldType.O3)
    ..pc<LevelBehavior>(2, 'levels', $pb.PbFieldType.PM, subBuilder: LevelBehavior.create)
    ..aOB(3, 'approved')
    ..hasRequiredFields = false
  ;

  MonsterBehavior._() : super();
  factory MonsterBehavior() => create();
  factory MonsterBehavior.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory MonsterBehavior.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  MonsterBehavior clone() => MonsterBehavior()..mergeFromMessage(this);
  MonsterBehavior copyWith(void Function(MonsterBehavior) updates) => super.copyWith((message) => updates(message as MonsterBehavior));
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static MonsterBehavior create() => MonsterBehavior._();
  MonsterBehavior createEmptyInstance() => create();
  static $pb.PbList<MonsterBehavior> createRepeated() => $pb.PbList<MonsterBehavior>();
  @$core.pragma('dart2js:noInline')
  static MonsterBehavior getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<MonsterBehavior>(create);
  static MonsterBehavior _defaultInstance;

  @$pb.TagNumber(1)
  $core.int get monsterId => $_getIZ(0);
  @$pb.TagNumber(1)
  set monsterId($core.int v) { $_setSignedInt32(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasMonsterId() => $_has(0);
  @$pb.TagNumber(1)
  void clearMonsterId() => clearField(1);

  @$pb.TagNumber(2)
  $core.List<LevelBehavior> get levels => $_getList(1);

  @$pb.TagNumber(3)
  $core.bool get approved => $_getBF(2);
  @$pb.TagNumber(3)
  set approved($core.bool v) { $_setBool(2, v); }
  @$pb.TagNumber(3)
  $core.bool hasApproved() => $_has(2);
  @$pb.TagNumber(3)
  void clearApproved() => clearField(3);
}

class LevelBehavior extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo('LevelBehavior', package: const $pb.PackageName('dadguide_proto'), createEmptyInstance: create)
    ..a<$core.int>(1, 'level', $pb.PbFieldType.O3)
    ..pc<BehaviorGroup>(2, 'groups', $pb.PbFieldType.PM, subBuilder: BehaviorGroup.create)
    ..hasRequiredFields = false
  ;

  LevelBehavior._() : super();
  factory LevelBehavior() => create();
  factory LevelBehavior.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory LevelBehavior.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  LevelBehavior clone() => LevelBehavior()..mergeFromMessage(this);
  LevelBehavior copyWith(void Function(LevelBehavior) updates) => super.copyWith((message) => updates(message as LevelBehavior));
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static LevelBehavior create() => LevelBehavior._();
  LevelBehavior createEmptyInstance() => create();
  static $pb.PbList<LevelBehavior> createRepeated() => $pb.PbList<LevelBehavior>();
  @$core.pragma('dart2js:noInline')
  static LevelBehavior getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<LevelBehavior>(create);
  static LevelBehavior _defaultInstance;

  @$pb.TagNumber(1)
  $core.int get level => $_getIZ(0);
  @$pb.TagNumber(1)
  set level($core.int v) { $_setSignedInt32(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasLevel() => $_has(0);
  @$pb.TagNumber(1)
  void clearLevel() => clearField(1);

  @$pb.TagNumber(2)
  $core.List<BehaviorGroup> get groups => $_getList(1);
}

class BehaviorGroup extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo('BehaviorGroup', package: const $pb.PackageName('dadguide_proto'), createEmptyInstance: create)
    ..e<BehaviorGroup_GroupType>(1, 'groupType', $pb.PbFieldType.OE, defaultOrMaker: BehaviorGroup_GroupType.UNSPECIFIED, valueOf: BehaviorGroup_GroupType.valueOf, enumValues: BehaviorGroup_GroupType.values)
    ..aOM<Condition>(2, 'condition', subBuilder: Condition.create)
    ..pc<BehaviorItem>(3, 'children', $pb.PbFieldType.PM, subBuilder: BehaviorItem.create)
    ..hasRequiredFields = false
  ;

  BehaviorGroup._() : super();
  factory BehaviorGroup() => create();
  factory BehaviorGroup.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory BehaviorGroup.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  BehaviorGroup clone() => BehaviorGroup()..mergeFromMessage(this);
  BehaviorGroup copyWith(void Function(BehaviorGroup) updates) => super.copyWith((message) => updates(message as BehaviorGroup));
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static BehaviorGroup create() => BehaviorGroup._();
  BehaviorGroup createEmptyInstance() => create();
  static $pb.PbList<BehaviorGroup> createRepeated() => $pb.PbList<BehaviorGroup>();
  @$core.pragma('dart2js:noInline')
  static BehaviorGroup getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<BehaviorGroup>(create);
  static BehaviorGroup _defaultInstance;

  @$pb.TagNumber(1)
  BehaviorGroup_GroupType get groupType => $_getN(0);
  @$pb.TagNumber(1)
  set groupType(BehaviorGroup_GroupType v) { setField(1, v); }
  @$pb.TagNumber(1)
  $core.bool hasGroupType() => $_has(0);
  @$pb.TagNumber(1)
  void clearGroupType() => clearField(1);

  @$pb.TagNumber(2)
  Condition get condition => $_getN(1);
  @$pb.TagNumber(2)
  set condition(Condition v) { setField(2, v); }
  @$pb.TagNumber(2)
  $core.bool hasCondition() => $_has(1);
  @$pb.TagNumber(2)
  void clearCondition() => clearField(2);
  @$pb.TagNumber(2)
  Condition ensureCondition() => $_ensure(1);

  @$pb.TagNumber(3)
  $core.List<BehaviorItem> get children => $_getList(2);
}

enum BehaviorItem_Value {
  group, 
  behavior, 
  notSet
}

class BehaviorItem extends $pb.GeneratedMessage {
  static const $core.Map<$core.int, BehaviorItem_Value> _BehaviorItem_ValueByTag = {
    2 : BehaviorItem_Value.group,
    3 : BehaviorItem_Value.behavior,
    0 : BehaviorItem_Value.notSet
  };
  static final $pb.BuilderInfo _i = $pb.BuilderInfo('BehaviorItem', package: const $pb.PackageName('dadguide_proto'), createEmptyInstance: create)
    ..oo(0, [2, 3])
    ..aOM<BehaviorGroup>(2, 'group', subBuilder: BehaviorGroup.create)
    ..aOM<Behavior>(3, 'behavior', subBuilder: Behavior.create)
    ..hasRequiredFields = false
  ;

  BehaviorItem._() : super();
  factory BehaviorItem() => create();
  factory BehaviorItem.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory BehaviorItem.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  BehaviorItem clone() => BehaviorItem()..mergeFromMessage(this);
  BehaviorItem copyWith(void Function(BehaviorItem) updates) => super.copyWith((message) => updates(message as BehaviorItem));
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static BehaviorItem create() => BehaviorItem._();
  BehaviorItem createEmptyInstance() => create();
  static $pb.PbList<BehaviorItem> createRepeated() => $pb.PbList<BehaviorItem>();
  @$core.pragma('dart2js:noInline')
  static BehaviorItem getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<BehaviorItem>(create);
  static BehaviorItem _defaultInstance;

  BehaviorItem_Value whichValue() => _BehaviorItem_ValueByTag[$_whichOneof(0)];
  void clearValue() => clearField($_whichOneof(0));

  @$pb.TagNumber(2)
  BehaviorGroup get group => $_getN(0);
  @$pb.TagNumber(2)
  set group(BehaviorGroup v) { setField(2, v); }
  @$pb.TagNumber(2)
  $core.bool hasGroup() => $_has(0);
  @$pb.TagNumber(2)
  void clearGroup() => clearField(2);
  @$pb.TagNumber(2)
  BehaviorGroup ensureGroup() => $_ensure(0);

  @$pb.TagNumber(3)
  Behavior get behavior => $_getN(1);
  @$pb.TagNumber(3)
  set behavior(Behavior v) { setField(3, v); }
  @$pb.TagNumber(3)
  $core.bool hasBehavior() => $_has(1);
  @$pb.TagNumber(3)
  void clearBehavior() => clearField(3);
  @$pb.TagNumber(3)
  Behavior ensureBehavior() => $_ensure(1);
}

class Behavior extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo('Behavior', package: const $pb.PackageName('dadguide_proto'), createEmptyInstance: create)
    ..aOM<Condition>(1, 'condition', subBuilder: Condition.create)
    ..a<$core.int>(2, 'enemySkillId', $pb.PbFieldType.O3)
    ..p<$core.int>(3, 'childIds', $pb.PbFieldType.P3)
    ..hasRequiredFields = false
  ;

  Behavior._() : super();
  factory Behavior() => create();
  factory Behavior.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory Behavior.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  Behavior clone() => Behavior()..mergeFromMessage(this);
  Behavior copyWith(void Function(Behavior) updates) => super.copyWith((message) => updates(message as Behavior));
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static Behavior create() => Behavior._();
  Behavior createEmptyInstance() => create();
  static $pb.PbList<Behavior> createRepeated() => $pb.PbList<Behavior>();
  @$core.pragma('dart2js:noInline')
  static Behavior getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Behavior>(create);
  static Behavior _defaultInstance;

  @$pb.TagNumber(1)
  Condition get condition => $_getN(0);
  @$pb.TagNumber(1)
  set condition(Condition v) { setField(1, v); }
  @$pb.TagNumber(1)
  $core.bool hasCondition() => $_has(0);
  @$pb.TagNumber(1)
  void clearCondition() => clearField(1);
  @$pb.TagNumber(1)
  Condition ensureCondition() => $_ensure(0);

  @$pb.TagNumber(2)
  $core.int get enemySkillId => $_getIZ(1);
  @$pb.TagNumber(2)
  set enemySkillId($core.int v) { $_setSignedInt32(1, v); }
  @$pb.TagNumber(2)
  $core.bool hasEnemySkillId() => $_has(1);
  @$pb.TagNumber(2)
  void clearEnemySkillId() => clearField(2);

  @$pb.TagNumber(3)
  $core.List<$core.int> get childIds => $_getList(2);
}

class Condition extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo('Condition', package: const $pb.PackageName('dadguide_proto'), createEmptyInstance: create)
    ..a<$core.int>(1, 'hpThreshold', $pb.PbFieldType.O3)
    ..a<$core.int>(2, 'useChance', $pb.PbFieldType.O3)
    ..a<$core.int>(3, 'repeatsEvery', $pb.PbFieldType.O3)
    ..aOB(4, 'globalOneTime')
    ..a<$core.int>(5, 'triggerEnemiesRemaining', $pb.PbFieldType.O3)
    ..aOB(6, 'ifDefeated')
    ..aOB(7, 'ifAttributesAvailable')
    ..p<$core.int>(8, 'triggerMonsters', $pb.PbFieldType.P3)
    ..a<$core.int>(9, 'triggerCombos', $pb.PbFieldType.O3)
    ..aOB(10, 'ifNothingMatched')
    ..a<$core.int>(11, 'triggerTurn', $pb.PbFieldType.O3)
    ..a<$core.int>(12, 'triggerTurnEnd', $pb.PbFieldType.O3)
    ..hasRequiredFields = false
  ;

  Condition._() : super();
  factory Condition() => create();
  factory Condition.fromBuffer($core.List<$core.int> i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromBuffer(i, r);
  factory Condition.fromJson($core.String i, [$pb.ExtensionRegistry r = $pb.ExtensionRegistry.EMPTY]) => create()..mergeFromJson(i, r);
  Condition clone() => Condition()..mergeFromMessage(this);
  Condition copyWith(void Function(Condition) updates) => super.copyWith((message) => updates(message as Condition));
  $pb.BuilderInfo get info_ => _i;
  @$core.pragma('dart2js:noInline')
  static Condition create() => Condition._();
  Condition createEmptyInstance() => create();
  static $pb.PbList<Condition> createRepeated() => $pb.PbList<Condition>();
  @$core.pragma('dart2js:noInline')
  static Condition getDefault() => _defaultInstance ??= $pb.GeneratedMessage.$_defaultFor<Condition>(create);
  static Condition _defaultInstance;

  @$pb.TagNumber(1)
  $core.int get hpThreshold => $_getIZ(0);
  @$pb.TagNumber(1)
  set hpThreshold($core.int v) { $_setSignedInt32(0, v); }
  @$pb.TagNumber(1)
  $core.bool hasHpThreshold() => $_has(0);
  @$pb.TagNumber(1)
  void clearHpThreshold() => clearField(1);

  @$pb.TagNumber(2)
  $core.int get useChance => $_getIZ(1);
  @$pb.TagNumber(2)
  set useChance($core.int v) { $_setSignedInt32(1, v); }
  @$pb.TagNumber(2)
  $core.bool hasUseChance() => $_has(1);
  @$pb.TagNumber(2)
  void clearUseChance() => clearField(2);

  @$pb.TagNumber(3)
  $core.int get repeatsEvery => $_getIZ(2);
  @$pb.TagNumber(3)
  set repeatsEvery($core.int v) { $_setSignedInt32(2, v); }
  @$pb.TagNumber(3)
  $core.bool hasRepeatsEvery() => $_has(2);
  @$pb.TagNumber(3)
  void clearRepeatsEvery() => clearField(3);

  @$pb.TagNumber(4)
  $core.bool get globalOneTime => $_getBF(3);
  @$pb.TagNumber(4)
  set globalOneTime($core.bool v) { $_setBool(3, v); }
  @$pb.TagNumber(4)
  $core.bool hasGlobalOneTime() => $_has(3);
  @$pb.TagNumber(4)
  void clearGlobalOneTime() => clearField(4);

  @$pb.TagNumber(5)
  $core.int get triggerEnemiesRemaining => $_getIZ(4);
  @$pb.TagNumber(5)
  set triggerEnemiesRemaining($core.int v) { $_setSignedInt32(4, v); }
  @$pb.TagNumber(5)
  $core.bool hasTriggerEnemiesRemaining() => $_has(4);
  @$pb.TagNumber(5)
  void clearTriggerEnemiesRemaining() => clearField(5);

  @$pb.TagNumber(6)
  $core.bool get ifDefeated => $_getBF(5);
  @$pb.TagNumber(6)
  set ifDefeated($core.bool v) { $_setBool(5, v); }
  @$pb.TagNumber(6)
  $core.bool hasIfDefeated() => $_has(5);
  @$pb.TagNumber(6)
  void clearIfDefeated() => clearField(6);

  @$pb.TagNumber(7)
  $core.bool get ifAttributesAvailable => $_getBF(6);
  @$pb.TagNumber(7)
  set ifAttributesAvailable($core.bool v) { $_setBool(6, v); }
  @$pb.TagNumber(7)
  $core.bool hasIfAttributesAvailable() => $_has(6);
  @$pb.TagNumber(7)
  void clearIfAttributesAvailable() => clearField(7);

  @$pb.TagNumber(8)
  $core.List<$core.int> get triggerMonsters => $_getList(7);

  @$pb.TagNumber(9)
  $core.int get triggerCombos => $_getIZ(8);
  @$pb.TagNumber(9)
  set triggerCombos($core.int v) { $_setSignedInt32(8, v); }
  @$pb.TagNumber(9)
  $core.bool hasTriggerCombos() => $_has(8);
  @$pb.TagNumber(9)
  void clearTriggerCombos() => clearField(9);

  @$pb.TagNumber(10)
  $core.bool get ifNothingMatched => $_getBF(9);
  @$pb.TagNumber(10)
  set ifNothingMatched($core.bool v) { $_setBool(9, v); }
  @$pb.TagNumber(10)
  $core.bool hasIfNothingMatched() => $_has(9);
  @$pb.TagNumber(10)
  void clearIfNothingMatched() => clearField(10);

  @$pb.TagNumber(11)
  $core.int get triggerTurn => $_getIZ(10);
  @$pb.TagNumber(11)
  set triggerTurn($core.int v) { $_setSignedInt32(10, v); }
  @$pb.TagNumber(11)
  $core.bool hasTriggerTurn() => $_has(10);
  @$pb.TagNumber(11)
  void clearTriggerTurn() => clearField(11);

  @$pb.TagNumber(12)
  $core.int get triggerTurnEnd => $_getIZ(11);
  @$pb.TagNumber(12)
  set triggerTurnEnd($core.int v) { $_setSignedInt32(11, v); }
  @$pb.TagNumber(12)
  $core.bool hasTriggerTurnEnd() => $_has(11);
  @$pb.TagNumber(12)
  void clearTriggerTurnEnd() => clearField(12);
}

