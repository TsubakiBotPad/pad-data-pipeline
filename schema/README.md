## Regenerating the schema dump

```bash
mysqldump -u root dadguide -p --no-data > mysql.sql
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
