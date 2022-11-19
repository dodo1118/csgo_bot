# -*- coding = utf-8 -*-
# @Time: 2022/10/18 20:17
# @Author：dodo
# @Software：PyCharm
import asyncio

import Sentence


async def main_group(uid, gid, message):
    await asyncio.gather(
        Sentence.get_gold_help(gid, message),  # csgo开箱帮助
        Sentence.get_csgo(gid, message, uid),  # csgo武器箱开箱
        Sentence.get_csgo_rank(gid, message),  # 获取财产排名
        Sentence.register_daily(gid, message, uid),  # 每日签到
        Sentence.get_daily_probability(gid, message, uid),  # 每日武器箱概率
        Sentence.get_daily_probability_all(gid, message, uid),  # 所有武器箱概率
        Sentence.get_gold_rank(gid, message),  # 出金榜
        Sentence.get_my_property(gid, message, uid),  # 获得自己的财产
        Sentence.share_money(gid, message, uid),  # 转账
        Sentence.change_weapon_box(gid, message, uid),  # 更换武器箱
        Sentence.get_my_property_weapon(gid, message, uid)  # 查看自己的武器
    )
