import allure
import pytest

from unit_tools.apiutils_business import RequestsBase
from unit_tools.handle_data.yaml_handler import read_yaml


class TestUser:
    @allure.story('权限管理-用户管理')
    # 使用 pytest 的参数化装饰器，从 YAML 文件中获取测试数据
    @pytest.mark.parametrize('api_info', read_yaml('./testcase/testManage/userManage/userManage.yaml'))
    def test_user_module(self, api_info):
        # 设置Allure报告中的测试标题为API名称
        allure.dynamic.title(api_info['baseInfo']['api_name'])
        # 使用RequestsBase类执行测试用例
        RequestsBase().execute_test_cases(api_info)
