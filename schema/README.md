## Regenerating the schema dump

```bash
mysqldump -u root dadguide -p --no-data > mysql.sql

# TODO: need to reset autoinsert on dump?
```

## Dumping a built database to sqlite

```bash

./mysql2sqlite.sh -u root -p <password> dadguide
```

## Clearing the local database

```sql
delete from schedule where true;
delete from news where true;

delete from awakenings where true;
delete from awoken_skills where true;

delete from drops where true;
delete from encounters where true;
delete from sub_dungeons where true;
delete from dungeons where true;

delete from evolutions where true;
delete from monsters where true;
delete from leader_skills where true;
delete from active_skills where true;

delete from d_attributes;
delete from d_types;
```

## WIP tables

### Mostly settled

* active_skills
* awakenings
* awoken_skills
* d_attributes
* d_types
* evolutions
* leader_skills
* monsters
* timestamps

### Needs work (some, a lot)

* dungeon
* dungeon_monster
* dungeon_monster_drop
* dungeon_sublevel
* dungeon_type
* news
* rank_reward
* schedule
* series
* skill_condition
