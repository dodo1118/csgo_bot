# -*- coding = utf-8 -*-
# @Time: 2022/10/7 19:16
# @Author：dodo
# @Software：PyCharm
from datetime import datetime

import httpx
import aiohttp

from Csgo import CsgoUtils

# 请求头
headers = {"content-type": "application/json"}
message_ids = {}


async def fetch_content(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def get_gold_help(gid, message):
    if message == "。开箱帮助":
        payload = {
            "group_id": gid,
            "message": "[CQ:image,file=https://i0.hdslb.com/bfs/album/e630167dee9d68dd0179d41ea84b7ca769993b83.png]"
        }
        await send_group_day(gid, payload.get('message'))
    return 'ok'


async def send_group(gid, message):
    async with httpx.AsyncClient(base_url="http://127.0.0.1:5700/") as client:
        payload = {
            "group_id": gid,
            "message": message
        }
        message_id = await client.get("/send_group_msg", params=payload, timeout=20)
        if message_id:
            message_id = message_id.json()['data']['message_id']
            message_ids[message_id] = datetime.now()
    return 'ok'


# 发送不会撤回的消息
async def send_group_day(gid, message):
    async with httpx.AsyncClient(base_url="http://127.0.0.1:5700/") as client:
        payload = {
            "group_id": gid,
            "message": message
        }
        await client.get("/send_group_msg", params=payload, timeout=20)
    return 'ok'


async def clear_message_group():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:5700/") as client:
        if message_ids:
            key = list(message_ids.keys())[0]
            value = list(message_ids.values())[0]
            #   1分钟后撤回消息
            if datetime.now() - value > datetime(2017, 3, 22, 16, 10, 29, 0) - datetime(2017, 3, 22, 16, 9, 29, 0):
                payload = {
                    "message_id": key,
                }
                message_ids.pop(list(message_ids.keys())[0])
                await client.get("/delete_msg", params=payload, timeout=20)
    return 'ok'


async def get_csgo(gid, message, uid):
    if message == '。开箱':
        await CsgoUtils.sender_csgo(gid, uid)
    return 'ok'


async def get_csgo_rank(gid, message):
    if message == '。排行榜':
        await CsgoUtils.get_richer(gid)

    if message == '。倒霉蛋':
        await CsgoUtils.get_unlucky_guy(gid)
    return 'ok'


async def register_daily(gid, message, uid):
    if message == '。签到':
        await CsgoUtils.register_day(gid, uid)
    return 'ok'


async def get_daily_probability(gid, message, uid):
    if message == '。当前武器箱':
        mess = await CsgoUtils.get_day_probability(gid)
        await send_group(gid, message=mess)
    return 'ok'


async def get_daily_probability_all(gid, message, uid):
    if message == '。所有武器箱':
        mess = await CsgoUtils.get_day_probability_all()
        await send_group_day(gid, message=mess)
    return 'ok'


async def change_weapon_box(gid, message, uid):
    if message == '。更换武器箱':
        await CsgoUtils.change_weapon_box(gid, uid)
    return 'ok'


async def get_gold_rank(gid, message):
    if message == '。出金榜':
        await CsgoUtils.gold_rank(gid)
    return 'ok'


async def get_my_property(gid, message, uid):
    if message == '。我的财产':
        await CsgoUtils.get_my_property_(gid, uid)
    return 'ok'


async def share_money(gid, message: str, uid):
    if message.startswith('。转账'):
        await CsgoUtils.share_money(gid, message, uid)
    return 'ok'


async def get_my_property_weapon(gid, message, uid):
    if message.startswith('。我的武器') and len(message) <= 5:
        await send_group_day(gid, '请输入页码')
        return 'ok'
    if message.startswith('。我的武器') and len(message) > 5:
        page_no = int(message[-1])
        if page_no <= 0:
            await send_group_day(gid, '请输入正确的页码')
            return 'ok'
        await CsgoUtils.get_my_property_weapon(gid, uid, page_no)
    return 'ok'
