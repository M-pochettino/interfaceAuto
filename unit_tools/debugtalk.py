import random
import re
import time

import faker
from faker.proxy import Faker

from unit_tools.handle_data.yaml_handler import get_extract_yaml


class DebugTalk:
    fake = Faker('zh_CN')   # 初始化Faker对象，设置区域为中国

    def get_extract_data(self, node_name, out_format=None):
        """
        获取extract.yaml数据，首先判断out_format是否为数字类型，如果不是就获取下一个节点的value
        :param node_name: extract.yaml文件中的key
        :param out_format: str类型，0：随机去读取；-1：读取全部数据，返回字符串格式；-2：读取全部，返回是列表格式
                            其他值的就按顺序读取
        :return: 返回处理后的数据
        """
        data = get_extract_yaml(node_name)  # 获取extract.yaml文件中的数据，返回列表
        if out_format is not None and bool(re.compile(r'^[+-]?\d+$').match(str(out_format))):
            # 判断out_format是否为数字类型
            out_format = int(out_format)    # 将out_format转换为整数类型
            data_value = {
                out_format: self.seq_read(data, out_format),    # 按顺序读取数据
                0: random.choice(data),     # 随机读取一个数据
                -1: ','.join(data),     # 读取全部数据，并用逗号连接返回字符串格式
                -2: ','.join(data).split(',')     # 读取全部数据，并用逗号连接返回列表格式
            }
            data = data_value[out_format]   # 根据out_format的值返回对应的数据
        else:
            data = get_extract_yaml(node_name, out_format)  # 如果out_format不为数字类型，则直接获取下一个节点的value
        return data  # 返回处理后的数据

    @classmethod
    def seq_read(cls, data, out_format):
        """
        获取extract.yaml，第二个参数不为0，-1，-2的情况下
        :param data: 从extract.yaml文件中获取的数据
        :param out_format: 整数类型，按顺序读取数据
        :return: 返回按顺序读取的数据
        """
        if out_format not in [0, -1, -2]:   # 判断out_format是否为0，-1，-2
            return data[out_format - 1]     # 返回按顺序读取的数据，索引值为out_format-1
        else:
            return None     # 如果out_format为0，-1，-2，则返回None

    @classmethod
    def params_md5(cls):
        """这是一个占位方法，目前没有实现具体功能"""
        pass

    @classmethod
    def get_now_time(cls):
        """
        获取当前时间戳
        :return: 返回当前时间的时间戳
        """
        return time.time()  # 返回当前时间的时间戳（秒）

    @classmethod
    def get_headers(cls, params_type):
        """
        获取请求头
        :param params_type: 参数类型，如“data”或“json”
        :return: 返回对应的请求头
        """
        headers_mapping = {
            'data': {'Content-Type': 'application/x-www-formurlencoded;charset=UTF-8'},
            'json': {'Content-Type': 'application/json;charset=UTF-8'}
        }
        header = headers_mapping.get(params_type)   # 根据参数类型获取对应的请求头
        if header is None:  # 如果请求头不存在，抛出异常
            raise ValueError('不支持其他类型的请求头设置！')
        return header   # 返回请求头

    @classmethod
    def get_headers_auth(cls, params_type):
        """
        获取带有授权信息的请求头
        :param params_type: 参数类型，如“data”或“json”
        :return: 返回带有授权信息的请求头
        """
        auth1 = get_extract_yaml("access_token", None)  # 从extract.yaml文件中获取access_token
        auth2 = 'Bearer ' + auth1   # 拼接成完整的授权信息
        headers_mapping = {
            'data': {'Content-Type': 'application/x-www-formurlencoded;charset=UTF-8'},
            'json': {
                'Content-Type': 'application/json;charset=UTF-8',
                'Authorization': auth2  # 添加授权信息到请求头
            }
        }
        header = headers_mapping.get(params_type)   # 根据参数类型获取对应的请求头
        if header is None:  # 如果请求头不存在，抛出异常
            raise ValueError('不支持其他类型的请求头设置！')
        return header   # 返回请求头

    @classmethod
    def get_random_string(cls, params):
        """
        根据传入的参数生成随机值
        :param params: 信息字段
        :return: 对应的随机值
        """
        if params == "username":
            return cls.fake.user_name()  # 生成随机用户名
        elif params == "phone":
            return cls.fake.phone_number()  # 生成随机电话号码
        elif params == "nickname":
            return cls.fake.name()  # 生成随机昵称
        elif params == "name":
            return cls.fake.name_female()  # 生成随机女性名字
        elif params == "email":
            return cls.fake.email()  # 生成随机电子邮件
        else:
            return "unknown"  # 如果传入的参数不在上述范围内，返回"unknown"

    @classmethod
    def get_extract_info(cls, params):
        """
        获取extract.yaml文件中的信息
        :param params: extract.yaml文件中的key
        :return: 返回对应的值
        """
        auth1 = get_extract_yaml(params, None)  # 获取extract.yaml文件中的信息
        return auth1  # 返回信息
