## Regenerating the schema dump

This is generally very out of date. It's not actually used for anything.

```bash
mysqldump -u root dadguide -p --no-data > mysql.sql
```

## Dumping a built database to sqlite

```bash
rm dadguide.sqlite
./mysql2sqlite.sh -u root -p<password> dadguide | sqlite3 dadguide.sqlite
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

## Deleting records

Tables with computed IDs will generally be autocreated and shouldn't be deleted, instead they should have a column added
to hide them from display.

For tables that are autoincrement ID keyed, we may need to delete records (e.g. for `encounters`).

This is done by automatically inserting a row into the `deleted_rows` table via a trigger on the table, created like:

```sql
delimiter #
CREATE TRIGGER encounters_deleted
AFTER DELETE ON encounters
FOR EACH ROW
BEGIN
  INSERT INTO deleted_rows (table_name, table_row_id, tstamp) VALUES ('encounters', OLD.encounter_id, UNIX_TIMESTAMP());
END#
```
