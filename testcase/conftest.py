import pytest
from unit_tools.log_util.recordlog import logs


@pytest.fixture(autouse=True)
def print_info():
    """
    日志打印 Fixture，用于记录接口测试的开始和结束。

    这个 Fixture 在每个 API 测试会话开始和结束时记录日志信息。
    使用 autouse=True 自动在每个测试函数之前和之后运行。

    Yields:
        None: 这个 Fixture 没有返回特定值，但会记录日志信息。
    """
    logs.info('---------------接口测试开始---------------')   # 记录接口测试开始的日志
    yield
    logs.info('---------------接口测试结束---------------')   # 记录接口测试结束的日志
