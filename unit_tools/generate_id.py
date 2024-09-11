import random
import time
import uuid


def generate_module_id():
    """
    生成模块id
    :return: 生成的模块id
    """
    for i in range(1, 1000):    # 生成1到999的数字
        module_id = 'M' + str(i).zfill(2) + '_'     # 生成模块id，前缀为'M'，后跟两位数字，不足两位前面补0
        yield module_id     # 使用生成器返回模块id


def generate_testcase_id():
    """
    生成测试用例编号
    :return:
    """
    for i in range(1, 10000):   # 生成1到9999的数字
        case_id = 'C' + str(i).zfill(2) + '_'   # 生成测试用例编号，前缀为'C'，后跟两位数字，不足两位前面补0
        yield case_id   # 使用生成器返回测试用例编号


m_id = generate_module_id()     # 初始化模块id生成器
c_id = generate_testcase_id()   # 初始化测试用例编号生成器


def generate_uuid():
    """
    生成UUID
    :return: 生成的UUID字符串
    """
    try:
        # Attempt to generate UUID using crypto.randomUUID if available
        return str(uuid.uuid4())    # 使用uuid库生成一个随机的UUID
    except AttributeError:
        pass    # 如果uuid库不支持crypto.randomUUID，继续尝试下一个方法

    try:
        # Attempt to use secure random values
        rand_bytes = random.getrandbits(128).to_bytes(16, 'big')  # 生成128位的随机数并转换为16字节的bytes
        return str(uuid.UUID(bytes=rand_bytes, version=4))  # 使用生成的随机bytes创建一个UUID
    except NotImplementedError:
        pass    # 如果不支持getrandbits方法，继续尝试下一个方法

    # Fallback to timestamp-based UUID
    timestamp = int(time.time() * 1000)  # 获取当前时间戳（毫秒）
    random_part = random.randint(0, 2 ** 64)  # 生成一个64位的随机整数
    uuid_str = '{:08x}-{:04x}-4{:03x}-{:04x}-{:012x}'.format(
        timestamp & 0xFFFFFFFF,  # 取时间戳的低32位
        (timestamp >> 32) & 0xFFFF,  # 取时间戳的中间16位
        (timestamp >> 48) & 0xFFF,  # 取时间戳的高12位
        random_part & 0xFFFF,  # 取随机数的低16位
        random_part >> 16  # 取随机数的高48位
    )

    return uuid_str     # 返回生成的UUID字符串
