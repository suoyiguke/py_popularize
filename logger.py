import logging
import os
import re
import sys
#用于自动切换日志写入文件，保证单个日志文件不会太大
from logging.handlers import RotatingFileHandler

#按日期


log_src_test = './log/logname'
log_src_code = '/code/log/logname'

geshi = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'

class logger:

    def __init__(self, set_level="debug",
                 name=os.path.split(os.path.splitext(sys.argv[0])[0])[-1],
                 log_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "log"),
                 use_console=True):
        '''
            set_level： 设置日志的打印级别，默认为DEBUG
            name： 日志中将会打印的name，默认为运行程序的name
            log_path： 日志文件夹的路径，默认为logger.py同级目录中的log文件夹
            use_console： 是否在控制台打印，默认为True
        '''

        #  这里进行判断，如果logger.handlers列表为空，则添加，否则，直接去写日志
        # 解决重复打印日志问题
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            if set_level.lower() == "critical":
                self.logger.setLevel(logging.CRITICAL)
            elif set_level.lower() == "error":
                self.logger.setLevel(logging.ERROR)
            elif set_level.lower() == "warning":
                self.logger.setLevel(logging.WARNING)
            elif set_level.lower() == "info":
                self.logger.setLevel(logging.INFO)
            elif set_level.lower() == "debug":
                self.logger.setLevel(logging.DEBUG)
            else:
                self.logger.setLevel(logging.NOTSET)
            if not os.path.exists(log_path):
                os.makedirs(log_path)

            #按日期分割
            formatter = logging.Formatter("%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s","%Y-%m-%d %H:%M:%S")

            try:
                log_handler = logging.handlers.TimedRotatingFileHandler(filename=log_src_test, when="MIDNIGHT",
                                                                        interval=1, backupCount=30)
            except BaseException as err:
                log_handler = logging.handlers.TimedRotatingFileHandler(filename=log_src_code, when="MIDNIGHT",
                                                                        interval=1, backupCount=30)

            finally:
               print('请检查好日志文件路径环境！')


            #后缀
            log_handler.suffix = '%Y-%m-%d.log'
            log_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}")
            log_handler.setFormatter(formatter)

            self.logger.addHandler(log_handler)

            #输出在控制台
            if use_console:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(logging.Formatter(geshi))
                self.logger.addHandler(console_handler)

    def addHandler(self, hdlr):
        self.logger.addHandler(hdlr)

    def removeHandler(self, hdlr):
        self.logger.removeHandler(hdlr)

    def critical(self, msg, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)



    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def log(self, level, msg, *args, **kwargs):
        self.logger.log(level, msg, *args, **kwargs)

#测试
if __name__ == '__main__':
    logger = logger()
    while True:
      logger.info('============================================================================================================================================')
