import time
from datetime import timedelta

import pytest

from configs.setting import is_dd_msg
from unit_tools.handle_data.yaml_handler import clear_yaml
from unit_tools.other_util.ding_rebot import send_dd_msg


@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    """
    Pytest的fixture，用于在测试会话开始前自动执行清理操作
    :return:
    """
    clear_yaml()    # 调用方法清理yaml文件


def format_duration(seconds):
    """将秒数转换为时分秒格式"""
    return str(timedelta(seconds=seconds)).split('.')[0]  # 将秒数转换为时分秒格式，并去掉毫秒部分


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Pytest框架里面预定义的钩子函数，用于在测试结束后自动化收集测试结果
    :param terminalreporter: Pytest的终端报告对象
    :param exitstatus: 测试的退出状态
    :param config: 测试配置对象
    :return:
    """
    testcase_total = terminalreporter._numcollected  # 获取总共收集到的测试用例数量
    passed_num = len(terminalreporter.stats.get('passed', []))  # 获取通过的测试用例数量
    failed_num = len(terminalreporter.stats.get('failed', []))  # 获取失败的测试用例数量
    error_num = len(terminalreporter.stats.get('error', []))  # 获取出错的测试用例数量
    skip_num = len(terminalreporter.stats.get('skipped', []))  # 获取跳过的测试用例数量
    duration = round(time.time() - terminalreporter._sessionstarttime, 2)  # 计算测试执行的总时长，单位为秒
    formatted_duration = format_duration(duration)  # 将总时长转换为时分秒格式

    # 统计通过率、失败率、错误率
    pass_rate = f"{(passed_num / testcase_total) * 100:.0f}%" if testcase_total > 0 else "N/A"
    fail_rate = f"{(failed_num / testcase_total) * 100:.0f}%" if testcase_total > 0 else "N/A"
    error_rate = f"{(error_num / testcase_total) * 100:.0f}%" if testcase_total > 0 else "N/A"
    # 创建测试结果的摘要信息
    summary = f"""
    自动化测试结果，通知如下，具体执行结果：
    测试用例总数：{testcase_total}  
    测试用例通过数：{passed_num}
    通过率：{pass_rate}
    测试用例失败数：{failed_num}
    失败率：{fail_rate}
    错误数量：{error_num}
    错误率：{error_rate}       
    跳过执行数量：{skip_num}
    执行总时长：{duration}s ({formatted_duration})
    """
    print(summary)  # 打印测试结果摘要
    if is_dd_msg:  # 如果配置为发送钉钉消息
        send_dd_msg(summary)  # 调用方法发送钉钉消息
