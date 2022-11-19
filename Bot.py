# -*- coding = utf-8 -*-
# @Time: 2022/10/7 18:42
# @Author：dodo
# @Software：PyCharm
import asyncio
import sys
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

import QQUtils
import Script
import Sentence
from Csgo import CsgoUtils
from flask_restful import Resource, Api
import os

app = Flask(__name__)
scheduler = BackgroundScheduler(timezone='Asia/Shanghai')

api = Api(app)
os.environ['TZ'] = 'Asia/Shanghai'

queue = {}  # 消息队列


class AcceptMes(Resource):

    def post(self):
        if request.get_json().get('notice_type') == 'group_increase':  # 如果有人加群 在数据库将他插入
            uid = request.get_json().get('user_id')
            gid = request.get_json().get('group_id')
            print('qq: {0} 加入群: {1} '.format(uid, gid))
            QQUtils.update_user_one(uid, gid)
            pass
        if request.get_json().get('message_type') == 'group':  # 如果是群聊信息
            gid = request.get_json().get('group_id')  # 获取群号
            uid = request.get_json().get('sender').get('user_id')  # 获取信息发送者的 QQ号码
            message = request.get_json().get('raw_message')  # 获取原始信息
            print('时间：{0}, 群号：{1}, QQ号:{2}, 消息：{3}'.format(datetime.now(), gid, uid, message))
            if message.startswith('。'):
                # if message.startswith('。') and uid == 2309106919:
                data = {
                    'uid': uid,
                    'gid': gid,
                    'message': message
                }
                print('data数据:{}'.format(data))
                if uid + gid in list(queue.keys()):
                    asyncio.run(Sentence.send_group(gid, '[CQ:at,qq={}]您的任务在处理中,请勿重复提交'.format(uid)))
                    return 'ok'
                queue[uid + gid] = data
            # 此处uid可换为你的qq
            if uid == 2309106919 and message == '。重启':
                python = sys.executable
                os.execl(python, python, *sys.argv)


api.add_resource(AcceptMes, "/", endpoint="index")


def handler_message():
    for i in range(4):
        #   处理消息队列
        if queue:
            value = list(queue.values())[0]
            asyncio.run(Script.main_group(value['uid'], value['gid'], value['message']))
            queue.pop(list(queue.keys())[0])
        # 撤回消息
        if Sentence.message_ids:
            asyncio.run(Sentence.clear_message_group())


if __name__ == '__main__':
    scheduler.add_job(func=CsgoUtils.sender_daily, trigger="cron", hour=0)
    scheduler.add_job(func=CsgoUtils.change_hours, trigger="interval", start_date='2022-11-13 00:00:00', hours=2)
    scheduler.add_job(func=handler_message, trigger="interval", start_date='2022-11-13 00:00:00', seconds=1)
    scheduler.start()
    asyncio.run(QQUtils.update_bot())
    app.run(debug=False, host='127.0.0.1', port=8000, use_reloader=False)
