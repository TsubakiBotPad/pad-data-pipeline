# PAD Data Processing

This folder contains the ETL pipeline that downloads raw PAD data (and saves it), converts it to a more useful format (
and saves it), and then applies updates to the DadGuide database.

If you're looking to do your own processing, start with `etl/pad/raw`.

If you're interested in duplicating this whole process, you should probably contact tactical_retreat, it's somewhat
involved.

I use shell scripts triggered via cron to execute the various scripts.

## Scripts in this directory

The scripts here do all the data updating, and also some misc utility stuff.

### Primary data pull

| Script                      | Purpose                                               |
| ---                         | ---                                                   |
| pad_data_pull.py            | Downloads PAD data from server via API                |
| data_processor.py           | Updates PadGuide database, writes processed files     |
| default_db_config.json      | Dummy file for DG database connection                 |

You don't need to run `pad_data_pull.py`; all the results of calling the API are published, see the `utils` directory
for information on how to access them.

`data_processor.py` is only neccessary if you want to maintain your own copy of the DadGuide database. The database is
published after each update, see the `utils` directory.

### Secondary data pull stuff

| Script                      | Purpose                                               |
| ---                         | ---                                                   |
| auto_dungeon_scrape.py      | Identifies dungeons with no data and starts loader    |
| pad_dungeon_pull.py         | Actually pulls the dungen spawns and saves them       |
| media_copy.py               | Moves image files into place for DadGuide             |

### Enemy skills

| Script                      | Purpose                                               |
| ---                         | ---                                                   |
| rebuild_enemy_skills.py     | Rebuilds the enemy skill flat file database           |

# Testing/Utility

| Script                      | Purpose                                               |
| ---                         | ---                                                   |

## etl

Contains all the library code that the scripts in this directory rely on. It does the data pulling, processing,
formatting, and database updating. There's a lot of stuff in here.

## dadguide_proto

Contains the Python bindings for the DadGuide protocol buffers. Currently only used for enemy skills. 
