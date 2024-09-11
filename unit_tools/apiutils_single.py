# -*- coding:utf-8 -*-

import json
import re
import traceback

import allure
import jsonpath

from unit_tools.assertion_utils import Assertions
from unit_tools.debugtalk import DebugTalk
from unit_tools.handle_data.configParse import ConfigParse
from unit_tools.handle_data.yaml_handler import read_yaml, write_yaml
from unit_tools.sendrequests import SendRequests
from unit_tools.log_util.recordlog import logs


class RequestsBase:

    def __init__(self):
        self.conf = ConfigParse()  # 初始化配置解析实例
        self.send_request = SendRequests()  # 初始化请求发送实例
        self.asserts = Assertions()  # 初始化断言实例

    @classmethod
    def parse_and_replace_variables(cls, yml_data):
        """
        解析并替换YAML数据中的变量引用，如：${get_extract_data(goodsId,1)}
        :param yml_data: 解析的YAML数据
        :return: 返回的是dict类型
        """
        # 如果yml_data是字符串则直接使用，否则将其转换为JSON字符串
        yml_data_str = yml_data if isinstance(yml_data, str) else json.dumps(yml_data, ensure_ascii=False)
        # 循环处理字符串中的所有变量引用
        for _ in range(yml_data_str.count('${')):
            # 检查是否存在变量引用的标记
            if '${' in yml_data_str and '}' in yml_data_str:
                start_index = yml_data_str.index('$')  # 获取变量引用的起始位置
                end_index = yml_data_str.index('}', start_index)  # 获取变量引用的结束位置
                variable_data = yml_data_str[start_index:end_index + 1]  # 提取变量引用部分

                # 使用正则表达式提取函数名和参数
                match = re.match(r'\$\{(\w+)\((.*?)\)\}', variable_data)
                if match:
                    func_name, func_params = match.groups()     # 获取函数名和参数
                    func_params = func_params.split(',') if func_params else []  # 分割参数字符串为列表

                    # 使用面向对象反射getattr调用函数
                    extract_data = getattr(DebugTalk(), func_name)(*func_params)

                    # 使用正则表达式替换原始字符中的变量引用为调用后的结果
                    yml_data_str = re.sub(re.escape(variable_data), str(extract_data), yml_data_str)

        # 还原数据，将其转换为字典类型
        try:
            data = json.loads(yml_data_str)     # 尝试将字符串转换为JSON对象
        except json.JSONDecodeError:
            data = yml_data_str     # 尝试将字符串转换为JSON对象
        # 返回解析后的数据
        return data

    @classmethod
    def allure_attach_dict_result(cls, result):
        """
        处理结果是字典类型，就将其转换成字符串类型，并做格式化处理，否则直接返回
        :param result: 传入的结果，可以是任何类型
        :return: 如果是字典类型，返回格式化后的字符串，否则返回原结果
        """
        # 检查传入的结果是否为字典类型
        if isinstance(result, dict):
            # 将字典转换为格式化后的JSON字符串，不使用ASCII编码，缩进为4个空格
            allure_response = json.dumps(result, ensure_ascii=False, indent=4)
        else:
            # 如果不是字典类型，直接返回原结果
            allure_response = result
        # 返回处理后的结果
        return allure_response

    def execute_test_cases(self, base_info, testcase):
        """
        规范yaml接口信息，执行接口、提取结果以及断言操作
        :param base_info: （dict）yaml里面接口基本信息
        :param testcase: （dict）yaml里面接口测试用例信息
        :return:
        """
        try:
            # 从配置文件中获取主机地址
            conf_host = self.conf.get_conf('Host', 'host')
            # 构建完整的接口URL
            url = conf_host + base_info['url']
            # 获取接口名称
            api_name = base_info['api_name']
            # 获取请求方法（GET, POST等）
            method = base_info['method']
            # 获取请求头信息，可能为空
            headers = base_info.get('headers', None)
            if headers is not None:
                # 如果headers是字符串类型，解析其中的变量
                headers = eval(self.parse_and_replace_variables(headers)) if isinstance(headers, str) else headers
            # 获取cookies信息，可能为空
            cookies = base_info.get('cookies', None)
            if cookies is not None:
                # 如果cookies是字符串类型，解析其中的变量
                cookies = eval(self.parse_and_replace_variables(cookies)) if isinstance(cookies, str) else cookies

            # 从testcase中提取测试用例名称并移除该键值对
            case_name = testcase.pop('case_name')

            # 解析并替换测试用例中的断言结果
            val_result = self.parse_and_replace_variables(testcase.get('validation'))
            testcase['validation'] = val_result
            # 移除断言结果键值对并保存到变量中
            validation = testcase.pop('validation')

            # 处理接口返回值提取部分，可能为空
            extract, extract_list = testcase.pop('extract', None), testcase.pop('extract_list', None)
            # 初始化参数类型和请求参数变量
            param_type, request_params = None, None
            # 处理参数类型和请求参数
            for param_type, param_value in testcase.items():
                if param_type in ['params', 'data', 'json']:
                    # 解析并替换参数中的变量
                    request_params = self.parse_and_replace_variables(param_value)
                    testcase[param_type] = request_params

            # 处理文件上传，可能为空
            files = testcase.pop('files', None)
            if files:
                for fk, fv in files.items():
                    files = {fk: open(fv, mode='rb')}
            # 发送接口请求并获取响应
            response = self.send_request.execute_api_request(
                api_name=api_name, url=url, method=method,
                headers=headers,
                case_name=case_name,
                cookies=cookies,
                files=files,
                **testcase)
            # 获取响应状态码和响应内容
            status_code, response_text = response.status_code, response.text
            # 记录日志，显示接口实际返回结果
            logs.info(f'接口实际返回结果：{response_text}')

            # 在allure报告Test body显示内容
            allure_info = {
                '接口地址': url,
                '接口名称': api_name,
                '请求方式': method,
                '请求头': self.allure_attach_dict_result(headers if headers else "无需请求头"),
                'Cookie': self.allure_attach_dict_result(cookies if cookies else "无需Cookie"),
                '测试用例名称': case_name,
                '参数类型': param_type if param_type else "",
                '请求参数': self.allure_attach_dict_result(request_params if request_params else "无需入参"),
                '接口实际响应信息': self.allure_attach_dict_result(response.json())

            }
            # 将allure_info中的信息附加到allure报告中
            for title, content in allure_info.items():
                allure.attach(content, title, attachment_type=allure.attachment_type.JSON)

            # 处理接口返回值提取
            if extract is not None:
                self.extract_data(extract, response_text)
            if extract_list is not None:
                self.extract_data_list(extract_list, response_text)

            # 处理接口断言
            self.asserts.assert_result(validation, response.json(), status_code)

        except Exception as e:
            # 记录日志，显示异常信息
            logs.error(f'出现未知异常，-- {str(traceback.format_exc())}')
            # 抛出异常
            raise e

    @classmethod
    def extract_data(cls, testcase_extract, response_text):
        """
        提取单个参数，提取接口的返回参数，支持正则表达式提取和json提取器
        :param testcase_extract: （dict）yaml文件中的extract值，例如：{'token': '$.token'}
        :param response_text: （str）接口的实际返回值
        :return:
        """
        extract_data = None
        try:
            # 遍历要提取的键值对
            for key, value in testcase_extract.items():
                # 判断是否为正则表达式
                if any(pat in value for pat in ['(.*?)', '(.+?)', r'(\d+)', r'(\d*)']):
                    # 使用正则表达式进行提取
                    ext_list = re.search(value, response_text)
                    # 根据正则表达式结果提取数据
                    extract_data = {key: int(ext_list.group(1)) if r'(\d+)' in value else ext_list.group(1)}
                # 判断是否为JSON提取器表达式
                elif "$" in value:
                    # 使用jsonpath提取数据
                    extract_json = jsonpath.jsonpath(json.loads(response_text), value)[0]
                    # 如果提取到数据，则存储在extract_data中，否则存储错误信息
                    extract_data = {key: extract_json} if extract_json else {key: "未提取到数据，请检查接口返回信息或表达式！"}
                # 如果有提取到数据，写入yaml文件
                if extract_data:
                    write_yaml(extract_data)

        except re.error:
            # 捕获正则表达式解析错误，记录日志
            logs.error('正则表达式解析错误，请检查yaml文件extract表达式是否正确！')
        except json.JSONDecodeError:
            # 捕获JSON解析错误，记录日志
            logs.error('JSON解析错误，请检查yaml文件extract表达式是否正确！')

    @classmethod
    def extract_data_list(cls, testcase_extract_list, response_text):
        """
        提取多个参数，提取接口的返回参数，支持正则表达式提取和json提取器
        :param testcase_extract_list: （dict）yaml文件中的extract_list值，例如：{'token': '$.token'}
        :param response_text: （str）接口的实际返回值
        :return:
        """
        extract_data = None
        try:
            # 遍历要提取的键值对
            for key, value in testcase_extract_list.items():
                # 判断是否为正则表达式
                if any(pat in value for pat in ['(.*?)', '(.+?)', r'(\d+)', r'(\d*)']):
                    # 使用正则表达式进行提取
                    ext_list = re.findall(value, response_text, re.S)
                    # 如果提取到数据，则存储在extract_data中
                    if ext_list:
                        extract_data = {key: ext_list}
                # 判断是否为JSON提取器表达式
                elif "$" in value:
                    # 使用jsonpath提取数据
                    extract_json = jsonpath.jsonpath(json.loads(response_text), value)
                    # 如果提取到数据，则存储在extract_data中，否则存储错误信息
                    if extract_json:
                        extract_data = {key: extract_json}
                    else:
                        extract_data = {key: "未提取到数据，请检查接口返回信息或表达式！"}
                # 如果有提取到数据，写入yaml文件
                if extract_data:
                    write_yaml(extract_data)

        except re.error:
            # 捕获正则表达式解析错误，记录日志
            logs.error('正则表达式解析错误，请检查yaml文件extract表达式是否正确！')
        except json.JSONDecodeError:
            # 捕获JSON解析错误，记录日志
            logs.error('JSON解析错误，请检查yaml文件extract表达式是否正确！')
