import redis
from unit_tools.handle_data.configParse import ConfigParse


class ConnectRedis:
    """
    连接到 Redis 数据库并执行操作。
    """

    def __init__(self):
        """
        初始化 Redis 连接客户端。
        """
        try:
            # 使用 ConfigParse 类从配置文件获取 Redis 连接信息
            self.redis_client = redis.StrictRedis(
                host=ConfigParse().get_redis_conf('host'),  # 获取 Redis 主机地址
                port=ConfigParse().get_redis_conf('port'),  # 获取 Redis 端口号
                db=ConfigParse().get_redis_conf('db')  # 获取 Redis 数据库编号
            )
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")

    def get(self, key):
        """
        获取指定键的值。
        :param key: Redis 键名
        :return: 键对应的值，如果键不存在则返回 None
        """
        try:
            value = self.redis_client.get(key)  # 查询 Redis 中指定键的值
            if value:
                return value.decode('utf-8')  # 解码为字符串并返回
            else:
                return None  # 如果键不存在则返回 None
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return None

    def close(self):
        """
        关闭 Redis 连接。
        """
        self.redis_client.close()  # 关闭 Redis 连接
