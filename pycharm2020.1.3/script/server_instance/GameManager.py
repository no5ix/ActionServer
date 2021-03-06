import sys

from TcpServer import TcpServer
# from common import gr
from core.mobilelog.LogManager import LogManager


class GameManager(object):

    def __init__(self, server_name):
        # server_name = sys.argv[1]

        server_json_conf_path = r"../bin/win/conf/battle_server.json"
        self._server = TcpServer(server_name, server_json_conf_path)
        self._logger = LogManager.get_logger()

    def start(self):
        self._server.run()


if __name__ == '__main__':
    game_server_name = sys.argv[1]
    bs = GameManager(game_server_name)
    bs.start()

