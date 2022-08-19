from dataclasses import dataclass
from typing import Tuple

from sshtunnel import SSHTunnelForwarder


@dataclass
class TunnelConfig:  # TODO: custon ssh port
    host: str
    user: str
    password: str
    bind_address: Tuple[str, int]


class Tunnel:
    def __init__(self, config: TunnelConfig):
        self.__config = config
        self.__server = self.__create_server(self.__config)

    def start(self):
        if not self.__server.is_alive and not self.__server.is_active:
            self.__server.start()

        return self.__server.local_bind_address[1]

    def stop(self):
        if self.__server.is_alive and self.__server.is_active:
            self.__server.stop()

    def __create_server(self, config: TunnelConfig) -> SSHTunnelForwarder:
        server = SSHTunnelForwarder(
            config.host,
            ssh_username=config.user,
            ssh_password=config.password,
            remote_bind_address=config.bind_address
        )

        return server
