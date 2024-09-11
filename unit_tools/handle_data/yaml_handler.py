import os

import yaml

from configs.setting import FILE_PATH
from unit_tools.log_util.recordlog import logs


def read_yaml(yaml_path):
    """
    读取yaml文件数据
    :param yaml_path: 文件路径
    :return: 包含测试用例数据的列表或字典
    """
    try:
        testcase_list = []
        with open(yaml_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            # 处理一个yaml文件多条测试用例的场景
            if len(data) <= 1:
                yaml_data = data[0]
                base_info = yaml_data.get('baseInfo')
                for ts in yaml_data.get('testCase'):
                    params = [base_info, ts]
                    testcase_list.append(params)
                return testcase_list
            else:
                return data
    except UnicodeDecodeError:
        logs.error(f'{yaml_path}文件编码格式错误，--尝试使用utf-8去解码YAML文件发生错误，请确保你的yaml文件是utf-8格式！')
    except yaml.YAMLError as e:
        logs.error(f'Error：读取yaml文件失败，请检查格式 -{yaml_path}，{e}')
    except Exception as e:
        logs.error(f'读取{yaml_path}文件时出现异常，原因：{e}')


def write_yaml(value):
    """
    将数据写入yaml文件
    :param value: 需要写入的数据，必须是字典类型
    :return: None
    """
    file_ptah = FILE_PATH['extract']    # 获取yaml文件路径
    if not os.path.exists(file_ptah):
        with open(file_ptah, 'w'):      # 如果文件不存在，创建空文件
            pass
    file = None
    try:
        file = open(file_ptah, 'a', encoding='utf-8')      # 以追加模式打开文件
        if isinstance(value, dict):
            write_data = yaml.dump(value, allow_unicode=True, sort_keys=False)      # 转换数据并写入文件
            file.write(write_data)
        else:
            logs.warning('写入的数据必须为字典类型！')
    except Exception as e:
        logs.error(f'写入yaml文件出现异常，原因：{e}')
    finally:
        file.close()


def clear_yaml():
    """
    清空extract.yaml文件数据
    :return: None
    """
    with open(FILE_PATH['extract'], 'w') as f:      # 获取yaml文件路径
        f.truncate()    # 清空文件内容


def get_extract_yaml(node_name, sub_node_name=None):
    """
    获取extract.yaml文件中的数据
    :param node_name: 第一级key值
    :param sub_node_name: 第二级key值，可选
    :return: 指定key对应的值
    """
    file_ptah = FILE_PATH['extract']    # 获取yaml文件路径
    try:
        with open(file_ptah, 'r', encoding='utf-8') as file:
            extract_data = yaml.safe_load(file)
            if sub_node_name is None:
                return extract_data[node_name]      # 返回第一级key对应的值
            else:
                return extract_data.get(node_name, {}).get(sub_node_name)       # 返回第二级key对应的值
    except yaml.YAMLError as e:
        logs.error(f'Error：读取yaml文件失败，请检查格式 -{file_ptah}，{e}')
    except Exception as e:
        logs.error(f'Error：未知异常 - {e}')
