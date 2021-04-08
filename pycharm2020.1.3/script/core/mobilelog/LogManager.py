import os
import sys

from datetime import time as dt_time
# import platform
import logging
import time
from concurrent.futures.thread import ThreadPoolExecutor
# from functools import wraps
from logging.handlers import TimedRotatingFileHandler

# import aiologger
#
# from aiologger.handlers.files import (
#     AsyncFileHandler,
#     BaseAsyncRotatingFileHandler,
#     AsyncTimedRotatingFileHandler,
#     RolloverInterval,
#     ONE_WEEK_IN_SECONDS,
#     ONE_DAY_IN_SECONDS,
#     ONE_MINUTE_IN_SECONDS,
#     ONE_HOUR_IN_SECONDS,
# )
#
#
# from aiologger.utils import get_running_loop
# from aiologger.filters import StdoutFilter
# from aiologger.handlers.streams import AsyncStreamHandler
# from aiologger.levels import LogLevel
# from aiologger.logger import Logger
# from aiologger.records import LogRecord
# # from tests.utils import make_read_pipe_stream_reader
# from aiologger.formatters.base import Formatter
import inspect


_log_tp_executor = ThreadPoolExecutor(max_workers=1)  # 1 for sequentiality


class WholeIntervalRotatingFileHandler(TimedRotatingFileHandler):

    def computeRollover(self, currentTime):
        if self.when[0] == 'W' or self.when == 'MIDNIGHT':
            # use existing computation
            return super().computeRollover(currentTime)
        # round time up to nearest next multiple of the interval
        print(f"cur ts: {int(time.time())}")
        print(f"currentTime: {currentTime}")
        # print("\033[1;31;40m您输入的帐号或密码错误！\033[0m")
        # print("\033[0;31m%s\033[0m" % "输出红色字符")
        print(f"dssss: {((currentTime // self.interval) + 1) * self.interval}")
        return ((currentTime // self.interval) + 1) * self.interval

    def doRollover(self):
        super(WholeIntervalRotatingFileHandler, self).doRollover()


class LogManager:
    log_tag = ""
    log_path = ""
    file_handler = None
    stream_handler = None

    @staticmethod
    def set_log_tag(tag):
        LogManager.log_tag = tag

    @staticmethod
    def set_log_path(path):
        LogManager.log_path = path

    @staticmethod
    def get_logger(logger_name=None):
        if logger_name is None:
            try:
                # st = inspect.stack()
                # sta1 = inspect.stack()[1]
                caller_module = inspect.stack()[1][0]
                if "self" in caller_module.f_locals:
                    logger_name = caller_module.f_locals["self"].__class__.__name__
                elif "cls" in caller_module.f_locals:
                    logger_name = caller_module.f_locals["cls"].__name__
                else:
                    logger_name = inspect.getmodule(caller_module).__name__
            except:
                raise Exception("logger_name is None and can't get caller name")
        if LogManager.file_handler is None:
            if LogManager.log_tag == "":
                raise Exception("LogManager Error: log tag is empty!")
            # LogManager.file_handler = TimedRotatingFileHandler(
            LogManager.file_handler = WholeIntervalRotatingFileHandler(
                "".join((LogManager.log_path + LogManager.log_tag + ".log"
                         # + "." + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
                         ))
                , when="M")
        if LogManager.stream_handler is None:
            LogManager.stream_handler = logging.StreamHandler()
            # LogManager.file_handler.doRollover()
        return AsyncLogger(logger_name)
        # _temp_file_name = 'test_log.log'
        #
        # use_st_logger = True
        # # _th_executor = ThreadPoolExecutor(max_workers=1)
        # # _th_executor.submit()
        # # if platform.system() == 'Linux':
        # if use_st_logger:
        #     # logger = logging.getLogger(logger_name)
        #     # # logger.setLevel(logging.DEBUG)
        #     # fh = TimedRotatingFileHandler('test_log.log', when='D')
        #     # # fh = TimedRotatingFileHandler(_temp_file_name, when='S')
        #     # # fh.setLevel(logging.DEBUG)
        #     #
        #     # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] : %(message)s')
        #     # fh.setFormatter(formatter)
        #     # logger.addHandler(fh)
        #     # # fh.setLevel(logging.DEBUG)
        #     # logger.setLevel(logging.DEBUG)
        #     # # logger.shu
        #
        #     return AsyncLogger(logger_name)
        # # else:
        # #     logger = aiologger.logger.Logger()
        # #     handler = AsyncTimedRotatingFileHandler(
        # #         # filename=self.temp_file.name,
        # #         filename=_temp_file_name,
        # #         when=RolloverInterval.SECONDS,
        # #
        # #         # backup_count=1,
        # #     )
        # #     # handler.stream
        # #     formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] : %(message)s')
        # #     handler.formatter = formatter
        # #     logger.add_handler(handler)
        # #     logger.level = LogLevel.INFO
        # #
        # #     # if __name__ == '__main__':
        # #     #
        # #     #     # async def main():
        # #     #     #     logger = LogManager.get_logger('test_logger')
        # #     #     #
        # #     #     # # 'application' code
        # #     #     #     await logger.debug('debug message')
        # #     #     #     await logger.info('info message')
        # #     #     #     await logger.warning('warn message')
        # #     #     #     await logger.error('error message')
        # #     #     #     await logger.critical('critical message')
        # #     #     #     # await logger.shutdown()
        # #     #     #
        # #     #     # import asyncio
        # #     #     #
        # #     #     # loop = asyncio.get_event_loop()
        # #     #     # loop.run_until_complete(main())
        # #     #     # loop.close()
        # #
        # #     return logger


class AsyncLogger:

    def __init__(self, logger_name):
        # logging.basicConfig(
        #     format='%(asctime)s - %(name)s - %(levelname)s : %(message)s',
        #     handlers=[TimedRotatingFileHandler(
        #         LogManager.log_path + LogManager.log_tag + ".log", when='S')],
        # )
        self._logger = logging.getLogger(logger_name)

        # fh = TimedRotatingFileHandler(
        #     LogManager.log_path + LogManager.log_tag + ".log", when='D')
        # fh = TimedRotatingFileHandler(_temp_file_name, when='S')
        # fh.setLevel(logging.DEBUG)
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] : %(message)s')
        # add 'levelname_c' attribute to log resords
        orig_record_factory = logging.getLogRecordFactory()
        log_colors = {
            logging.DEBUG: "\033[1;34m",  # blue
            logging.INFO: "\033[1;32m",  # green
            logging.WARNING: "\033[1;35m",  # magenta
            logging.ERROR: "\033[1;31m",  # red
            logging.CRITICAL: "\033[1;41m",  # red reverted
        }

        def record_factory(*args, **kwargs):
            record = orig_record_factory(*args, **kwargs)
            record.levelname_colored = "{}{}{}".format(
                log_colors[record.levelno], record.levelname, "\033[0m")
            return record

        logging.setLogRecordFactory(record_factory)

        _file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s : %(message)s')
        _stream_formatter = logging.Formatter('%(asctime)s - %(levelname_colored)s - %(name)s : %(message)s')
        LogManager.file_handler.setFormatter(_file_formatter)
        LogManager.stream_handler.setFormatter(_stream_formatter)

        self._logger.addHandler(LogManager.file_handler)
        self._logger.addHandler(LogManager.stream_handler)
        # fh.setLevel(logging.DEBUG)
        self._logger.setLevel(logging.DEBUG)

    def _log_decorator(func):
        # @wraps(func)
        # def wrapper(self, msg, *args, **kw):
        def wrapper(self, msg, *args, stack_incr_cnt=0, **kwargs):
            # final_msg = self.join_caller_filename_lineno(msg, kw.get("stack_incr_cnt", 0))
            final_msg = self.join_caller_filename_lineno(msg, stack_incr_cnt)
            _func_name = func.__name__
            # if gv.is_dev_version:
            #     # and func.__name__ in ("debug", "error", "warning", "critical"):
            #     print(" - ".join(
            #         (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            #          _func_name.upper(), self._logger.name, final_msg)) % args)
            _log_tp_executor.submit(
                getattr(self._logger, _func_name), final_msg, *args, **kwargs)
            return
            # return func(self, msg, *args, **kw)
        return wrapper

    @staticmethod
    def join_caller_filename_lineno(msg, stack_incr_cnt=0):
        # caller = inspect.getframeinfo(inspect.stack()[2][0])
        caller = inspect.stack()[2+stack_incr_cnt]
        # return ''.join(('[', inspect.stack()[2].filename, ':', str(inspect.stack()[2].lineno), ']', msg))
        final_msg = ''.join(('[', os.path.basename(caller.filename), ':', str(caller.lineno), ']: ', msg))
        # if gr.is_dev_version:
        #     print(final_msg)
        return final_msg

    @_log_decorator
    def debug(self, msg, *args, **kwargs):
        pass
        # _log_tp_executor.submit(self.logger.debug, self.join_caller_filename_lineno(msg), *args, **kwargs)

    @_log_decorator
    def info(self, msg, *args, **kwargs):
        # _log_tp_executor.submit(self.logger.info, self.join_caller_filename_lineno(msg), *args, **kwargs)
        pass

    @_log_decorator
    def warning(self, msg, *args, **kwargs):
        # _log_tp_executor.submit(self.logger.warning, self.join_caller_filename_lineno(msg), *args, **kwargs)
        pass

    @_log_decorator
    def error(self, msg, *args, **kwargs):
        # _log_tp_executor.submit(self.logger.error, self.join_caller_filename_lineno(msg), *args, **kwargs)
        pass

    @_log_decorator
    def critical(self, msg, *args, **kwargs):
        # _log_tp_executor.submit(self.logger.critical, self.join_caller_filename_lineno(msg), *args, **kwargs)
        pass

    # def debug(self, msg, *args, **kwargs):
    #     _log_tp_executor.submit(self.logger.debug, self.join_caller_filename_lineno(msg), *args, **kwargs)
    #
    # def info(self, msg, *args, **kwargs):
    #     _log_tp_executor.submit(self.logger.info, self.join_caller_filename_lineno(msg), *args, **kwargs)
    #
    # def warning(self, msg, *args, **kwargs):
    #     _log_tp_executor.submit(self.logger.warning, self.join_caller_filename_lineno(msg), *args, **kwargs)
    #
    # def error(self, msg, *args, **kwargs):
    #     _log_tp_executor.submit(self.logger.error, self.join_caller_filename_lineno(msg), *args, **kwargs)
    #
    # def critical(self, msg, *args, **kwargs):
    #     _log_tp_executor.submit(self.logger.critical, self.join_caller_filename_lineno(msg), *args, **kwargs)

    def log_last_except(self):
        tp, value, traceback = sys.exc_info()
        tb_cont = self.convert_python_tb_to_str(tp, value, traceback)
        self.critical(f'on_traceback, type:{tp}, value:{value}, traceback:{tb_cont}', stack_incr_cnt=1)

    @staticmethod
    def convert_python_tb_to_str(t, v, tb, limit=None):
        tb_info = [str(t), str(v)]
        if tb is None:
            return
        n = 0
        while tb and (limit is None or n < limit):
            frame = tb.tb_frame
            # 上传服务器的文件名筛选
            # script_idx = frame.f_code.co_filename.find('script', 0)
            # if script_idx != -1:
            #	filename = frame.f_code.co_filename[script_idx:]

            max_trace_len = 1024
            try:
                _locals = dict(frame.f_locals)
                local_self = _locals.pop('self', None)
                if local_self:
                    local_str = "{'self': " + str(local_self) + ", " + str(_locals)[1:]
                else:
                    local_str = str(_locals)
            except:
                local_str = 'Cannot print locals'
            if len(local_str) > max_trace_len:
                local_str = local_str[:max_trace_len] + '...'

            line = [
                '  File "%s"' % frame.f_code.co_filename,
                'line %d' % tb.tb_lineno,
                'in %s' % frame.f_code.co_name,
                ]
            tb_info.append(', '.join(line))
            tb_info.append('    locals=' + local_str)
            tb = tb.tb_next
            n = n + 1
        return '\n'.join(tb_info)


if __name__ == '__main__':

    # sync logger
    # create logger
    logger = logging.getLogger('simple_example')

        # logger.setLevel(logging.DEBUG)
    fh = TimedRotatingFileHandler('test_log_mgr.log', when='D')
    # fh = TimedRotatingFileHandler(_temp_file_name, when='S')
    # fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] : %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.DEBUG)

    logger.debug('debug message ::%s', "dmmm?")
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')

    ##################################################
    # async logger 'application' code
    LogManager.set_log_tag('test_log')
    logger = LogManager.get_logger('test_log')
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')

    try:
        1/0
    except:
        # import sys
        # tp, value, traceback = sys.exc_info()
        #
        # tb_cont = convert_python_tb_to_str(tp, value, traceback)
        # logger.error(f'on_traceback, type:{tp}, value:{value}, traceback:{tb_cont}')
        # logging.exception("Deliberate divide by zero traceback")
        logger.log_last_except()
