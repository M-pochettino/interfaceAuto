import os
import sys

# 获取当前文件的父目录的父目录作为根路径
DIR_PATH = os.path.dirname(os.path.dirname(__file__))
# 将根路径添加到系统路径中，以便于导入自定义模块
sys.path.append(DIR_PATH)

# 定义文件路径的字典
FILE_PATH = {
    'extract': os.path.join(DIR_PATH, 'extract.yaml'),  # 定义一个 YAML 文件的路径
    'ini': os.path.join(DIR_PATH, 'configs', 'config.ini'),  # 定义一个 INI 文件的路径
    'log': os.path.join(DIR_PATH, 'logs')  # 定义一个日志文件夹的路径
}

# 设置是否发送钉钉群消息，默认为False则不会发送
is_dd_msg = False

# 钉钉机器人签名和地址
secret = 'SECb163daa45904540212492d8ad7bf7c3ce428fae5211c2e94b1f0926be0778191'
webhook = 'https://oapi.dingtalk.com/robot/send?access_token=' \
          'df849617e1f9593fd9c31f75ce4fdf2fea8fec39c7b714a65f20413444f5cea5'
