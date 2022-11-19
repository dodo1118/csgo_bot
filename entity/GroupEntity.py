# -*- coding = utf-8 -*-
# @Time: 2022/11/12 12:54
# @Author：dodo
# @Software：PyCharm

class Group:
    def setQQ(self, data):
        self.group_id = data['group_id']

    def set_group_id(self, group_id):
        self.group_id = group_id

    def get_group_id(self):
        return self.group_id
