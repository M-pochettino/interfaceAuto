import configparser

from configs.setting import FILE_PATH
from unit_tools.log_util.recordlog import logs


class ConfigParse:
    """
    解析.ini后缀的配置文件，并提供获取配置参数的方法。
    """

    def __init__(self, file_path=FILE_PATH['ini']):
        """
        初始化 ConfigParse 类。
        :param file_path: 配置文件路径，默认为 FILE_PATH['ini']
        """
        self.file_path = file_path  # 设置配置文件路径
        self.config = configparser.ConfigParser()  # 创建 ConfigParser 对象
        self.read_config()  # 调用读取配置文件的方法

    def read_config(self):
        """
        读取配置文件内容。
        """
        self.config.read(self.file_path, encoding='utf-8')  # 使用 utf-8 编码读取配置文件

    def get_value(self, section, option):
        """
        获取配置文件中指定 section 和 option 的值。
        :param section: 配置文件中的 section 名称
        :param option: 配置文件中的 option 名称
        :return: 对应 option 的值，如果获取失败则记录错误并返回 None
        """
        try:
            return self.config.get(section, option)  # 获取指定 section 和 option 的值
        except Exception as e:
            logs.error(f'解析配置文件出现异常，原因：{e}')  # 记录日志并输出异常信息
            return None

    def get_conf(self, conf, option):
        """
        获取配置文件中指定 section 和 option 的值的简化方法。
        :param section: 配置文件中的 section 名称
        :param option: 配置文件中的 option 名称
        :return: 对应 option 的值，如果获取失败则返回 None
        """
        return self.get_value(conf, option)

    def get_mysql_conf(self, option):
        """
        获取MySQL数据库的配置参数值。
        :param option: MySQL配置参数的名称
        :return: 对应 option 的值，如果获取失败则返回 None
        """
        return self.get_value('MySQL', option)

    def get_redis_conf(self, option):
        """
        获取Redis数据库的配置参数值。
        :param option: Redis配置参数的名称
        :return: 对应 option 的值，如果获取失败则返回 None
        """
        return self.get_value('Redis', option)
