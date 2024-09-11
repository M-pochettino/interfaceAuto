# -*- coding:utf-8 -*-
import operator
from typing import Callable, Any

import allure
import jsonpath

from unit_tools.db_connector.connectMysql import ConnectMysql
from unit_tools.exception_utils.exceptions import AssertTypeError
from unit_tools.log_util.recordlog import logs


class Assertions:
    """
    接口断言模式封装
    1） 状态码断言
    2） 包含模式断言
    3） 相等断言
    4） 不相等断言
    5） 数据库断言
    """

    @classmethod
    def status_code_assert(cls, expected_result, status_code):
        """
        接口的响应状态码断言
        :param expected_result: （int）yaml文件code模式中的预期状态码
        :param status_code: （int）接口实际返回的状态码
        :return:   返回断言失败的计数
        """
        # 断言状态标识，0 表示成功，其他表示失败
        failure_count = 0   # 初始化断言失败计数器为0
        if not isinstance(expected_result, int):    # 检查expected_result是否为整数类型
            expected_result = int(expected_result)  # 如果不是，则将其转换为整数类型

        if expected_result == status_code:  # 判断预期状态码是否与实际返回状态码相同
            logs.info(f'状态码断言成功：接口实际返回状态码 {status_code} == {expected_result}')
            # 记录断言成功的日志信息
            allure.attach(f"预期结果：{str(expected_result)}\n实际结果：{str(status_code)}", "状态码断言结果：成功",
                          attachment_type=allure.attachment_type.TEXT)
            # 使用allure附加断言成功的详细信息
        else:
            logs.error(f'状态码断言失败：接口实际返回状态码 {status_code} != {expected_result}')
            # 记录断言失败的日志信息
            failure_count += 1  # 断言失败计数器加1
            allure.attach(f"预期结果：{str(expected_result)}\n实际结果：{str(status_code)}", "状态码断言结果：失败",
                          attachment_type=allure.attachment_type.TEXT)
            # 使用allure附加断言失败的详细信息
        return failure_count    # 返回断言失败的计数

    @classmethod
    def contain_assert(cls, expected_result, response):
        """
        字符串包含模式，断言预期结果字符串是否包含在接口的实际响应返回信息中
        :param expected_result: （dict）yaml文件里面contain模式的数据
        :param response: （dict）接口的实际响应信息
        :return:   返回断言失败的计数
        """
        # 断言状态标识，0 表示成功，其他表示失败
        failure_count = 0   # 初始化断言失败计数器为0
        for assert_key, assert_value in expected_result.items():    # 遍历预期结果字典中的每个键值对
            response_list = jsonpath.jsonpath(response, f'$..{assert_key}') # 使用jsonpath提取响应中所有匹配键的值列表
            if response_list and isinstance(response_list[0], str): # 检查提取的结果是否存在且第一个元素是否为字符串
                response_str = ''.join(response_list)   # 将提取的字符串列表连接成一个完整的字符串

                success_message = f"包含模式断言成功：预期结果【{assert_value}】存在于实际结果【{response_str}】中"
                failure_message = f"包含模式断言失败：预期结果【{assert_value}】未在实际结果【{response_str}】中找到"
                if assert_value in response_str:    # 检查预期结果值是否包含在实际结果字符串中
                    logs.info(success_message)  # 记录断言成功的日志信息
                else:
                    failure_count = failure_count + 1   # 断言失败计数器加1
                    logs.error(failure_message) # 记录断言失败的日志信息
        return failure_count    # 返回断言失败的计数

    @classmethod
    def equal_assert(cls, expected_result, response):
        """
        相等断言，根据yaml里面的validation关键词下面的eq模式数据去跟接口实际响应信息对比
        :param expected_result: （dict）yaml里面的eq值
        :param response: （dict）接口实际响应结果
        :return:   返回断言失败的计数
        """
        failure_count = 0   # 初始化断言失败计数器为0
        if isinstance(response, dict) and isinstance(expected_result, dict):    # 检查响应和预期结果是否都是字典类型
            # 找出实际结果与预期结果共同的key值
            common_key = list(expected_result.keys() & response.keys()) # 获取预期结果和实际响应中共同的键列表
            if common_key:   # 如果存在共同的键
                common_key = common_key[0]  # 取出第一个共同的键
                # 根据相同的key值去实际结果中获取，并重新生成一个实际结果的字典
                new_actual_result = {common_key: response[common_key]}  # 生成一个新的字典，包含实际响应中对应键的值
                eq_assert = operator.eq(new_actual_result, expected_result) # 判断新生成的实际结果字典是否等于预期结果字典
                if eq_assert:   # 如果相等
                    logs.info(f"相等断言成功：接口实际结果 {new_actual_result} == 预期结果：{expected_result}")
                    # 记录断言成功的日志信息
                    allure.attach(f"预期结果：{str(expected_result)}\n实际结果：{str(new_actual_result)}", "相等断言结果：成功",
                                  attachment_type=allure.attachment_type.JSON)
                    # 使用allure附加断言成功的详细信息
                else:
                    failure_count += 1
                    logs.error(f"相等断言失败：接口实际结果 {new_actual_result} != 预期结果：{expected_result}")
                    # 记录断言失败的日志信息
                    allure.attach(f"预期结果：{str(expected_result)}\n实际结果：{str(new_actual_result)}", "相等断言结果：失败",
                                  attachment_type=allure.attachment_type.JSON)
                    # 使用allure附加断言失败的详细信息
            else:
                failure_count += 1  # 断言失败计数器加1
                logs.error('相等断言失败，请检查yaml文件eq模式的预期结果或接口返回值是否正确')
                # 记录断言失败的日志信息，提示检查预期结果或实际响应

        return failure_count    # 返回断言失败的计数

    @classmethod
    def not_equal_assert(cls, expected_result, response):
        """
        不相等断言，根据yaml里面的validation关键词下面的ne模式数据去跟接口实际响应信息对比
        :param expected_result: （dict）yaml里面的eq值
        :param response: （dict）接口实际响应结果
        :return:   failure_count
        """
        failure_count = 0
        if isinstance(response, dict) and isinstance(expected_result, dict):
            # 找出实际结果与预期结果共同的key值
            common_key = list(expected_result.keys() & response.keys())
            if common_key:
                common_key = common_key[0]
                # 根据相同的key值去实际结果中获取，并重新生成一个实际结果的字典
                new_actual_result = {common_key: response[common_key]}
                eq_assert = operator.ne(new_actual_result, expected_result)
                if eq_assert:
                    logs.info(f"不相等断言成功：接口实际结果 {new_actual_result} != 预期结果：{expected_result}")
                else:
                    failure_count += 1
                    logs.error(f"不相等断言失败：接口实际结果 {new_actual_result} == 预期结果：{expected_result}")
            else:
                failure_count += 1
                logs.error('不相等断言失败，请检查yaml文件eq模式的预期结果或接口返回值是否正确')

        return failure_count

    @classmethod
    def database_assert(cls, expected_result, status_code=None):
        """
        数据库断言
        :param expected_result: yaml文件db模式中的SQL语句预期结果
        :param status_code: 不做任何操作
        :return:
        """
        failure_count = 0
        conn = ConnectMysql()
        db_value = conn.query(expected_result)
        if db_value is not None:
            logs.info('数据库断言成功')
        else:
            failure_count += 1
            logs.error('数据库断言失败，请检查数据库是否存在该数据')
        return failure_count

    @classmethod
    def assert_result(cls, expected_result, response, status_code):
        """
        断言主函数，通过all_flag标记，如all_flag == 0表示测试成功，否则为失败
        :param expected_result: （list）yaml文件validation关键词下面的预期结果
        :param response: （dict）接口的实际响应信息
        :param status_code: （int）接口的实际响应状态码
        :return:
        """
        all_flag = 0
        # 通过字典映射方式管理不同的断言方式
        assert_methods = {
            'code': cls.status_code_assert,
            'contain': cls.contain_assert,
            'eq': cls.equal_assert,
            'ne': cls.not_equal_assert,
            'db': cls.database_assert
        }

        try:
            for yq in expected_result:
                for assert_mode, assert_value in yq.items():
                    # 表示assert_method是一个接受两个参数，类型为Any表示可以是任意类型，并返回整数的可调用对象
                    assert_method: Callable[[Any, Any], int] = assert_methods.get(assert_mode)
                    if assert_method:
                        # 调用对应的断言方法，传递适当的参数
                        if assert_mode in ['code', 'db']:
                            flag = assert_method(assert_value, status_code)
                        else:
                            flag = assert_method(assert_value, response)
                        all_flag += flag
                    else:
                        raise AssertTypeError(f'不支持{assert_mode}该断言模式')

        except Exception as exceptions:
            raise exceptions

        assert all_flag == 0, '测试失败'
        logs.info('测试成功')
