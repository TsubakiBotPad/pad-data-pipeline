import logging

from pad.common.monster_id_mapping import server_monster_id_fn
from pad.common.shared_types import Server
from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.egg_machine import EggMachine
from pad.storage.egg_machines_monsters import EggMachinesMonster

logger = logging.getLogger('processor')


class EggMachineProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.egg_machines = {
            Server.jp: data.jp_egg_machines,
            Server.na: data.na_egg_machines,
            Server.kr: data.kr_egg_machines,
        }

    def process(self, db: DbWrapper):
        for server, egg_machine_list in self.egg_machines.items():
            logger.debug('Process {} egg machines'.format(server.name.upper()))
            for egg_machine in egg_machine_list:
                em = EggMachine.from_eem(egg_machine, server)
                egg_machine_id = db.insert_or_update(em)

                # process contents of the eggmachines
                id_mapper = server_monster_id_fn(server)
                monsters = [EggMachinesMonster(
                    monster_id=id_mapper(k),
                    roll_chance=v,
                    machine_row=em.machine_row,
                    machine_type=em.machine_type,
                    server_id=em.server_id
                ) for k, v in egg_machine.contents.items()]
                for emm in monsters:
                    db.insert_or_update(emm)
