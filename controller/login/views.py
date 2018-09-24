from aureus import simple_template, render_json, redirect
from aureus.session import session

from core.base_view import BaseView, SessionView


class Login(BaseView):
    def get(self):
        if 'user' in self.session_map:
            return redirect("/")

        return simple_template("login/login.html")


class Logout(SessionView):
    def get(self):
        self.wechat.logout()
        session.pop(self.request, 'user')
        session.pop(self.request, 'status')
        session.pop(self.request, 'is_login')
        session.pop(self.request, 'wechat')

        return redirect("/login")


class GetQrCode(BaseView):
    def get(self):
        image_path = "static/qr_image/{session_id}.png".format(session_id=self.session_id)
        self.wechat.get_qrcode(image_path)
        self.wechat.login(session, self.request)

        return render_json({
            'ok': 1,
            'image_url': '/' + image_path
        })


class CheckLogin(BaseView):
    def get(self):

        message_map = {
            '200': '登录成功，跳转中...',
            '201': '请在手机微信上验证'
        }

        ok = int(self.session_map.get('status', 0))

        if self.session_map.get('status') == '200' and self.session_map.get('is_login'):
            session.push(self.request, 'user', self.wechat.storageClass.nickName)
            ok = 1

        return render_json({
            'ok': ok,
            'message': message_map.get(self.session_map.get('status'), '请扫码登录')
        })