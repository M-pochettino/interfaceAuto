import allure
import pytest
import requests
import uuid

from unit_tools.apiutils_single import RequestsBase
from unit_tools.db_connector.connectRedis import ConnectRedis
from unit_tools.handle_data.configParse import ConfigParse
from unit_tools.handle_data.yaml_handler import read_yaml

"""
登录模块需要第一个执行，以便后续接口可以获取到token，用于校验访问权限
"""


class TestLogin:
    """登录模块"""

    @allure.story('登录模块')
    @pytest.mark.parametrize('base_info,testcase', read_yaml('./testcase/testManage/login/login.yaml'))
    def test_login_module(self, base_info, testcase):
        # 获取host路径
        host = ConfigParse().get_conf('Host', 'host')
        # 获取code接口路径
        code = ConfigParse().get_conf('Code', 'code')
        # 相加即验证码接口完整访问路径
        url = host + code
        # 生成随机的UUID作为randomStr的值
        parm = str(uuid.uuid4())
        # 每次访问生成验证码接口都要携带一个随机数，即randomStr
        params = {'randomStr': parm}
        # 发送一个get请求，远端系统生成验证码
        requests.get(url, params=params)
        # 根据生成的随机数，获取缓存中的验证码结果
        conn = ConnectRedis()
        # 构建存储在 Redis 中的键名
        key = f'DEFAULT_CODE_KEY:{parm}'
        # 获取缓存中数据
        value = conn.get(key)
        # 关闭 Redis 连接
        conn.close()
        # 获取到底验证码结果赋值给测试用例参数
        testcase['params']['code'] = value
        testcase['params']['randomStr'] = parm
        # 调用allure生成测试报告
        allure.dynamic.title(testcase['case_name'])
        # 调用自动化测试方法
        RequestsBase().execute_test_cases(base_info, testcase)
