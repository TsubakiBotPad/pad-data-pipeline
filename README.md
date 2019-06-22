# dadguide-data

## Database setup

```bash
sudo apt install mysql-workbench
sudo apt install mysql-server

```

Acquire an export of the DadGuide database.


Notes about PadGuide database conversion:
```
can maybe autocompute skill rotation list?
enhance mats that skill up rem monsters


sub_dungeon needs new fields:
total_points (mp)
rewards (complex string data, convert to json), might need override
score



monster new fields:
exchangable?

history_jp, history_na, history_us?
i'm only adding 'new added' but padguide had more info


icon list -> get rid of icon_seq probably

```