from common import service_const, gv
# from common.service_const import DISPATCHER_SERVICE
from core.util import UtilApi
from core.util.performance.cpu_load_handler import AvgCpuLoad
from server_entity.ServerEntity import ServerEntity


class LoadReporter(ServerEntity):

    def __init__(self):
        super().__init__()
        self._avg_load = AvgCpuLoad()
        self.timer_hub.call_later(1, self.report_load, repeat_count=-1, repeat_interval_sec=5)

    def report_load(self):
        dispatcher_service_addr = UtilApi.get_service_info(service_const.DISPATCHER_SERVICE)
        if dispatcher_service_addr:
            print(f"report_server_load: {self._avg_load.get_avg_cpu_by_period(5)}")
            self.call_remote_method(
                "report_load", {"sn": gv.game_server_name, "l": self._avg_load.get_avg_cpu_by_period(5)},
                "LoadCollector", dispatcher_service_addr)
        else:
            self.logger.error("can not find dispatcher_service_addr")
