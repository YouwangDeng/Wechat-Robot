import json
import os
import threading
from multiprocessing.pool import ThreadPool

import itchat
from config import message_dict


sex_map = {
    '1': 'fa-mars',
    '2': 'fa-venus'
}


class WeChat:
    def __init__(self):
        self.wechat = itchat.new_instance()
        self.storageClass = self.wechat.storageClass
        self.get_friends = self.wechat.get_friends
        self.msg_register = self.wechat.msg_register
        self.TYPE = itchat.content.INCOME_MSG
        self.friend_list = []

        self.is_logging = False

        if not os.path.exists(message_dict):
            self.message_map = {}
            with open(message_dict, 'w') as f:
                f.write(json.dumps(self.message_map))
        else:
            with open(message_dict, 'r') as fr:
                self.message_map = json.loads(fr.read())

    def save_message_config(self):
        with open(message_dict, 'w') as fw:
            fw.write(json.dumps(self.message_map))

    def download_head(self, path, filename):
        rep = self.wechat.s.get('https://wx2.qq.com' + path, stream=True)

        path = os.path.join('static', 'head', self.wechat.storageClass.nickName)

        if not os.path.exists(path):
            os.mkdir(path)

        with open(os.path.join(path, filename), 'wb') as f:
            f.write(rep.content)

    def login(self, s, request):

        def do():
            self.is_logging = True
            while True:
                s.push(request, 'status', self.wechat.check_login())
                if s.get(request, 'status') == '200':
                    break
            self.wechat.web_init()
            self.wechat.show_mobile_login()
            self.wechat.get_contact(True)
            self.wechat.start_receiving()

            self.download_head(self.wechat.storageClass.headImgUrl, 'user.jpeg')

            self.init_replay(s, request)
            self.init_friends()

            self.wechat.run()

        if not self.is_logging:
            threading.Thread(target=do).start()

    def get_qrcode(self, path):
        self.wechat.get_QRuuid()
        self.wechat.get_QR(picDir=path)

    def logout(self):
        self.wechat.logout()

    def init_replay(self, s, request):
        @self.wechat.msg_register(self.TYPE)
        def replay(message):
            self.wechat.send(self.message_map['auto_replay'], message['FromUserName'])

    def init_friends(self, s, request):
        friends = self.wechat.get_friends(update=True)

        pool = ThreadPool(processes=15)
        for friend in friends[1:]:
            data = {}

            path = os.path.join('static', 'head', self.storageClass.nickName, friend['NickName'].replace(" ", '') + '.jpeg')
            if not os.path.exists(path):
                pool.apply_async(self.download_head, (friend['HeadImgUrl'], friend['NickName'].replace(" ", '') + '.jpeg'))

            data['image_url'] = '/static/head/{user}/{nick_name}.jpeg'.format(user=self.storageClass.nickName, nick_name=friend['NickName'].replace(" ", ''))
            data['nick_name'] = friend['NickName']
            data['mark_name'] = friend['RemarkName']
            data['sex'] = sex_map.get(str(friend['Sex']), '')
            data['province'] = friend['Province']
            data['city'] = friend['City']
            data['signature'] = friend['Signature']
            data['user_name'] = friend['UserName']

            self.friend_list.append(data)
        s.push(request, 'is_login', True)

    def get_friend_list(self):
        return self.friend_list