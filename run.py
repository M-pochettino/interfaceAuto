import os
import shutil

import pytest

if __name__ == '__main__':
    """
    主程序入口，执行测试并生成报告
    """
    pytest.main()  # 调用pytest的main方法，执行测试
    shutil.copy('./environment.xml', './report/temp')  # 复制环境配置文件到报告目录中
    os.system('allure serve ./report/temp')  # 使用操作系统命令启动Allure报告服务，生成并展示测试报告

