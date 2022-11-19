# -*- coding = utf-8 -*-
# @Time: 2022/11/11 20:28
# @Author：dodo
# @Software：PyCharm

class Csgo:
    def set_csgo(self, csgo: dict):
        self.name_ = csgo['name_']
        self.icon = csgo['icon']
        self.exterior_name = csgo['exterior_name']
        self.price = csgo['price']
        self.qq = csgo['qq']
        self.group_ = csgo['group_']

    def get_csgo_name(self):
        return self.name_

    def get_csgo_icon(self):
        return self.icon

    def get_csgo_exterior_name(self):
        return self.exterior_name

    def get_csgo_price(self):
        return self.price

    def get_csgo_qq(self):
        return self.qq

    def get_csgo_group(self):
        return self.group_

    def set_csgo_name(self, name_):
        self.name_ = name_

    def set_csgo_icon(self, icon):
        self.icon = icon

    def set_csgo_exterior_name(self, exterior_name):
        self.exterior_name = exterior_name

    def set_csgo_price(self, price):
        self.price = price

    def set_csgo_qq(self, qq):
        self.qq = qq

    def set_csgo_group(self, group_):
        self.group_ = group_
