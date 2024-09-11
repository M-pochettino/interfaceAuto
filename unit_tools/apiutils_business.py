# -*- coding:utf-8 -*-

import json
import os
import re
import traceback

import allure
import jsonpath
import requests

from unit_tools.assertion_utils import Assertions
from unit_tools.debugtalk import DebugTalk
from unit_tools.handle_data.configParse import ConfigParse
from unit_tools.handle_data.yaml_handler import write_yaml
from unit_tools.sendrequests import SendRequests
from unit_tools.log_util.recordlog import logs


class RequestsBase:

    def __init__(self):
        # 初始化配置解析、发送请求和断言功能
        self.conf = ConfigParse()  # 配置解析器实例
        self.send_request = SendRequests()  # 发送请求实例
        self.asserts = Assertions()  # 断言实例

    @classmethod
    def parse_and_replace_variables(cls, yml_data):
        """
        解析并替换YAML数据中的变量引用，如：${get_extract_data(goodsId,1)}
        :param yml_data: 解析的YAML数据，可以是字典或字符串
        :return: 解析后的字典数据
        """
        # 将输入数据转换为字符串形式以便处理
        yml_data_str = yml_data if isinstance(yml_data, str) else json.dumps(yml_data, ensure_ascii=False)
        # 循环处理所有的变量引用，直到没有变量引用为止
        for _ in range(yml_data_str.count('${')):
            if '${' in yml_data_str and '}' in yml_data_str:
                # 找到变量引用的起始和结束位置
                start_index = yml_data_str.index('$')
                end_index = yml_data_str.index('}', start_index)
                variable_data = yml_data_str[start_index:end_index + 1]
                # 使用正则表达式提取函数名和参数
                match = re.match(r'\$\{(\w+)\((.*?)\)\}', variable_data)
                if match:
                    func_name, func_params = match.groups()
                    func_params = func_params.split(',') if func_params else []
                    # 使用面向对象反射getattr调用函数
                    extract_data = getattr(DebugTalk(), func_name)(*func_params)
                    # 替换原始字符串中的变量引用为函数调用后的结果
                    yml_data_str = re.sub(re.escape(variable_data), str(extract_data), yml_data_str)

        # 尝试将处理后的字符串转换回字典形式
        try:
            data = json.loads(yml_data_str)
        except json.JSONDecodeError:
            # 如果解析失败，则返回原始字符串形式的数据
            data = yml_data_str

        return data

    @classmethod
    def allure_attach_dict_result(cls, result):
        """
        将字典类型的结果转换为格式化的JSON字符串，其他类型直接返回
        :param result: 需要处理的结果数据
        :return: 格式化的JSON字符串或原始数据
        """
        if isinstance(result, (dict, list)):
            # 如果结果是字典或列表类型，则转换为格式化的JSON字符串
            allure_response = json.dumps(result, ensure_ascii=False, indent=4)
        else:
            # 如果结果不是字典或列表类型，则直接返回原始数据
            allure_response = result
        return allure_response

    def execute_test_cases(self, api_info):
        """
        规范yaml接口信息，执行接口、提取结果以及断言操作
        :param api_info: （dict）yaml里面接口信息
        :return:
        """
        try:
            # 获取配置文件中的主机地址
            conf_host = self.conf.get_conf('Host', 'host')
            # 构建请求的完整URL
            url = conf_host + api_info['baseInfo']['url']
            # 获取API名称
            api_name = api_info['baseInfo']['api_name']
            # 获取请求方法（GET, POST等）
            method = api_info['baseInfo']['method']
            # 获取请求头信息
            headers = api_info['baseInfo'].get('headers', None)
            if headers is not None:
                # 如果headers是字符串形式，解析其中的变量，否则直接使用
                headers = eval(self.parse_and_replace_variables(headers)) if isinstance(headers, str) else headers
            # 获取cookies信息
            cookies = api_info['baseInfo'].get('cookies', None)
            if cookies is not None:
                # 如果cookies是字符串形式，解析其中的变量，否则直接使用
                cookies = eval(self.parse_and_replace_variables(cookies)) if isinstance(cookies, str) else cookies

            # 处理testCase下面的每个测试用例
            for testcase in api_info['testCase']:
                # 获取测试用例名称并从testcase中移除
                case_name = testcase.pop('case_name')

                # 通过变量引用处理断言结果
                val_result = self.parse_and_replace_variables(testcase.get('validation'))
                testcase['validation'] = val_result

                validation = testcase.pop('validation')

                # 处理接口返回值提取部分
                extract, extract_list = testcase.pop('extract', None), testcase.pop('extract_list', None)

                param_type, request_params = None, None
                # 处理参数类型和请求参数
                for param_type, param_value in testcase.items():
                    if param_type in ['params', 'data', 'json']:
                        request_params = self.parse_and_replace_variables(param_value)
                        testcase[param_type] = request_params

                # 处理文件上传
                files = testcase.pop('files', None)
                if files:
                    # 假设从 testcase 中获取文件对象 f
                    f = testcase.get('files')  # 需要根据实际情况修改获取文件对象的方式
                    files = {
                        'file': ('import.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    }
                # 执行API请求
                response = self.send_request.execute_api_request(
                    api_name=api_name, url=url, method=method,
                    headers=headers,
                    case_name=case_name,
                    cookies=cookies,
                    files=files,
                    **testcase)
                # 获取响应状态码和响应文本
                status_code, response_text = response.status_code, response.text
                # 记录日志，输出接口实际返回结果
                logs.info(f'接口实际返回结果：{response_text}')

                # 处理文件流下载
                content_type = response.headers.get('Content-Type', '')
                if 'application/octet-stream' in content_type or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
                    # 提取文件名
                    content_disposition = response.headers.get('Content-Disposition', '')
                    filename = None
                    if content_disposition:
                        # 从 Content-Disposition 中提取文件名
                        filename_start = content_disposition.find('filename*=utf-8\'\'')
                        if filename_start != -1:
                            filename = content_disposition[filename_start + len('filename*=utf-8\'\''):]

                    if filename:
                        # 去除文件名中的URL编码转义字符
                        filename = requests.utils.unquote(filename)
                        # 移除非法字符，例如冒号
                        filename = re.sub(r'[\\/:*?"<>|]', '', filename)
                        # 确定保存路径
                        save_path = './testcase/report'
                        os.makedirs(save_path, exist_ok=True)  # 确保路径存在
                        # 完整的文件保存路径
                        file_path = os.path.join(save_path, filename)
                        # 保存文件流为本地文件
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        print(f'文件保存为 {file_path}')

                try:
                    response_data = response.json()
                except json.JSONDecodeError:
                    response_data = {'response_text': response_text}

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
                    '接口实际响应信息': self.allure_attach_dict_result(response_data)

                }
                # 遍历allure_info字典，将每个title和content附加到Allure报告中
                for title, content in allure_info.items():
                    allure.attach(content, title, attachment_type=allure.attachment_type.JSON)

                # 处理接口返回值提取
                if extract is not None:
                    # 如果extract不为空，调用extract_data方法从响应文本中提取数据
                    self.extract_data(extract, response_text)
                if extract_list is not None:
                    # 如果extract_list不为空，调用extract_data_list方法从响应文本中提取数据
                    self.extract_data_list(extract_list, response_text)

                # 处理接口断言
                if validation is not None:
                    # 如果validation不为空，调用assert_result方法进行断言，比较实际结果和预期结果
                    self.asserts.assert_result(validation, response_data, status_code)

        except Exception as e:
            # 捕获所有异常，记录错误日志，并将异常抛出
            logs.error(f'出现未知异常，-- {str(traceback.format_exc())}')
            raise e

    @classmethod
    def extract_data(cls, testcase_extract, response_text):
        """
        提取单个参数，提取接口的返回参数，支持正则表达式提取和json提取器
        :param testcase_extract: （dict）yaml文件中的extract值，例如：{'token': '$.token'}
        :param response_text: （str）接口的实际返回值
        :return:
        """
        extract_data = None     # 初始化提取数据变量
        try:
            # 遍历提取规则字典
            for key, value in testcase_extract.items():
                # 如果提取规则包含正则表达式模式
                if any(pat in value for pat in ['(.*?)', '(.+?)', r'(\d+)', r'(\d*)']):
                    # 使用正则表达式进行搜索匹配
                    ext_list = re.search(value, response_text)
                    # 根据匹配结果提取数据，整数型和字符串型区分处理
                    extract_data = {key: int(ext_list.group(1)) if r'(\d+)' in value else ext_list.group(1)}
                # 如果提取规则包含JSON路径
                elif "$" in value:
                    # 使用jsonpath提取数据
                    extract_json = jsonpath.jsonpath(json.loads(response_text), value)[0]
                    # 将提取结果写入字典
                    extract_data = {key: extract_json} if extract_json else {
                        key: "未提取到数据，请检查接口返回信息或表达式！"}
                # 如果提取到数据，写入yaml文件
                if extract_data:
                    write_yaml(extract_data)
        # 捕获正则表达式错误
        except re.error:
            logs.error('正则表达式解析错误，请检查yaml文件extract表达式是否正确！')
        # 捕获JSON解析错误
        except json.JSONDecodeError:
            logs.error('JSON解析错误，请检查yaml文件extract表达式是否正确！')

    @classmethod
    def extract_data_list(cls, testcase_extract_list, response_text):
        """
        提取多个参数，提取接口的返回参数，支持正则表达式提取和json提取器
        :param testcase_extract_list: （dict）yaml文件中的extract_list值，例如：{'token': '$.token'}
        :param response_text: （str）接口的实际返回值
        :return:
        """
        extract_data = None     # 初始化提取数据变量
        try:
            # 遍历要提取的键值对
            for key, value in testcase_extract_list.items():
                # 如果提取规则包含正则表达式模式
                if any(pat in value for pat in ['(.*?)', '(.+?)', r'(\d+)', r'(\d*)']):
                    # 使用正则表达式进行全局搜索匹配
                    ext_list = re.findall(value, response_text, re.S)
                    # 如果有匹配结果，将其写入字典
                    if ext_list:
                        extract_data = {key: ext_list}
                # 如果提取规则包含JSON路径
                elif "$" in value:
                    # 使用jsonpath提取数据
                    extract_json = jsonpath.jsonpath(json.loads(response_text), value)
                    # 将提取结果写入字典
                    if extract_json:
                        extract_data = {key: extract_json}
                    else:
                        extract_data = {key: "未提取到数据，请检查接口返回信息或表达式！"}
                # 如果提取到数据，写入yaml文件
                if extract_data:
                    write_yaml(extract_data)
        # 捕获正则表达式错误
        except re.error:
            logs.error('正则表达式解析错误，请检查yaml文件extract表达式是否正确！')
        # 捕获JSON解析错误
        except json.JSONDecodeError:
            logs.error('JSON解析错误，请检查yaml文件extract表达式是否正确！')
