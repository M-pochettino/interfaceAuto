import pymysql

from unit_tools.handle_data.configParse import ConfigParse
from unit_tools.log_util.recordlog import logs

# 创建 ConfigParse 的实例
conf = ConfigParse()


class ConnectMysql:
    """
    连接MySQL数据库，进行增删改查操作
    """

    def __init__(self):
        self.conf = {
            'host': conf.get_conf('MySQL', 'host'),  # 从配置文件中获取数据库主机地址
            'port': int(conf.get_conf('MySQL', 'port')),  # 从配置文件中获取数据库端口号，并转换为整数
            'user': conf.get_conf('MySQL', 'user'),  # 从配置文件中获取数据库用户名
            'password': conf.get_conf('MySQL', 'password'),  # 从配置文件中获取数据库密码
            'database': conf.get_conf('MySQL', 'database')  # 从配置文件中获取数据库名称
        }

        try:
            # 尝试建立数据库连接
            self.conn = pymysql.connect(**self.conf)
            # 获取操作游标
            # cursor=pymysql.cursors.DictCursor：将数据库表字段显示，以key-value形式显示
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            logs.info(f'成功连接到数据库：数据库ip：{self.conf.get("host")}')
        except Exception as e:
            # 连接失败时记录日志
            logs.error(f"连接数据库失败，原因：{e}")

    def close(self):
        """
        关闭数据库连接和游标。
        :return: True，表示成功关闭连接
        """
        if self.conn and self.cursor:
            self.conn.close()
            self.cursor.close()
        return True

    def query(self, sql, fetchall=False):
        """
        查询数据库数据
        :param sql: 查询的SQL语句
        :param fetchall: 查询全部数据，默认为False则查询单条数据
        :return:
        """
        try:
            self.cursor.execute(sql)  # 执行SQL查询语句
            self.conn.commit()  # 提交事务
            if fetchall:
                res = self.cursor.fetchall()  # 获取所有查询结果
            else:
                res = self.cursor.fetchone()  # 获取单条查询结果
            return res
        except Exception as e:
            logs.error(f'查询数据库内容出现异常，{e}')  # 查询异常时记录日志
        finally:
            self.close()  # 最终关闭数据库连接

    def delete(self, sql):
        """
        删除数据库内容
        :param sql: 删除的SQL语句
        :return:
        """
        try:
            self.cursor.execute(sql)  # 执行SQL删除语句
            self.conn.commit()  # 提交事务
            logs.info('数据库数据删除成功')  # 记录删除成功的日志
        except Exception as e:
            logs.error(f'删除数据库数据出现异常，{e}')  # 删除异常时记录日志
        finally:
            self.close()  # 最终关闭数据库连接
