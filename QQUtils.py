# -*- coding = utf-8 -*-
# @Time: 2022/11/12 13:05
# @Author：dodo
# @Software：PyCharm
import asyncio

import httpx

from Mysql.MysqlUtils import UsingMysql


async def get_groups():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:5700/") as client:
        return await client.get("/get_group_list", timeout=20)


async def get_users(gid):
    async with httpx.AsyncClient(base_url="http://127.0.0.1:5700/") as client:
        payload = {
            "group_id": gid,
        }
        return await client.get("/get_group_member_list", params=payload, timeout=20)


async def get_user(gid, uid):
    async with httpx.AsyncClient(base_url="http://127.0.0.1:5700/") as client:
        payload = {
            "group_id": gid,
            "user_id": uid
        }
        return await client.get("/get_group_member_info", params=payload, timeout=20)


async def update_group(group_ids):
    with UsingMysql() as um:
        for group in group_ids:
            result = um.select_one("select * from group_ where group_id = %s", group)
            if result:
                print("{0}群已在数据库存在".format(group))
                continue
            um.create("insert into group_(group_id) values(%s)", group)
    print('QQ群更新完成')


async def update_user(group_ids):
    qq_ids = []
    with UsingMysql() as um:
        for group_id in group_ids:
            results_qq = await get_users(group_id)
            results_qq = results_qq.json()['data']
            for result in results_qq:
                qq_ids.append(result['user_id'])
            for qq_id in qq_ids:
                """
                此处有问题！！！！记得修
                问题：更新群的时候如果已经有群了 会把不是非群成员的人加入进来 虽不影响使用 但会影响一定的性能
                """
                result = um.select_one("select * from user where qq_id = %s and group_id = %s", [qq_id, group_id])
                if result:
                    continue
                print("QQ号: {0} 添加到数据库".format(qq_id))
                um.create("insert into user(qq_id, money, group_id, day) values(%s, %s, %s, %s)",
                          [qq_id, 0, group_id, 0])
                um.create("insert into qq_group(qq, group_id) values(%s, %s)", [qq_id, group_id])
        qq_ids.clear()
    print('QQ群成员更新完成')


async def update_bot():
    group_ids = []
    results_group = await get_groups()
    results_group = results_group.json()['data']
    for result in results_group:
        group_ids.append(result['group_id'])
    await update_group(group_ids)
    await update_user(group_ids)
    print('qq数据更新完成!')
    return 'ok'


def update_user_one(uid, gid):
    with UsingMysql() as um:
        result = um.select_one("select * from user where qq_id = %s and group_id = %s", [uid, gid])
        if result:
            return 'ok'
        um.create("insert into user(qq_id, money, group_id, day) values(%s, %s, %s, %s)",
                  [uid, 0, gid, 0])
        um.create("insert into qq_group(qq, group_id) values(%s, %s)", [uid, gid])
    return 'ok'
