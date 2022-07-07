from django import http
from django.core.handlers.wsgi import WSGIRequest
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from book.models import User


def register(request: WSGIRequest):
    username = request.POST.get('username')
    password = request.POST.get('password')
    if User.objects.filter(username=username):
        return http.JsonResponse({'msg': 'username is Duplicated ...'})
    user = User.objects.create_user(username=username, password=password)
    return http.JsonResponse({'id': user.id})



# DRF Token 使用
# 1. DRF自带token auth
# rest_framework.authtoken作为Django的子应用，需要注册、自带Token模型类需要迁移
# 请求时header中添加Authorization(可自定义)，值为Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b，认证成功提供认证材料User对象和Token对象，以json返回token key；认证失败响应401
# 仅有一个视图类，默认下，obtain_auth_token视图使用JSON请求和响应，而不是settings中默认指定的渲染器和解析器类，也没有应用任何权限或节流，如果需要throttle，可以自定义视图类继承并指定throttle_classes如下。
# drf的自带的token认证缺点：最大的缺点就是token永久有效，即一旦发送永远能够登入
class CustomDRFObtainAuthToken(ObtainAuthToken):
    # permission_classes = (IsAuthenticated,)
    # throttle_classes = ('', )


    # def get_token(self, user):
    #     token = Token.objects.filter(user=user).first()
    #     if token is not None:
    #         return token.key
    #     else:
    #         return Token.objects.create(user=user).key
    #
    # def post1(self, request):
    #     token = self.get_token(request.user)
    #     return Response('')

    # 重写post方法
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        # 自定义返回
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

# 2. 第三方包djangorestframework-jwt
# 依赖PyJWT包，提供了JWT的视图操作，安装后，无需在Django注册，只需定义好路由path，映射controller到djangorestframework-jwt中的obtain_jwt_token即可



