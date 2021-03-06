import collections
import sys
import os

from core.mobilelog.LogManager import LogManager


class ReloadRecord(object):
    """
    根据上次启动、reload时记录的文件修改时间，进行增量func code reload
    仅支持散包py、pyc文件，暂时不支持zipfile
    """

    def __init__(self):
        super(ReloadRecord, self).__init__()
        self._count = 0
        self._record = collections.defaultdict(float)
        self.init_record()

    def init_record(self):
        for name, mtime in self.iter_modules():
            self._record[name] = mtime

    @staticmethod
    def iter_modules():
        for name, module in sys.modules.items():
            module_file = getattr(module, '__file__', None)
            if not module_file or not isinstance(module_file, (str, )) or not os.path.isfile(module_file):
                # module file not found
                continue
            if not module_file[-3:].lower() == '.py' and not module_file[-4:].lower() == '.pyc':
                # not py or pyc
                continue
            if module_file.lower().endswith('.pyc') and os.path.isfile(module_file[:-1]):
                module_file = module_file[:-1]
            mtime = os.path.getmtime(module_file)
            yield name, mtime

    def _generate_diff(self):
        diff_list = []
        for name, mtime in self.iter_modules():
            if self._record[name] < mtime:
                # have modify
                self._record[name] = mtime
                diff_list.append(name)
        return diff_list

    def generate_diff(self):
        self._count += 1
        return self._generate_diff()


_reload_record = ReloadRecord()


def init_reload_record():
    _reload_record.init_record()


def set_base_to_now():
    _reload_record.generate_diff()


def reload_script():
    """
    增量进行funccode reload
    :return:
    """
    diff_list = _reload_record.generate_diff()
    if not diff_list:
        LogManager.get_logger().info('nothing to reload')
        return False
    from core.tool import reload_impl
    for mod_name in diff_list:
        reload_impl.reload_module(mod_name)
    return True
