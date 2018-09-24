#!/usr/bin/env python
# encoding: utf-8

from aureus import redirect
from aureus.session import AuthSession, session, get_session_id
from aureus.view import View

from core.wechat_manager import WeChat
import aureus.exceptions as exceptions


class BaseView(View):
    methods = ['GET, POST']
    request = None
    session_id = None
    session_map = None
    wechat = None

    def post(self):
        pass

    def get(self):
        pass

    def dispatch_request(self, request, *args, **options):
        methods_meta = {
            'GET': self.get,
            'POST': self.post,
        }

        self.request = request
        self.session_id = get_session_id(request)
        self.session_map = session.map(request)

        if 'wechat' not in self.session_map:
            session.push(request, 'wechat', WeChat(), is_save=False)
            self.wechat = session.get(request, 'wechat')

        self.wechat = session.get(request, 'wechat')

        if request.method in methods_meta:
            return methods_meta[request.method]()
        else:
            raise exceptions.InvalidRequestMethodError


class AuthLogin(AuthSession):

    # 如果没有验证通过，则返回一个链接点击到登录页面
    @staticmethod
    def auth_fail_callback(request, *args, **options):
        return redirect("/login")

    # 验证逻辑，如果 user 这个键不在会话当中，则验证失败，反之则成功
    @staticmethod
    def auth_logic(request, *args, **options):
        if 'user' in session.map(request):
            return True
        return False


# 会话视图基类
class SessionView(BaseView):

    # 验证类抓装饰器
    @AuthLogin.auth_session
    def dispatch_request(self, request, *args, **options):
        # 结合装饰器内部的逻辑，调用继承的子类的 dispatch_request 方法
        return super(SessionView, self).dispatch_request(request, *args, **options)