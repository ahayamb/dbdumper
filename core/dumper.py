import datetime
import os
import subprocess
from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass
from typing import Tuple

from core.config import config
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
            mod_conn.host = "localhost"
            mod_conn.port = local_port

        filename, _ = self.dump_db(mod_conn)
        saved_filename = filename
        if config.ENABLE_COMPRESSION:
            from zipfile import ZipFile, ZIP_LZMA

            compressed_filename = '%s.zip' % (filename)
            with ZipFile(compressed_filename, mode="w", compresslevel=4, compression=ZIP_LZMA, allowZip64=True) as zf:
                zf.write(filename)

            os.remove(filename)
            saved_filename = compressed_filename

        if self.__tunnel:
            self.__tunnel.stop()

        return saved_filename

    def get_name(self):
        location = config.DUMP_LOCATION
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
        binary = os.path.join(config.BINARY_LOCATION, "mysql", "mysqldump")

        p = subprocess.Popen([
            binary,
            "--no-tablespaces",
            "-h", conn_config.host,
            "--protocol=tcp",
            "--max-allowed-packet=1GB",
            "-P", str(conn_config.port),
            "-u", conn_config.user,
            "-p%s" % (conn_config.password),
            conn_config.database,
            "-r", current_name
        ])
        os.waitpid(p.pid, 0)

        return current_name, True


class PgDumper(Dumper):

    def dump_db(self, conn_config: ConnConfig):
        current_name = self.get_name()

        binary = os.path.join(config.BINARY_LOCATION, "postgres", "pg_dump")
        cenv = os.environ.copy()
        cenv["PGPASSWORD"] = conn_config.password
        p = subprocess.Popen([
            binary,
            "-h", conn_config.host,
            "-p", str(conn_config.port),
            "-U", conn_config.user,
            "-d", conn_config.database,
            "-f", current_name
        ], env=cenv)
        os.waitpid(p.pid, 0)

        return current_name, True
