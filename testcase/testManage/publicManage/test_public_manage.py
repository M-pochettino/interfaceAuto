import allure
import pytest

from unit_tools.apiutils_business import RequestsBase
from unit_tools.handle_data.excel_handler import get_excel_data


class TestPublic:
    # 使用 pytest 的参数化装饰器，从 Excel 表格中获取测试数据
    @pytest.mark.parametrize('api_info', get_excel_data('./testcase/excel/publicManage.xlsx'))
    def test_public_module(self, api_info):
        # 添加测试报告的动态故事（Story）和动态标题（Title），从测试数据中获取基本信息
        allure.dynamic.story(api_info['baseInfo']['model'])
        allure.dynamic.title(api_info['baseInfo']['api_name'])
        # 调用 RequestsBase 类的 execute_test_cases 方法执行测试用例
        RequestsBase().execute_test_cases(api_info)
