# -*- coding = utf-8 -*-
# @Time: 2022/11/12 12:54
# @Author：dodo
# @Software：PyCharm

class QQ:
    def setQQ(self, data):
        self.qq_id = data['qq_id']
        self.group_id = data['group_id']
        self.money = data['money']
        self.day = data['day']

    def set_qq_id(self, qq_id):
        self.qq_id = qq_id

    def set_group_id(self, group_id):
        self.group_id = group_id

    def set_money(self, money):
        self.money = money

    def set_day(self, day):
        self.day = day

    def get_day(self):
        return self.day

    def get_qq_id(self):
        return self.qq_id

    def get_group_id(self):
        return self.group_id

    def get_money(self):
        return self.money
