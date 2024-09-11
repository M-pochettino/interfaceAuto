# -*- coding:utf-8 -*-
import logging
import os
import time
from logging.handlers import RotatingFileHandler  # 按文件大小滚动备份

import colorlog

from configs.setting import FILE_PATH
# 获取日志文件存储路径
logs_path = FILE_PATH['log']
if not os.path.exists(logs_path):
    os.mkdir(logs_path)
# 日志文件名按日期命名
logfile_name = logs_path + r'\test.{}.log'.format(time.strftime('%Y%m%d'))


class HandleLogs:

    @classmethod
    def setting_log_color(cls):
        """
        设置彩色日志输出格式
        :return: 彩色日志输出格式对象
        """
        log_color_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'ERROR': 'red',
            'WARNING': 'yellow',
            'CRITICAL': 'red'
        }
        formatter = colorlog.ColoredFormatter(
            '%(log_color)s %(levelname)s - %(asctime)s - %(filename)s:%(lineno)d -[%(module)s:%(funcName)s] - '
            '%(message)s',
            log_colors=log_color_config)

        return formatter

    @classmethod
    def output_logs(cls):
        """
        配置日志输出到控制台和文件
        :return: 日志记录器对象
        """
        logger = logging.getLogger(__name__)
        steam_format = cls.setting_log_color()      # 获取彩色日志输出格式
        # 防止重复打印日志
        if not logger.handlers:
            logger.setLevel(logging.DEBUG)      # 设置日志记录器的日志级别为DEBUG
            log_format = logging.Formatter(
                '%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d -[%(module)s:%(funcName)s] - %(message)s')
            # 把日志信息输出到控制台
            sh = logging.StreamHandler()  # 创建控制台日志处理器
            sh.setLevel(logging.DEBUG)  # 设置控制台日志处理器的日志级别为DEBUG
            sh.setFormatter(steam_format)  # 设置控制台日志处理器的格式
            logger.addHandler(sh)  # 将控制台日志处理器添加到日志记录器中

            # 把日志输出到文件里面
            fh = RotatingFileHandler(filename=logfile_name, mode='a', maxBytes=5242880, backupCount=7, encoding='utf-8')
            fh.setLevel(logging.DEBUG)  # 设置文件日志处理器的日志级别为DEBUG
            fh.setFormatter(log_format)  # 设置文件日志处理器的格式
            logger.addHandler(fh)  # 将文件日志处理器添加到日志记录器中

        return logger  # 返回配置好的日志记录器对象

# 使用HandleLogs类配置日志记录器并命名为logs
handle = HandleLogs()
logs = handle.output_logs()
