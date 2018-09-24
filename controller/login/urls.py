from controller.login import views


url_maps = [
    {'url': '/login', 'view': views.Login, 'endpoint': 'login'},
    {'url': '/logout', 'view': views.Logout, 'endpoint': 'logout'},

    {'url': '/api/get_qrcode', 'view': views.GetQrCode, 'endpoint': 'get_qrcode'},
    {'url': '/api/check_login', 'view': views.CheckLogin, 'endpoint': 'check_login'}
]