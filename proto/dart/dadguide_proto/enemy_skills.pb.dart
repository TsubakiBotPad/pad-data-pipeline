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

class MonsterBehavior extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo('MonsterBehavior', package: const $pb.PackageName('dadguide_proto'), createEmptyInstance: create)
    ..pc<BehaviorGroup>(1, 'groups', $pb.PbFieldType.PM, subBuilder: BehaviorGroup.create)
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
  $core.List<BehaviorGroup> get groups => $_getList(0);
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
}

class Condition extends $pb.GeneratedMessage {
  static final $pb.BuilderInfo _i = $pb.BuilderInfo('Condition', package: const $pb.PackageName('dadguide_proto'), createEmptyInstance: create)
    ..a<$core.int>(1, 'hpThreshold', $pb.PbFieldType.O3)
    ..a<$core.int>(2, 'useChance', $pb.PbFieldType.O3)
    ..a<$core.int>(3, 'repeatsEvery', $pb.PbFieldType.O3)
    ..a<$core.int>(4, 'enemiesRemaining', $pb.PbFieldType.O3)
    ..aOB(5, 'onDeath')
    ..aOB(6, 'orbLimited')
    ..p<$core.int>(7, 'triggerMonsters', $pb.PbFieldType.P3)
    ..aOB(8, 'globalOneTime')
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
  $core.int get enemiesRemaining => $_getIZ(3);
  @$pb.TagNumber(4)
  set enemiesRemaining($core.int v) { $_setSignedInt32(3, v); }
  @$pb.TagNumber(4)
  $core.bool hasEnemiesRemaining() => $_has(3);
  @$pb.TagNumber(4)
  void clearEnemiesRemaining() => clearField(4);

  @$pb.TagNumber(5)
  $core.bool get onDeath => $_getBF(4);
  @$pb.TagNumber(5)
  set onDeath($core.bool v) { $_setBool(4, v); }
  @$pb.TagNumber(5)
  $core.bool hasOnDeath() => $_has(4);
  @$pb.TagNumber(5)
  void clearOnDeath() => clearField(5);

  @$pb.TagNumber(6)
  $core.bool get orbLimited => $_getBF(5);
  @$pb.TagNumber(6)
  set orbLimited($core.bool v) { $_setBool(5, v); }
  @$pb.TagNumber(6)
  $core.bool hasOrbLimited() => $_has(5);
  @$pb.TagNumber(6)
  void clearOrbLimited() => clearField(6);

  @$pb.TagNumber(7)
  $core.List<$core.int> get triggerMonsters => $_getList(6);

  @$pb.TagNumber(8)
  $core.bool get globalOneTime => $_getBF(7);
  @$pb.TagNumber(8)
  set globalOneTime($core.bool v) { $_setBool(7, v); }
  @$pb.TagNumber(8)
  $core.bool hasGlobalOneTime() => $_has(7);
  @$pb.TagNumber(8)
  void clearGlobalOneTime() => clearField(8);
}

