# dadguide-data

## Database setup

```bash
sudo apt install mysql-workbench
sudo apt install mysql-server

```

Acquire an export of the DadGuide database.


Notes about PadGuide database conversion:
```
skill_leader_data -> move leader_data into leader_skill table, convert to json

can maybe autocompute skill rotation list?
enhance mats that skill up rem monsters


sub_dungeon needs new fields:
total_points (mp)
rewards (complex string data, convert to json), might need override
score



monster new fields:
buy_mp, sell_mp, exchangable (json?)

history_jp, history_na, history_us?
i'm only adding 'new added' but padguide had more info
pal_egg, rare_egg, sell_price, fodder_exp
inheritable, type3


icon list -> get rid of icon_seq probably
denormalize evo_material_list

FK missing from evolution_list
```