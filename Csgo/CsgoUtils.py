# -*- coding = utf-8 -*-
# @Time: 2022/11/11 20:50
# @Author：dodo
# @Software：PyCharm
import asyncio
import math
import random
from datetime import datetime
from decimal import Decimal

import aiohttp

import QQUtils
import Sentence
from Mysql.MysqlUtils import UsingMysql
from entity.CsgoEntity import Csgo

headers = {
    'Host': 'lycsgo.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Content-Length': '17',
    'Origin': 'https://lycsgo.com',
    'Connection': 'keep-alive',
    'Referer': 'https://lycsgo.com/box/detail?id=138',
    'Cookie': 'Hm_lvt_c152d811595b70974247b8c08a3cf8a8=1668167617,1668244276,1668316747; PHPSESSID=5uccuds85mbjr7o0c87j8926db; Hm_lpvt_c152d811595b70974247b8c08a3cf8a8=1668323957',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin'
}
url = 'https://lycsgo.com/box/dodraw'
weapon_wox_img_path = 'http://43.143.161.197:9090/img/'
weapon_box = {
    0: {'name': '一号武器箱', 'cid': '1657', 'money': 500},
    1: {'name': '二号武器箱', 'cid': '9960', 'money': 200},
    2: {'name': '三号武器箱', 'cid': '9995', 'money': 70},
    3: {'name': '四号武器箱', 'cid': '9996', 'money': 30},
    4: {'name': '五号武器箱', 'cid': '9970', 'money': 300},
    5: {'name': '六号武器箱', 'cid': '9986', 'money': 130},
    6: {'name': '七号武器箱', 'cid': '9989', 'money': 45},
    7: {'name': '八号武器箱', 'cid': '9991', 'money': 700},
    8: {'name': '九号武器箱', 'cid': '9997', 'money': 2000},
    9: {'name': '十号武器箱', 'cid': '1027', 'money': 20000},
    10: {'name': '十一号武器箱', 'cid': '9984', 'money': 1300},
    11: {'name': '十二号武器箱', 'cid': '9968', 'money': 90}
}


async def fetch_content(url_, data: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(url_, data=data, headers=headers) as response:
            return await response.json()


async def get_qq_name(uid, gid):
    result = await QQUtils.get_user(gid, uid)
    result = result.json()
    if result['data']['card'] == '':
        return result['data']['nickname']
    return result['data']['card']


async def get_csgo_object(data: dict):
    result = (await fetch_content(url, data=data))['data']['list'][0]
    csgo_obj = Csgo()
    csgo_obj.set_csgo(csgo={
        'name_': result['name'],
        'icon': result['icon'],
        'exterior_name': result['exterior_name'],
        'price': result['price'],
        'qq': '',
        'group_': ''
    })
    return csgo_obj


async def sender_csgo(gid, uid):
    result = await get_group_weapon(gid)
    index = result['weapon_box_index']
    data_today = weapon_box[index]
    data = {
        'cid': data_today['cid'],
        'number': '1'
    }
    csgo = await get_csgo_object(data)
    csgo.set_csgo_group(gid)
    csgo.set_csgo_qq(uid)
    await update_user_money(uid, gid, Decimal(csgo.get_csgo_price()) - data_today['money'])
    payload = {
        "group_id": gid,
        "message": '[CQ:at,qq={0}]\n'
                   '恭喜你获得:{1}\n'
                   '[CQ:image,file={2}]\n'
                   '磨损度:{3}\n'
                   '价值:{4}￥'.format(csgo.get_csgo_qq(), csgo.get_csgo_name(), csgo.get_csgo_icon(),
                                    csgo.get_csgo_exterior_name(),
                                    csgo.get_csgo_price())
    }
    await Sentence.send_group(payload['group_id'], payload['message'])
    if Decimal(csgo.get_csgo_price()) > Decimal(1000):
        await add_user_obj(qq_id=uid, csgo=csgo)
    if Decimal(csgo.get_csgo_price()) > 1000:
        await add_csgo_obj(uid, csgo)
    return 'ok'


async def update_user_money(qq_id: int, group_id: int, change: Decimal):
    with UsingMysql() as um:
        result = um.select_one("select * from user where qq_id = %s and group_id = %s", [qq_id, group_id])['money']
        result = result + change
        um.update("update user set money = %s where qq_id = %s and group_id = %s", [result, qq_id, group_id])


async def add_user_obj(qq_id: int, csgo: Csgo):
    with UsingMysql() as um:
        result = um.select_one(
            "select name_, icon, exterior_name, price, qq_id from csgo_user where qq_id=%s and name_=%s",
            [qq_id, csgo.get_csgo_name()])
        if result and csgo.get_csgo_name() == result['name_'] and Decimal(csgo.get_csgo_price()) <= Decimal(
                result['price']):
            return 'ok'
        um.delete("delete from csgo_user where qq_id=%s and name_=%s", [qq_id, csgo.get_csgo_name()])
        um.create("insert into csgo_user(name_, icon, exterior_name, price, qq_id) VALUES (%s,%s,%s,%s,%s)",
                  [csgo.get_csgo_name(), csgo.get_csgo_icon(), csgo.get_csgo_exterior_name(), csgo.get_csgo_price(),
                   qq_id])
        return 'ok'


async def add_csgo_obj(qq_id: int, csgo: Csgo):
    with UsingMysql() as um:
        result = um.select_one("select name_, icon, exterior_name, price, qq from csgo_obj where qq=%s and name_=%s",
                               [qq_id, csgo.get_csgo_name()])
        if result and csgo.get_csgo_name() == result['name_'] and Decimal(csgo.get_csgo_price()) <= Decimal(
                result['price']):
            return 'ok'
        um.delete("delete from csgo_obj where qq=%s and name_=%s", [qq_id, csgo.get_csgo_name()])
        um.create("insert into csgo_obj(qq, group_, name_, icon, exterior_name, price) VALUES (%s, %s, %s, %s, %s, %s)",
                  [csgo.get_csgo_qq(), csgo.get_csgo_group(), csgo.get_csgo_name(), csgo.get_csgo_icon(),
                   csgo.get_csgo_exterior_name(),
                   csgo.get_csgo_price()])
        return 'ok'


async def get_group_weapon(gid: int):
    with UsingMysql() as um:
        result = um.select_one("select weapon_box_index from group_ where group_id=%s", gid)
    return result


async def get_richer(group_id: int):
    print(group_id)
    with UsingMysql() as um:
        results = um.select_all("select qq_id, money from user where money > 0 and group_id = %s order by money desc "
                                "limit 5", group_id)
    if not results:
        payload = {
            "group_id": group_id,
            "message": '暂无'
        }
        await Sentence.send_group(payload['group_id'], payload['message'])
        return 'ok'

    message = '富豪榜:\n'
    for i, result in enumerate(results):
        message = message + '{0}、{1} 财产:{2}￥\n'.format(i + 1, await get_qq_name(result['qq_id'], group_id),
                                                       result['money'])

    payload = {
        "group_id": group_id,
        "message": message[:-1]
    }
    await Sentence.send_group_day(payload['group_id'], payload['message'])


async def get_unlucky_guy(group_id: int):
    with UsingMysql() as um:
        results = um.select_all("select qq_id, money from user where money < 0 and group_id = %s order by money ",
                                group_id)
    if not results:
        payload = {
            "group_id": group_id,
            "message": '暂无'
        }
        await Sentence.send_group_day(payload['group_id'], payload['message'])
        return 'ok'

    message = '倒霉蛋: \n'
    for i, result in enumerate(results):
        message = message + '{0}、{1} 财产:{2}￥\n'.format(i + 1, await get_qq_name(result['qq_id'], group_id),
                                                       result['money'])

    payload = {
        "group_id": group_id,
        "message": message[:-1]
    }
    await Sentence.send_group_day(payload['group_id'], payload['message'])


async def register_day(group_id: int, qq_id: int):
    with UsingMysql() as um:
        result = um.select_one("select money, day from user where qq_id = %s and group_id = %s", [qq_id, group_id])
        if result['day'] == 0:
            money = result['money'] + Decimal(500)
            um.update("update user set money = %s, day = %s where qq_id = %s and group_id = %s",
                      [money, 1, qq_id, group_id])
            message = '[CQ:at,qq={0}]签到成功,获得500￥,您当前财产为:{1}￥'.format(qq_id, money)
        elif result['day'] == 1:
            message = '[CQ:at,qq={0}]您今日已签过到!请勿重复签到'.format(qq_id)
    payload = {
        "group_id": group_id,
        "message": message
    }
    await Sentence.send_group_day(payload['group_id'], payload['message'])


async def register_day_clear():
    print('每日签到已刷新')
    with UsingMysql() as um:
        um.update("update user set day = 0 where day = %s", 1)
        um.update("update group_ set number = 5 where group_id > 0")
    return 'ok'


async def csgo_daily():
    await register_day_clear()
    return 'ok'


def sender_daily():
    if datetime.now().hour == 0:
        asyncio.run(csgo_daily())
    return 'ok'


async def gold_rank(gid):
    with UsingMysql() as um:
        results = um.select_all("select qq, group_, name_, icon, exterior_name, price from csgo_obj where group_ = %s "
                                "and price > 1000 order by price desc limit 5", gid)
        if not results:
            payload = {
                "group_id": gid,
                "message": '暂无'
            }
            await Sentence.send_group_day(payload['group_id'], payload['message'])
            return 'ok'

        message = ''
        for result in results:
            message = message + ('{0}\n'
                                 '名称:{1}\n'
                                 '[CQ:image,file={2}]\n'
                                 '磨损度:{3}\n'
                                 '价值:{4}￥\n'
                                 '================\n'.format(await get_qq_name(result['qq'], gid), result['name_'],
                                                             result['icon'],
                                                             result['exterior_name'],
                                                             result['price']))
    payload = {
        "group_id": gid,
        "message": message
    }
    await Sentence.send_group(payload['group_id'], payload['message'])
    return 'ok'


async def get_day_probability(gid):
    result = await get_group_weapon(gid)
    index = result['weapon_box_index']
    data_today = weapon_box[index]
    img_path = weapon_wox_img_path + data_today['name'] + '.png'
    return '当前武器箱为：{0}\n花费为：{1}￥\n[CQ:image,file={2},c=2]'.format(data_today['name'], data_today['money'], img_path)


async def get_day_probability_all():
    message = ''
    for index in range(12):
        name = weapon_box[index]['name']
        img_path = weapon_wox_img_path + weapon_box[index]['name'] + '.png'
        message = message + name + ' 花费{0}￥\n[CQ:image,file={1}]\n================\n' \
            .format(weapon_box[index]['money'], img_path)
    return message


async def get_my_property_(gid, uid):
    with UsingMysql() as um:
        result_price = um.select_one("select money from user where group_id=%s and qq_id=%s", [gid, uid])
    message = '[CQ:at,qq={0}]的财产为: {1}￥'.format(uid, result_price['money'])
    payload = {
        "group_id": gid,
        "message": message
    }
    await Sentence.send_group_day(payload['group_id'], payload['message'])
    return 'ok'


async def get_my_property_weapon(gid, uid, page_no):
    page_no_temp = (page_no - 1) * 3
    with UsingMysql() as um:
        count = um.select_one("SELECT COUNT(*) FROM csgo_user where qq_id=%s", uid)
        totalPageNum = math.ceil(count['COUNT(*)'] / 3)
        result_weapons = um.select_all(
            "select name_, icon, exterior_name, price, qq_id from csgo_user where qq_id=%s order by price desc limit  %s, 3",
            [uid, page_no_temp])
        if not result_weapons:
            await Sentence.send_group_day(gid, '暂无')
            return 'ok'
        if page_no > totalPageNum:
            await Sentence.send_group_day(gid, '[CQ:at,qq={0}]您一共有{1}页武器,请输入正确的页数'.format(uid, totalPageNum))
            return 'ok'

    message = '[CQ:at,qq={0}]的第{1}/{2}页的物品:\n================\n'.format(uid, page_no, totalPageNum)
    for weapon in result_weapons:
        message = message + '名称:{0}\n[CQ:image,file={1}]\n磨损度:{2}\n价值:{3}￥\n================\n' \
            .format(weapon['name_'],
                    weapon['icon'],
                    weapon['exterior_name'],
                    weapon['price'])
    payload = {
        "group_id": gid,
        "message": message
    }
    await Sentence.send_group(payload['group_id'], payload['message'])
    return 'ok'


async def share_money(gid, message, uid):
    with UsingMysql() as um:
        result = um.select_one("select money from user where group_id=%s and qq_id=%s", [gid, uid])
    target_qq, money = message[13:].split(']')
    target_qq = int(target_qq)
    money = Decimal(money)
    if money <= 0 or money > Decimal(result['money']):
        payload = {
            "group_id": gid,
            "message": '请输入正确的金额'
        }
        await Sentence.send_group(payload['group_id'], payload['message'])
        return 'ok'
    await update_user_money(uid, gid, -money)
    await update_user_money(target_qq, gid, money)
    payload = {
        "group_id": gid,
        "message": '[CQ:at,qq={0}]转账成功'.format(uid)
    }
    await Sentence.send_group(payload['group_id'], payload['message'])
    return 'ok'


async def update_group_weapon_box_all(index: int):
    with UsingMysql() as um:
        um.update("update group_ set weapon_box_index = %s where group_id > 0", index)


async def update_group_weapon_box(index: int, group_id: int):
    with UsingMysql() as um:
        um.update("update group_ set weapon_box_index = %s where group_id=%s", [index, group_id])


async def change_weapon_hours():
    index = random.randint(0, 11)
    await update_group_weapon_box_all(index)
    return 'ok'


def change_hours():
    asyncio.run(change_weapon_hours())
    MessageDaily.flag_night = True
    MessageDaily.flag_morning = True
    MessageDaily.flag_noon = True


async def change_weapon_box(gid, uid):
    result = await QQUtils.get_user(gid, uid)
    result = result.json()
    role = result['data']['role']
    index = random.randint(0, 11)
    if role != 'member':
        #  管理员
        print('群【{}】武器箱已更新'.format(gid))
        await update_group_weapon_box(index, gid)
        payload = {
            "group_id": gid,
            "message": '武器箱已更新'
        }
        await Sentence.send_group(payload['group_id'], payload['message'])
        return 'ok'

    # 普通成员
    with UsingMysql() as um:
        result = um.select_one("select number from group_ where group_id=%s", gid)
        number = result['number']
        if number == 0:
            payload = {
                "group_id": gid,
                "message": '刷新机会已用完,请联系管理员刷新武器箱。'
            }
            await Sentence.send_group(payload['group_id'], payload['message'])
            return 'ok'
        await update_group_weapon_box(index, gid)
        um.update("update group_ set number=%s where group_id = %s", [number, gid])
        number = number - 1
    payload = {
        "group_id": gid,
        "message": '[CQ:at,qq={0}]刷新成功，还剩{1}次刷新机会'.format(uid, number)
    }
    await Sentence.send_group(payload['group_id'], payload['message'])
    return 'ok'
