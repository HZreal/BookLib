from django.urls import path, re_path
from book import viewsBasics, viewsAuth
from rest_framework.routers import SimpleRouter, DefaultRouter

from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    # path('index/', viewsBasics.IndexView.as_view()),

    # re_path('login/(float:version)/', views.LoginView.as_view()),
    # re_path(r'^login/(?P<version>[12]\.0)/$', viewsBasics.LoginView.as_view()),

    # re_path(r'^book/(?P<pk>\d+)/$', viewsBasics.BookView.as_view()),

    # re_path(r'^books/(?P<pk>\d+)/$', viewsBasics.BookDRFView.as_view()),

    # 使用ViewSet时的路由
    # re_path('books/', viewsBasics.BookViewSet.as_view({'get': 'list', 'post': 'create'})),
    # re_path(r'^book/(?P<pk>\d+)/$', viewsBasics.BookViewSet.as_view({'put': 'update'})),
    # re_path(r'^book/(?P<pk>\d+)/lastdata/$', viewsBasics.BookViewSet.as_view({'get': 'lastdata'})),

    # 使用GenericViewSet时的路由与使用ViewSet时的一样
    # re_path('books/', viewsBasics.BookGenericViewSet.as_view({'get': 'list', 'post': 'create'})),
    # re_path(r'^book/(?P<pk>\d+)/$', viewsBasics.BookGenericViewSet.as_view({'put': 'update'})),
    # re_path(r'^book/(?P<pk>\d+)/lastdata/$', viewsBasics.BookGenericViewSet.as_view({'get': 'lastdata'})),

    # 使用ModelViewSet时的路由
    # re_path('books/', viewsBasics.BookModelViewSet.as_view({'get': 'list', 'post': 'create'})),
    # re_path(r'^book/(?P<pk>\d+)/$', viewsBasics.BookModelViewSet.as_view({'put': 'update', 'get': 'retrieve', 'delete': 'destroy'})),

    path('register/', viewsAuth.register),
    # DRF自带 token auth
    path('drf-token-auth/', obtain_auth_token),
    # 基于obtain_auth_token自定义view
    path('custom-drf-token-auth/', viewsAuth.CustomDRFObtainAuthToken.as_view()),
    # 基于DRF的 jwt auth
    path('drf-jwt-auth/', obtain_jwt_token),

]

# 使用Routers来帮助我们快速实现路由信息：必须配合视图集使用
# REST framework提供了两个router
# SimpleRouter：适用于简单的五个扩展类方法路由的自动生成，无法自动生成自定义方法的路由(action装饰器 )
# router = SimpleRouter()
# register方法参数：1.资源名词复数    2.视图类(必须是视图集！！！)     3.路由别名
# router.register('books', viewsBasics.BookModelViewSet, basename='books')

# 获取生成的路由列表
# print(router.urls)
# 上述代码会形成的路由别名如下：
# ^books/$    name: book-list
# ^books/{pk}/$   name: book-detail

# 将生成的路由列表合并到urlpatterns
# urlpatterns += router.urls

# DefaultRouter继承自SimpleRouter：增加了根路径首页匹配(SimpleRouter没有)
# router2 = DefaultRouter()
