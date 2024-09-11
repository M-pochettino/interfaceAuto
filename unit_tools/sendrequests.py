import json
import re

import requests
from requests import utils

from unit_tools.handle_data.yaml_handler import read_yaml, write_yaml
from unit_tools.log_util.recordlog import logs


class SendRequests:

    def __init__(self):
        pass    # 初始化方法，这里没有任何初始化操作

    @classmethod
    def _text_encode(cls, res_text):
        """
        处理接口返回值出现unicode编码时，如：\\u767b
        :param res_text: 接口返回的文本
        :return: 处理后的文本
        """
        match = re.search(r"\\u[0-9a-fA-F]{4}", res_text)   # 查找是否有Unicode编码的字符
        if match:
            result = res_text.encode().decode('unicode_escape')     # 解码Unicode字符
        else:
            result = res_text   # 如果没有Unicode字符，直接返回原文本
        return result

    def send_request(self, **kwargs):
        """
       发送HTTP请求并处理响应
       :param kwargs: HTTP请求的关键字参数
       :return: 响应对象
       """
        # 创建一个会话
        session = requests.Session()
        response = None     # 初始化响应对象
        try:
            response = session.request(**kwargs)    # 使用会话发送请求
            set_cookie = requests.utils.dict_from_cookiejar(response.cookies)   # 从响应中提取cookie
            if set_cookie:
                write_yaml({'Cookie': set_cookie})      # 如果有cookie，将其写入到YAML文件中
            res = self._text_encode(response.text)      # 处理响应文本中的Unicode编码
        except requests.exceptions.ConnectionError:
            logs.error('接口请求异常，可能是request的链接数过多或者速度过快导致程序报错！')  # 处理连接错误
        except requests.exceptions.RequestException as e:
            logs.error(f'请求异常，请检查系统或数据是否正常！原因：{e}')     # 处理其他请求异常

        return response     # 返回响应对象

    def execute_api_request(self, api_name, url, method, headers, case_name, cookies=None, files=None, **kwargs):
        """
        发起接口请求
        :param api_name: 接口名称
        :param url: 接口地址
        :param method: 请求方法
        :param headers: 请求头
        :param case_name: 测试用例名称
        :param cookies: cookie
        :param files: 文件上传
        :param kwargs: 未知数量的关键字参数
        :return: 响应对象
        """
        # 打印请求相关信息到日志
        logs.info(f'接口名称：{api_name}')
        logs.info(f'请求地址：{url}')
        logs.info(f'请求方式：{method.upper()}')
        logs.info(f'请求头：{headers}')
        logs.info(f'测试用例名：{case_name}')
        logs.info(f'cookies值：{cookies}')

        yaml_params_type = kwargs.keys()     # 获取所有关键字参数的键
        if kwargs and ('data' in yaml_params_type or 'json' in yaml_params_type or 'params' in yaml_params_type):
            params_type = list(kwargs.keys())[0]     # 获取参数类型
            logs.info(f'参数类型：{params_type}')
            params = json.dumps(list(kwargs.values())[0], ensure_ascii=False)   # 将参数转换为JSON格式
            logs.info(f'请求参数：{params}')
        # 发送请求并获取响应
        response = self.send_request(
            method=method,
            url=url,
            headers=headers,
            cookies=cookies,
            files=files,
            timeout=10,  # 设置超时时间为10秒
            verify=False,  # 不验证SSL证书
            **kwargs)  # 传递其他关键字参数
        return response  # 返回响应对象
