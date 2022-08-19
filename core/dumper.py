import datetime
import os
import subprocess
from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass
from typing import Tuple

from core.tunnel import Tunnel, TunnelConfig


@dataclass
class ConnConfig:
    host: str
    user: str
    password: str
    port: int
    database: str


class Dumper():
    def __init__(self, conn_config: ConnConfig, tunnel_config: TunnelConfig):
        self.__tunnel = Tunnel(tunnel_config)
        self.__conn = conn_config

    def dump(self):
        mod_conn = ConnConfig(**self.__conn.__dict__)
        if self.__tunnel:
            local_port = self.__tunnel.start()
            print(local_port)
            mod_conn.host = "localhost"
            mod_conn.port = local_port

        self.dump_db(mod_conn)

        if self.__tunnel:
            self.__tunnel.stop()

    def dump_with_callback(self, callback):
        self.dump()
        callback()

    def get_name(self):
        location = os.environ.get("DUMPER_PATH", "backup")
        current_date = datetime.datetime.now().astimezone().strftime('%Y-%m-%d')
        if not os.path.exists(location):
            os.makedirs(location)
        return os.path.join(location, "%s_%s.sql" % (self.__conn.database, current_date))

    @abstractmethod
    def dump_db(self, conn_config: ConnConfig) -> Tuple[str, bool]:
        raise NotImplementedError()


class MySqlDumper(Dumper):

    def dump_db(self, conn_config: ConnConfig):
        current_name = self.get_name()
        command = "bin/mysql/mysqldump -h %s --protocol=tcp -P %s -u %s -p%s %s > %s" % (
            conn_config.host, conn_config.port, conn_config.user, conn_config.password, conn_config.database, current_name)

        p = subprocess.Popen(command, shell=True)
        os.waitpid(p.pid, 0)

        return current_name, True


class PgDumper(Dumper):

    def dump_db(self, conn_config: ConnConfig):
        current_name = self.get_name()
        command = "PGPASSWORD=%s bin/postgres/pg_dump -h %s -p %s -U %s -d %s > %s" % (
            conn_config.password, conn_config.host, conn_config.port, conn_config.user, conn_config.database, current_name)

        p = subprocess.Popen(command, shell=True)
        os.waitpid(p.pid, 0)

        return current_name, True
