# @Time     : 2022/5/5 17:50
# @Author   : CN-LanBao
# -*- coding: utf-8 -*-
import os
import sys
import logging
import logging.handlers


class LogUtil(object):

    def __init__(self, file_name, logger_name=None):
        self._logger = logging.getLogger(logger_name)
        # logger 对象设置的日志级别决定了日志能够被传递到 handler 对象
        self._logger.setLevel(logging.DEBUG)

        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../log")

        # 创建保存目录
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        elif not os.path.isdir(log_dir):
            log_dir = os.path.dirname(os.path.abspath(__file__))

        # 日志文件路径
        log_file_path = os.path.join(log_dir, file_name)

        # 设置日志零点滚动
        rh = logging.handlers.TimedRotatingFileHandler(filename=log_file_path, when='MIDNIGHT')
        # 日志后缀
        rh.suffix = "%Y_%m_%d.log"

        # 控制台句柄，指定为标准输出
        sh = logging.StreamHandler(stream=sys.stdout)

        # handler 对象设置的日志级别决定了日志消息是否会被记录下来
        rh.setLevel(logging.DEBUG), sh.setLevel(logging.INFO)

        # 格式化日志输出
        formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
        rh.setFormatter(formatter), sh.setFormatter(formatter)

        self._logger.addHandler(rh), self._logger.addHandler(sh)

    def debug(self, msg):
        self._logger.debug(msg)

    def info(self, msg):
        self._logger.info(msg)

    def warning(self, msg):
        self._logger.warning(msg)

    def error(self, msg):
        self._logger.error(msg)

    def critical(self, msg):
        self._logger.critical(msg)
