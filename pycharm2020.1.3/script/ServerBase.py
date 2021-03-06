from __future__ import annotations
import asyncio
import functools
# import json
import random
import signal
import platform
import sys
# from random import random
import socket

# from PuppetBindEntity import PuppetBindEntity
# from battle_entity.Puppet import Puppet
# from core.common import MsgpackSupport
from asyncio import events, tasks, transports

import typing

# from core.util.performance.cpu_load_handler import CpuLoad
import ConnBase
from ConnMgr import ConnMgr
from ProxyRpcHandler import ProxyCliRpcHandler
from core.util import UtilApi
from core.util.UtilApi import wait_or_not, Singleton
from RpcHandler import get_a_rpc_handler_id

if typing.TYPE_CHECKING:
    from RpcHandler import RpcHandler

import TcpConn
# from common import gv
from core.EtcdSupport import ServiceNode
# from core.common import EntityScanner
# from core.common.EntityFactory import EntityFactory
from core.mobilelog.LogManager import LogManager
# from core.util import EnhancedJson
from core.util.TimerHub import TimerHub
# from util.SingletonEntityManager import SingletonEntityManager
from common import gv
from core.common import EntityScanner
from core.common.EntityFactory import EntityFactory
from core.tool import incremental_reload
# from core.tool import incremental_reload

# TCP_SERVER = None


class ServerBase:

    def __init__(self, server_name, etcd_tag, json_conf_path, is_proxy=False):
        UtilApi.parse_json_conf(json_conf_path)
        gv.etcd_tag = etcd_tag

        self._is_proxy = is_proxy

        self._ev_loop = gv.get_ev_loop()
        # print(f"TcpServer._ev_loop is {id(self._ev_loop)=}")
        # self._ev_loop.set_debug(gv.is_dev_version)

        # events.set_event_loop(self._ev_loop)

        self._timer_hub = TimerHub()
        # self._conn_mgr = ConnMgr()

        # self._addr_2_conn_map = {}
        self._etcd_service_node = None  # type: typing.Optional[ServiceNode]
        # self.register_entities()

        gv.server_name = server_name

        LogManager.set_log_tag(gv.server_name)
        LogManager.set_log_path(gv.game_json_conf["log_path"])
        self._logger = LogManager.get_logger()

        # gv.add_server_singleton(self)

        self._register_server_entities()
        # self.register_battle_entities()
        self._register_component()

        incremental_reload.init_reload_record()  # 注意!! 一定要放到EntityScanner注册了的代码之后, 不然sys.modules里没相关的模块

        ConnMgr.instance().set_is_proxy(is_proxy)
        self._addr_2_conn_map = {}  # type: typing.Dict[typing.Tuple[str, int], TcpConn.TcpConn]

        gv.server_inst = self

    def _register_component(self):
        from common.component.Component import Component
        from common.component import ComponentRegister
        # gameconfig = self.config[self.config_sections.game]
        component_root = gv.game_json_conf.get('component_root')
        if component_root is None:
            self._logger.error('conf file has no component_root!')
            return
        component_classes = EntityScanner.scan_entity_package(component_root, Component)
        component_classes = component_classes.items()
        # component_classes.sort(lambda a, b: cmp(a[0], b[0]))
        for comp_type, comp_cls in component_classes:
            ComponentRegister.register(comp_cls)

    # def register_battle_entities(self):
    #     from BattleEntity import BattleEntity
    #     _ber = gr.game_json_conf.get('battle_entity_root', None)
    #     if _ber is None:
    #         self.logger.error('conf file has no battle_entity_root!')
    #         return
    #     entity_classes = EntityScanner.scan_entity_package(_ber, BattleEntity)
    #     entity_classes = entity_classes.items()
    #
    #     # def cmp(x, y):
    #     #     if x < y:
    #     #         return -1
    #     #     elif x == y:
    #     #         return 0
    #     #     else:
    #     #         return 1
    #     #
    #     # entity_classes.sort(lambda a, b: cmp(a[0], b[0]))
    #     for cls_name, cls in entity_classes:
    #         EntityFactory.instance().register_entity(cls_name, cls)

    @staticmethod
    def _register_server_entities():
        from BattleEntity import BattleEntity
        from LobbyEntity import LobbyEntity
        from server_entity.ServerEntity import ServerEntity
        _ser = gv.game_json_conf.get('server_entity_root', None)
        _ler = gv.game_json_conf.get('lobby_entity_root', None)
        _ber = gv.game_json_conf.get('battle_entity_root', None)
        if _ser is None:
            # self.logger.error('conf file has no server_entity_root!')
            raise Exception('conf file has no server_entity_root!')
        if _ler is None:
            # self.logger.error('conf file has no server_entity_root!')
            raise Exception('conf file has no lobby_entity_root!')
        if _ber is None:
            # self.logger.error('conf file has no server_entity_root!')
            raise Exception('conf file has no battle_entity_root!')
            # return
        _temp = {_ser: ServerEntity,
                 _ler: LobbyEntity,
                 _ber: BattleEntity}
        for _ent_root, _ent_cls in _temp.items():
            entity_classes = EntityScanner.scan_entity_package(
                _ent_root, _ent_cls)
            entity_classes = entity_classes.items()
            for cls_name, cls in entity_classes:
                EntityFactory.instance().register_entity(cls_name, cls)

    # def forward(self, addr, message):
    #     for _addr, _tcp_conn in self._addr_2_conn_map.items():
    #         # if w != writer:
    #             # w.write(f"{addr!r}: {message!r}\n".encode())
    #             # w.write(MsgpackSupport.encode(f"{addr!r}: {message!r}\n"))
    #         _tcp_conn.send_msg(f"{addr!r}: {message!r}\n")

    # def _add_conn(
    #         self,
    #         role_type: int,
    #         writer: asyncio.StreamWriter,
    #         reader: asyncio.StreamReader,
    #         rpc_handler: RpcHandler = None
    # ):
    #     addr = writer.get_extra_info("peername")
    #     conn = TcpConn.TcpConn(
    #         role_type, addr, writer, reader, rpc_handler,
    #         close_cb=lambda: self._remove_conn(addr))
    #     self._addr_2_conn_map[addr] = conn
    #     return conn
    #
    # def _remove_conn(self, addr: typing.Tuple[str, int]):
    #     self._addr_2_conn_map.pop(addr, None)
    #
    # async def open_conn_by_addr(self, addr: typing.Tuple[str, int], rpc_handler: RpcHandler):
    #     _conn = self._addr_2_conn_map.get(addr, None)
    #     if _conn is None:
    #         reader, writer = await asyncio.open_connection(addr[0], addr[1])
    #         _conn = self._add_conn(TcpConn.ROLE_TYPE_ACTIVE, writer, reader, rpc_handler)
    #     return _conn

    # def _on_conn_close(self,  addr: typing.Tuple[str, int]):
    #     self._addr_2_conn_map.pop(addr, None)
    #
    # def _create_conn(self, role_type, transport: transports.BaseTransport) -> ConnBase.ConnBase:
    #     raise NotImplementedError

    async def _start_server_task(self):
        raise NotImplementedError

    # def _handle_client_connected(self, reader, writer):
    #     # self._add_conn(TcpConn.ROLE_TYPE_PASSIVE, writer, reader)
    #     ConnMgr.instance().add_incoming_conn(
    #         ConnBase.ROLE_TYPE_PASSIVE, writer, reader,
    #         # rpc_handler=ProxyCliRpcHandler(get_a_rpc_handler_id()) if self._is_proxy else None
    #         # is_proxy=self._is_proxy
    #     )
    #     addr = writer.get_extra_info('peername')  # type: typing.Tuple[str, int]
    #     self._logger.info(f"{addr!r} is connected !!!!")
    #
    # async def _start_server_task(self):
    #     # server = await asyncio.start_server(
    #     #     handle_echo, '192.168.82.177', 8888)
    #     # _ip = gr.game_json_conf[gr.server_name]["ip"]
    #     # _port = gr.game_json_conf[gr.server_name]["port"]
    #     try:
    #         server = await asyncio.start_server(
    #             self._handle_client_connected, gv.local_ip, gv.local_port)
    #         # _start_srv_task = asyncio.create_task(asyncio.start_server(self.handle_client_connected, '192.168.82.177', 8888))
    #         # await _etcd_support_task
    #         # server = await _start_srv_task
    #         addr = server.sockets[0].getsockname()
    #         self._logger.info(f'Server on {addr}')
    #
    #         async with server:
    #             await server.serve_forever()
    #     except KeyboardInterrupt:
    #         self._logger.info(f"\nShutting Down Server: {gv.server_name}...\n")
    #         # _loop = asyncio.get_running_loop()
    #         # _loop.stop()
    #         # _loop.close()
    #         # server.close()
    #
    #         return
    #     except:
    #         # self.logger.info("Unexpected error:", sys.exc_info()[0])
    #         self._logger.log_last_except()

    async def _start_etcd_task(self):
        etcd_addr_list = [
            (ip_port_map["ip"], str(ip_port_map["port"])) for ip_port_map in gv.game_json_conf["etcd_servers"]]

        # _ip = gr.game_json_conf[gr.server_name]["ip"]
        # _port = gr.game_json_conf[gr.server_name]["port"]
        my_addr = (gv.local_ip, str(gv.local_port))

        # service_module_dict = {"BattleAllocatorCenter": ""} if gr.server_name == "battle_0" else {
        #     "BattleAllocatorStub": ""}

        # gv.etcd_tag = gv.game_json_conf[gv.server_name]["etcd_tag"]
        self._etcd_service_node = ServiceNode(etcd_addr_list, my_addr, gv.etcd_tag, gv.server_name)
        # self._etcd_service_node = ServiceNode(etcd_addr_list, my_addr, {"BattleAllocatorStub": ""})
        gv.etcd_service_node = self._etcd_service_node
        await self._etcd_service_node.start()

    def _handle_sig(self):

        def ask_exit(sig_name, loop):
            self._logger.info('got signal %s: exit' % sig_name)
            try:
                loop.stop()
            except RuntimeError:
                pass

        if platform.system() != 'Linux':
            return
        # _loop = asyncio.get_running_loop()
        for _sig_name in {'SIGINT', 'SIGTERM'}:
            self._ev_loop.add_signal_handler(
                getattr(signal, _sig_name), functools.partial(ask_exit, _sig_name, self._ev_loop))

    #         raise

    async def _main(self):
        try:
            self._handle_sig()

            gv.local_ip = gv.game_json_conf[gv.server_name]["ip"]
            gv.local_port = gv.game_json_conf[gv.server_name]["port"]

            _etcd_support_task = asyncio.create_task(self._start_etcd_task())
            _start_srv_task = asyncio.create_task(self._start_server_task())

            await _etcd_support_task
            await _start_srv_task
        except:
            self._logger.log_last_except()

    def run(self):
        try:
            # events.set_event_loop(loop)
            # if debug is not None:
            #     loop.set_debug(debug)
            # return loop.run_until_complete(main)
            self._ev_loop.run_until_complete(self._main())
        finally:
            try:
                # _cancel_all_tasks(self._ev_loop)
                loop = self._ev_loop
                to_cancel = tasks.all_tasks(loop)
                if not to_cancel:
                    return

                for task in to_cancel:
                    task.cancel()

                loop.run_until_complete(
                    tasks.gather(*to_cancel, loop=loop, return_exceptions=True))

                for task in to_cancel:
                    if task.cancelled():
                        continue
                    if task.exception() is not None:
                        loop.call_exception_handler({
                            'message': 'unhandled exception during asyncio.run() shutdown',
                            'exception': task.exception(),
                            'task': task,
                        })
                self._ev_loop.run_until_complete(self._ev_loop.shutdown_asyncgens())
            finally:
                events.set_event_loop(None)
                self._ev_loop.close()
        # self._ev_loop.run_until_complete(self.main())
        # asyncio.run(self.main())

    # def _check_game_start(self):
    #     # 随机种子
    #     # random.seed()
    #     # 得到本机ip
    #     try:
    #         gr.local_ip = socket.gethostbyname(socket.gethostname())
    #     except socket.gaierror:
    #         gr.local_ip = '127.0.0.1'
    #     # self._register_singleton()
    #
    # # def _register_singleton(self):
    #     # 创建各种server/cluster singleton
    #     SingletonEntityManager.instance().register_centers_and_stubs(
    #         gr.server_name,
    #         lambda flag: self._register_centers_and_stubs_cb(flag))
    #
    # def _register_centers_and_stubs_cb(self, flag):
    #     pass


if __name__ == '__main__':
    game_server_name = sys.argv[1]
    server_json_conf_path = r"../bin/win/conf/battle_server.json"
    tcp_server = TcpServer(game_server_name, server_json_conf_path)
    # TCP_SERVER = tcp_server
    tcp_server.run()

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
