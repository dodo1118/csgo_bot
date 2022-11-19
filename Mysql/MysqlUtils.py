# -*- coding = utf-8 -*-
# @Time: 2022/11/12 12:15
# @Author：dodo
# @Software：PyCharm


import pymysql

host = ''  # 主机
port = ''  # 端口
db = ''  # 表名
user = ''
password = ''


def get_connection():
    conn = pymysql.connect(host=host, port=port, db=db, user=user, password=password)
    return conn


# ---- 使用 with 的方式来优化代码
class UsingMysql(object):

    def __init__(self, commit=True):
        """
        :param commit: 是否在最后提交事务(设置为False的时候方便单元测试)
        """
        self._commit = commit

    def __enter__(self):
        # 在进入的时候自动获取连接和cursor
        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        conn.autocommit = False

        self._conn = conn
        self._cursor = cursor
        return self

    def __exit__(self, *exc_info):
        # 提交事务
        if self._commit:
            self._conn.commit()
        # 在退出的时候自动关闭连接和cursor
        self._cursor.close()
        self._conn.close()

    # ========= 一系列封装的业务方法

    def select_all(self, sql, args=None):
        """查询所有"""
        self._cursor.execute(sql, args)
        results = self._cursor.fetchall()
        return results

    def select_one(self, sql, args):
        """查询一个"""
        self._cursor.execute(sql, args)
        result = self._cursor.fetchone()
        return result

    def update(self, sql, args):
        """修改数据"""
        self._cursor.execute(sql, args)
        self._conn.commit()

    def create(self, sql, args):
        """新增数据"""
        self._cursor.execute(sql, args)
        self._conn.commit()

    def delete(self, sql, args):
        """删除数据"""
        self._cursor.execute(sql, args)
        self._conn.commit()
