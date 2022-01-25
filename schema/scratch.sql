CREATE TABLE d_fixed_slot_type (
  fixed_slot_type_id INTEGER NOT NULL,
  name TEXT,
  PRIMARY KEY (fixed_slot_type_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE fixed_teams (
  fixed_team_id INTEGER NOT NULL,
  sub_dungeon_id INTEGER NOT NULL,
  tstamp INTEGER NOT NULL,
  PRIMARY KEY (fixed_team_id),
  KEY tstamp_idx (tstamp),
  CONSTRAINT fixed_teams_fk_sub_dungeon_id FOREIGN KEY (sub_dungeon_id) REFERENCES sub_dungeons (sub_dungeon_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE fixed_teams_na (
  fixed_team_id INTEGER NOT NULL,
  sub_dungeon_id INTEGER NOT NULL,
  tstamp INTEGER NOT NULL,
  PRIMARY KEY (fixed_team_id),
  KEY tstamp_idx (tstamp),
  CONSTRAINT fixed_teams_na_fk_sub_dungeon_id FOREIGN KEY (sub_dungeon_id) REFERENCES sub_dungeons_na (sub_dungeon_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE fixed_team_monsters (
  fixed_team_monster_id INTEGER NOT NULL AUTO_INCREMENT,
  fixed_team_id INTEGER NOT NULL,
  fixed_slot_type_id INTEGER NOT NULL,
  alt_monster_id INTEGER,
  monster_level INTEGER,
  plus_hp INTEGER,
  plus_atk INTEGER,
  plus_rcv INTEGER,
  awakening_count INTEGER,
  skill_level INTEGER,
  /* Figure out a way to do latents */
  assist_alt_monster_id INTEGER,
  super_awakening_id INTEGER,
  order_idx INTEGER NOT NULL,
  tstamp INTEGER NOT NULL,
  PRIMARY KEY (fixed_team_monster_id),
  KEY tstamp_idx (tstamp),
  CONSTRAINT fixed_team_monsters_fk_fixed_slot_type_id FOREIGN KEY (fixed_slot_type_id) REFERENCES d_fixed_slot_type (fixed_slot_type_id),
  CONSTRAINT fixed_team_monsters_fk_fixed_team_id FOREIGN KEY (fixed_team_id) REFERENCES fixed_teams (fixed_team_id),
  CONSTRAINT fixed_team_monsters_fk_alt_monster_id FOREIGN KEY (alt_monster_id) REFERENCES alt_monsters (alt_monster_id),
  CONSTRAINT fixed_team_monsters_fk_assist_alt_monster_id FOREIGN KEY (assist_alt_monster_id) REFERENCES alt_monsters (alt_monster_id),
  CONSTRAINT fixed_team_monsters_fk_super_awakening_id FOREIGN KEY (super_awakening_id) REFERENCES awoken_skills (awoken_skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE fixed_team_monsters_na (
  fixed_team_monster_id INTEGER NOT NULL AUTO_INCREMENT,
  fixed_team_id INTEGER NOT NULL,
  fixed_slot_type_id INTEGER NOT NULL,
  alt_monster_id INTEGER,
  monster_level INTEGER,
  plus_hp INTEGER,
  plus_atk INTEGER,
  plus_rcv INTEGER,
  awakening_count INTEGER,
  skill_level INTEGER,
  /* Figure out a way to do latents */
  assist_alt_monster_id INTEGER,
  super_awakening_id INTEGER,
  order_idx INTEGER NOT NULL,
  tstamp INTEGER NOT NULL,
  PRIMARY KEY (fixed_team_monster_id),
  KEY tstamp_idx (tstamp),
  CONSTRAINT fixed_team_monsters_na_fk_fixed_slot_type_id FOREIGN KEY (fixed_slot_type_id) REFERENCES d_fixed_slot_type (fixed_slot_type_id),
  CONSTRAINT fixed_team_monsters_na_fk_fixed_team_id FOREIGN KEY (fixed_team_id) REFERENCES fixed_teams_na (fixed_team_id),
  CONSTRAINT fixed_team_monsters_na_fk_alt_monster_id FOREIGN KEY (alt_monster_id) REFERENCES alt_monsters_na (alt_monster_id),
  CONSTRAINT fixed_team_monsters_na_fk_assist_alt_monster_id FOREIGN KEY (assist_alt_monster_id) REFERENCES alt_monsters_na (alt_monster_id),
  CONSTRAINT fixed_team_monsters_na_fk_super_awakening_id FOREIGN KEY (super_awakening_id) REFERENCES awoken_skills (awoken_skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
