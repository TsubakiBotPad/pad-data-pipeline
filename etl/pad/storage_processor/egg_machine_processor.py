import logging

from pad.common.shared_types import Server
from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.egg_machine import EggMachine

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
                item = EggMachine.from_eem(egg_machine, server)
                db.insert_or_update(item)
