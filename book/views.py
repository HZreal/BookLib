from django import http
from django.http import JsonResponse, HttpResponse
import json
from django.views import View
from rest_framework.decorators import action

from book.models import BookInfo
from book.serializer import BookInfoSerializer, PersonInfoSerializer
from datetime import datetime
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet, ViewSet, ModelViewSet, ReadOnlyModelViewSet
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.views import APIView, exception_handler
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle
from rest_framework.pagination import PageNumberPagination



class IndexView(View):
    def get(self, request):
        # 前后端不分离，后端通过模板渲染
        # return render(request, 'index.html', context={'name': 'huang'})

        # 前后端分离：数据由json传给前端，不再关心渲染
        return http.JsonResponse({'name': 'huang'})


class LoginView(View):
    def get(self, request, version):
        username = request.GET.get('username')
        if version == 1.0:        # 版本号
            pass
        else:
            pass
        return http.JsonResponse({'message': 'OK'})



# DRF  传入视图的request对象不再是Django默认的HttpRequest对象，而是REST framework提供的扩展了HttpRequest类的Request类的对象
# REST framework 提供了Parser解析器，在接收到请求后会自动根据Content-Type指明的请求数据类型（如JSON、表单等）将请求数据进行parse解析，解析为类字典对象保存到Request对象中
# Request对象的数据是自动根据前端发送数据的格式进行解析之后的结果
# request.data 返回解析之后的请求体数据
# request.query_params与Django标准的request.GET相同，只是更换了更正确的名称而已
# DRF  提供了一个响应类Response，使用该类构造响应对象时，响应的具体数据内容会被转换（render渲染）成符合前端需求的类型
# data数据不要是render处理之后的数据，只需传递python的内建类型数据即可，REST framework会使用renderer渲染器处理data
# data不能是复杂结构的数据，如Django的模型类对象，对于这样的数据我们可以使用Serializer序列化器序列化处理后（转为了Python字典类型）再传递给data参数
class BookView(View):
    def get(self, request, pk):
        books = BookInfo.objects.all()
        s = BookInfoSerializer(books, many=True)     # 返回多个对象时，设置many=True

        return http.JsonResponse(s.data, safe=False)

    def post(self, request):
        data = json.loads(request.body.decode())

        # 验证数据
        s = BookInfoSerializer(data=data)
        # 验证方法：自动进行字段参数验证
        # s.is_valid()
        s.is_valid(raise_exception=True)    # 检测到错误自动抛出异常
        error_dict = s.errors    # 返回字段的错误提示信息，为字典，没有错误即空字典
        # 上述指定raise_exception=True则不需if判断
        # if s.errors is not None:
        #     return

        # 获取验证后的数据
        data = s.validated_data
        # 保存数据
        s.save()
        # 返回结果
        return http.JsonResponse(s.data)


class BookDRFView(View):
    def put(self, request, pk):
        # 获取前端数据
        data = json.loads(request.body.decode())
        name = data.get('name')
        pub_date = data.get('pub_date')
        read_count = data.get('read_count')
        comment_count = data.get('comment_count')

        # 验证数据...
        # if not all([name, pub_date, read_count, comment_count]):
        #     return http.JsonResponse({'error': '数据有误'}, status=400)
        # if pub_date is None:
        #     return http.JsonResponse({'error': '数据有误'}, status=400)
        try:
            book = BookInfo.objects.get(id=pk)
        except Exception:
            return http.JsonResponse({'error': '错误'}, status=400)
        s = BookInfoSerializer(book, data=data)
        s.is_valid()

        # 更新数据
        s.save()
        # try:
        #     book = BookInfo.objects.get(id=pk)
        # except Exception:
        #     return http.JsonResponse({})
        # book.name = name
        # book.pub_date = pub_date
        # book.read_count = read_count
        # book.comment_count = comment_count
        # book.save()

        # 返回结果
        # return http.JsonResponse({'id': book.id, 'name': book.name, 'pub_date': book.pub_date, 'read_count': book.read_count, 'comment_count': book.comment_count})
        return http.JsonResponse(s.data)

    def delete(self, request, pk):
        try:
            book = BookInfo.objects.get(id=pk)
        except Exception:
            return http.JsonResponse({'error': '错误'})
        book.is_delete = True
        book.save()
        return http.JsonResponse({'msg': 'OK'})


# 两个基类
# 一、APIView   继承自Django的View类
# APIView与View的不同之处在于：
#     传入到视图方法中的是REST framework的Request对象，而不是Django的HttpRequeset对象；
#     视图方法可以返回REST framework的Response对象，视图会为响应数据设置（render）符合前端要求的格式；
#     任何APIException异常都会被捕获到，并且处理成合适的响应信息；
#     在进行dispatch()分发前，会对请求进行身份认证、权限检查、流量控制
# 支持定义的属性
#     authentication_classes 列表或元祖，身份认证类
#     permissoin_classes 列表或元祖，权限检查类
#     throttle_classes 列表或元祖，流量控制类
class BookAPIView(APIView):
    def get(self, request):
        # 获取查询字符串
        query_params = request.query_params

        books = BookInfo.objects.all()

        s = BookInfoSerializer(books, many=True)

        return Response(s.data)

    def post(self, request):
        # 获取
        data = request.data
        # 验证
        s = BookInfoSerializer(data=data)
        s.is_valid()
        # 保存
        s.save()
        # 返回
        return Response(s.data)

    def put(self, request, pk):
        # 获取
        data = request.data
        # 验证
        try:
            book = BookInfo.objects.get(id=pk)
        except Exception:
            return JsonResponse({'error': '有误'})
        s = BookInfoSerializer(book, data=data)
        s.is_valid()
        # 更新
        s.save()
        # 返回
        return Response(s.data)


# 二、GenericAPIView    继承自APIView，增加了对于列表视图和详情视图可能用到的通用支持方法。通常使用时，可搭配一个或多个Mixin扩展类
# 支持定义的属性：
#     列表视图与详情视图通用：
#         queryset 列表视图的查询集
#         serializer_class 视图使用的序列化器
#     列表视图使用：
#         pagination_class 分页控制类
#         filter_backends 过滤控制后端
#     详情页视图使用：
#         lookup_field 查询单一数据库对象时使用的条件字段，默认为'pk'
#         lookup_url_kwarg 查询单一数据时URL中的参数关键字名称，默认与look_field相同
# get_queryset(self)   返回视图使用的查询集，是列表视图与详情视图获取数据的基础，默认返回queryset属性，可以重写
# get_serializer_class(self)    返回序列化器类，默认返回serializer_class，可以重写
# get_serializer(self, args, *kwargs)    返回序列化器对象，被其他视图或扩展类使用，如果我们在视图中想要获取序列化器对象，可以直接调用此方法
# get_object(self)   返回详情视图所需的模型类数据对象，默认使用lookup_field参数来过滤queryset。 在试图中可以调用该方法获取详情信息的模型类对象
class BookGenericAPIView(GenericAPIView):
    # 指定当前视图类使用的查询集数据
    queryset = BookInfo.objects.all()
    # 指定当前视图类使用的序列化器
    serializer_class = BookInfoSerializer

    def get_queryset(self):
        # 获取查询集
        return self.queryset

    def get_object(self):          # 会根据lookup_field(默认为pk)指定的字段值返回单一对象
        # 获取单一数据对象
        for instance in self.queryset:
            if instance.id == 1:
                return instance

    def get_serializer_class(self):
        # 获取指定序列化器类
        return self.serializer_class

    def get_serializer(self, data=None):
        # 获取序列化器对象
        serializer = self.get_serializer_class()
        return serializer(data=data)

    def get(self, request):
        # 获取查询集数据
        books = self.get_queryset()
        # 使用指定序列化器
        s = self.get_serializer(books, many=True)
        # 序列化结果返回
        return Response(s.data)

    def post(self, request):
        # 获取前端数据
        data = request.data
        # 使用指定序列化器
        s = self.get_serializer(data=data)
        # 验证
        s.is_valid()
        # 保存
        s.save()
        # 返回
        return Response(s.data)

    def put(self, request, pk):
        # 获取前端数据
        data = request.data
        # 验证数据
        try:
            # 从查询机中获取单一数据对象
            book = self.get_object()       # 自动根据pk值获取模型对象
        except:
            return JsonResponse({'error': '有误'})
        # 更新数据
        s = self.get_serializer(book, data=data)
        s.is_valid()
        # 返回数据
        return Response(s.data)



# 五个扩展类：继承自object
# ListModelMixin列表视图扩展类，提供list(request, *args, **kwargs)方法快速实现列表视图，返回200状态码。  该Mixin的list方法会对数据进行过滤和分页(若指定了过滤分页)
# CreateModelMixin创建视图扩展类，提供create(request, *args, **kwargs)方法快速实现创建资源的视图，成功返回201状态码。如果序列化器对前端发送的数据验证失败，返回400错误
# RetrieveModelMixin详情视图扩展类，提供retrieve(request, *args, **kwargs)方法，可以快速实现返回一个存在的数据对象。如果存在，返回200， 否则返回404
# UpdateModelMixin更新视图扩展类，提供update(request, *args, **kwargs)方法，可以快速实现更新一个存在的数据对象。同时也提供partial_update(request, *args, **kwargs)方法，可以实现局部更新。成功返回200，序列化器校验数据失败时，返回400错误
# DestroyModelMixin删除视图扩展类，提供destroy(request, *args, **kwargs)方法，可以快速实现删除一个存在的数据对象。成功返回204，不存在返回404
class BookGenericCreateModelListModel(GenericAPIView, CreateModelMixin, ListModelMixin):    # 也即是继承ListCreateAPIView
    queryset = BookInfo.objects.all()
    serializer_class = BookInfoSerializer

    def get(self, request):
        return self.list(request)        # list方法包含了Response返回
    def post(self, request):
        return self.create(request)        # create方法包含了返回

class BookGenericUpdateModelDestroyModel(GenericAPIView, UpdateModelMixin, DestroyModelMixin):
    queryset = BookInfo.objects.all()
    serializer_class = BookInfoSerializer
    def put(self, request, pk):
        return self.update(request, pk)
    def delete(self, request, pk):
        return self.destroy(request, pk)


# 几个可用子类视图：
# CreateAPIView  提供post方法   继承自： GenericAPIView、CreateModelMixin
# ListAPIView提供get方法   继承自：GenericAPIView、ListModelMixin
# ListCreateAPIView  继承自：GenericAPIView, CreateModelMixin, ListModelMixin  内部提供了get()、post()方法
# RetrieveAPIView提供get方法   继承自: GenericAPIView、RetrieveModelMixin
# DestroyAPIView提供delete方法   继承自：GenericAPIView、DestroyModelMixin
# UpdateAPIView提供put和patch方法   继承自：GenericAPIView、UpdateModelMixin
# RetrieveUpdateAPIView提供get、put、patch方法   继承自： GenericAPIView、RetrieveModelMixin、UpdateModelMixin
# RetrieveDestroyAPIView 继承自： GenericAPIView、RetrieveModelMixin、DestroyModelMixin
# RetrieveUpdateDestroyAPIView提供get、put、patch、delete方法   继承自：GenericAPIView、RetrieveModelMixin、UpdateModelMixin、DestroyModelMixin
class BookListCreateAPIView(ListCreateAPIView):
    queryset = BookInfo.objects.all()
    serializer_class = BookInfoSerializer
    # 内部实现了get()、post()

class BookRetrieveUpdateDestory(RetrieveUpdateDestroyAPIView):
    queryset = BookInfo.objects.all()
    serializer_class = BookInfoSerializer
    # 内部实现了get()  put()  patch()  delete()


# 视图集(1.路由匹配规则发生变化   2.视图中定义方法不再按照请求方式进行)
# 可以将一系列逻辑相关的动作放到一个类中： 不再实现get()、post()等方法，而是实现动作 action 如 list() 、create() 等
# 两个基本视图集：
# ViewSet 继承自APIView
# GenericViewSet 继承自GenericAPIView
class BookViewSet(ViewSet):
    def list(self, request):
        books = BookInfo.objects.all()
        s = BookInfoSerializer(books, many=True)
        return Response(s.data)

    def create(self, request):
        data = request.data
        s = BookInfoSerializer(data=data)
        s.is_valid()
        s.save()
        return Response(s.data)

    def update(self, request, pk):
        data = request.data
        try:
            book = BookInfo.objects.get(id=pk)
        except:
            return JsonResponse({'error': '信息有误'})
        s = BookInfoSerializer(book, data=data)
        s.is_valid()
        s.save()
        return Response(s.data)

    # 自定义方法
    def lastdata(self, request, pk):
        book = BookInfo.objects.get(id=pk)
        s = BookInfoSerializer(book)
        return Response(s.data)


class BookGenericViewSet(GenericViewSet):
    queryset = BookInfo.objects.all()
    serializer_class = BookInfoSerializer

    def list(self, request):
        books = self.get_queryset()
        s = self.get_serializer(books, many=True)
        return Response(s.data)

    def create(self, request):
        data = request.data
        s = BookInfoSerializer(data=data)
        s.is_valid()
        s.save()
        return Response(s.data)



# 两个拓展视图集：
# ModelViewSet  继承自GenericAPIView和五个扩展类   增删改查均可
# ReadOnlyModelViewSet 继承自GenericAPIView、ListModelMixin、RetrieveModelMixin  获取多个/单一数据对象(只读)

class BookModelViewSet(ModelViewSet):
    queryset = BookInfo.objects.all()
    # serializer_class = BookInfoSerializer        # 下面自定义了get_serializer_class

    # ModelViewSet提供了以下功能方法
    # list() 提供一组数据           路由：'get': 'list'
    # retrieve() 提供单个数据             'get': 'retrieve'
    # create() 创建数据                   'post': 'create'
    # update() 保存数据                   'put': 'update'
    # destroy() 删除数据                  'delete': 'destroy'

    # 自定义get_serializer_class返回序列化器类
    def get_serializer_class(self):
        if self.action == 'lastdata':     # 根据请求方法使用不同的序列化器
            return BookInfoSerializer
        else:
            return PersonInfoSerializer

    # 自定义方法
    # methods用于请求方式与视图的绑定，detail=False表示不使用p生成路由   detail=True表示生成带pk匹配的路由规则
    @action(methods=['get'], detail=True)         # detail=True时生成的路由：^book/(?P<pk>\d+)/lastdata/$      detail=False时生成的路由：^book/lastdata/$
    def lastdata(self, request, pk):
        print(self.action)       # 返回的是请求方法名lastdata
        book = self.get_object()
        s = self.get_serializer(book)
        return Response(s.data)


class BooksAPIView(APIView):
    """
    查询所有图书、增加图书
    """
    def get(self, request):
        """
        查询所有图书
        路由：GET /books/
        """
        queryset = BookInfo.objects.all()
        book_list = []
        for book in queryset:
            book_list.append({
                'id': book.id,
                'btitle': book.btitle,
                'bpub_date': book.bpub_date,
                'bread': book.bread,
                'bcomment': book.bcomment,
                'image': book.image.url if book.image else ''
            })
        return JsonResponse(book_list, safe=False)

    def post(self, request):
        """
        新增图书
        路由：POST /books/
        """
        json_bytes = request.body
        json_str = json_bytes.decode()
        book_dict = json.loads(json_str)

        # 此处详细的校验参数省略

        book = BookInfo.objects.create(
            btitle=book_dict.get('btitle'),
            bpub_date=datetime.strptime(book_dict.get('bpub_date'), '%Y-%m-%d').date()
        )

        return JsonResponse({
            'id': book.id,
            'btitle': book.btitle,
            'bpub_date': book.bpub_date,
            'bread': book.bread,
            'bcomment': book.bcomment,
            'image': book.image.url if book.image else ''
        }, status=201)


class BookAPIView(APIView):
    def get(self, request, pk):
        """
        获取单个图书信息
        路由： GET  /books/<pk>/
        """
        try:
            book = BookInfo.objects.get(pk=pk)
        except BookInfo.DoesNotExist:
            return HttpResponse(status=404)

        return JsonResponse({
            'id': book.id,
            'btitle': book.btitle,
            'bpub_date': book.bpub_date,
            'bread': book.bread,
            'bcomment': book.bcomment,
            'image': book.image.url if book.image else ''
        })

    def put(self, request, pk):
        """
        修改图书信息
        路由： PUT  /books/<pk>
        """
        try:
            book = BookInfo.objects.get(pk=pk)
        except BookInfo.DoesNotExist:
            return HttpResponse(status=404)

        json_bytes = request.body
        json_str = json_bytes.decode()
        book_dict = json.loads(json_str)

        # 此处详细的校验参数省略

        book.btitle = book_dict.get('btitle')
        book.bpub_date = datetime.strptime(book_dict.get('bpub_date'), '%Y-%m-%d').date()
        book.save()

        return JsonResponse({
            'id': book.id,
            'btitle': book.btitle,
            'bpub_date': book.bpub_date,
            'bread': book.bread,
            'bcomment': book.bcomment,
            'image': book.image.url if book.image else ''
        })

    def delete(self, request, pk):
        """
        删除图书
        路由： DELETE /books/<pk>/
        """
        try:
            book = BookInfo.objects.get(pk=pk)
        except BookInfo.DoesNotExist:
            return HttpResponse(status=404)

        book.delete()

        return HttpResponse(status=204)


# 认证
class ExampleView1(APIView):
    # 局部配置，仅对本DRF视图有效
    authentication_classes = (SessionAuthentication, BasicAuthentication)


# 权限
# 权限控制可以限制用户对于视图的访问和对于具体数据对象的访问。
# 在执行视图的dispatch()方法前，会先进行视图访问权限的判断
# 在通过get_object()获取具体对象时，会进行对象访问权限的判断
class ExampleView2(APIView):
    permission_classes = (IsAuthenticated,)

# 认证和权限一般是一起使用，分开使用没有什么意义



# 限流
# 可以对接口访问的频次进行限制，以减轻服务器压力
class ExampleView3(APIView):
    # 局部用户限流
    throttle_classes = (UserRateThrottle, AnonRateThrottle, ScopedRateThrottle, )

class ContactListView(APIView):
    throttle_scope = 'contacts'     # 指定限流的名称，进入此试图前会根据contacts对应的限流次数进行控制是否可进入此视图
    ...

class ContactDetailView(APIView):
    throttle_scope = 'contacts'     # 指定限流的名称
    ...

class UploadView(APIView):
    throttle_scope = 'uploads'       # 指定限流的名称
    ...



# 过滤
class BookListView1(ListAPIView):
    queryset = BookInfo.objects.all()
    serializer_class = BookInfoSerializer

    # 全局配置已注册django_filters，并指定DjangoFilterBackend
    # 过滤字段
    filter_fields = ('name', 'read_count')     # 前端查询字符串参数为对应字段=值  可搜索过滤



# 排序
class BookListView2(ListAPIView):
    queryset = BookInfo.objects.all()
    serializer_class = BookInfoSerializer

    # 指定排序后端
    filter_backends = [OrderingFilter]
    # 排序字段
    ordering_fields = ('id', 'read_count', 'pub_date')     # 前端查询字符串参数为ordering=排序字段   按该字段进行排序

    # DRF搜索
    # filter_backends = [SearchFilter]       # 内含模板
    # search_fields = ()



# 分页
# 自定义分页器，继承自PageNumberPagination
class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10                           # 后端指定的每页的数量
    page_query_param = 'page'                # 前端查询字符串参数page指定的页号，如http://api.example.org/accounts/?page=4
    page_size_query_param = 'page_size'      # 前端通过查询字符串参数page_size指定每页数量，如http://api.example.org/accounts/?page=4&page_size=15
    max_page_size = 20                       # 前端最多能指定每页返回的数量，若前端指定每页21条数据，依然每页只返回20条

class BookModelView(ModelViewSet):
    queryset = BookInfo.objects.all().order_by('id')
    serializer_class = BookInfoSerializer

    # 指定分页器类
    pagination_class = CustomPageNumberPagination
    # 请求时，默认调用了list方法中的分页功能

# LimitOffsetPagination分页器和PageNumberPagination使用方法一致，仅仅访问参数不同：http://api.example.org/books/?limit=100&offset=400
# default_limit 默认限制，默认值与PAGE_SIZE设置一直
# limit_query_param limit参数名，默认'limit'
# offset_query_param offset参数名，默认'offset'
# max_limit 最大limit限制，默认None



# 异常处理：
# DRF定义的异常有下，对数据库异常未做定义：
# APIException 所有异常的父类
# ParseError 解析错误
# AuthenticationFailed 认证失败
# NotAuthenticated 尚未认证
# PermissionDenied 权限决绝
# NotFound 未找到
# MethodNotAllowed 请求方式不支持
# NotAcceptable 要获取的数据格式不支持
# Throttled 超过限流次数
# ValidationError 校验失败

# DRF默认对数据库异常DatabaseError不做处理，需自定义异常处理函数
def custom_exception_handler(exc, context):
    # 先调用REST framework默认的异常处理方法获得标准错误响应对象
    response = exception_handler(exc, context)

    # 在此处补充自定义的异常处理
    if response is not None:
        response.data['status_code'] = response.status_code
    return response


# 补充上处理关于数据库的异常：可以写在一个单独utils.py文件中，并且在配置文件中设置此异常处理
from rest_framework.views import exception_handler
from rest_framework import status
from django.db import DatabaseError
def custom_db_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        view = context['view']
        if isinstance(exc, DatabaseError):
            print('[%s]: %s' % (view, exc))
            response = Response({'detail': '服务器内部错误'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

    return response

class DbErrorHandleModelView(ModelViewSet):
    serializer_class = BookInfoSerializer
    def get_queryset(self):
        try:
            queryset = BookInfo.objects.all()
        except DatabaseError:
            raise DatabaseError     # 当捕获到数据库异常时，DRF默认不处理，抛出错误，而上述已自定义数据库异常处理，则会去调用异常处理函数返回错误信息而不报错
        return queryset


# 接口文档
# 1.安装依赖pip install coreapi
# 2.在总路由中添加接口文档路径    re_path(r'^docs/', include_docs_urls(title='My API title'))
# 3.文档描述说明的定义位置
# 说明：
# 1）视图集ViewSet中的retrieve名称，在接口文档网站中叫做read
# 2）参数的Description需要在模型类或序列化器类的字段中以help_text选项定义

# 单一方法的视图，可直接使用类视图的文档字符串，如
class BookDocApiView(ListAPIView):
    """
    返回所有图书信息.
    """

# 包含多个方法的视图，在类视图的文档字符串中，分开方法定义，如
class BookListCreateView(ListCreateAPIView):
    """
    get:
    返回所有图书信息.

    post:
    新建图书.
    """

# 对于视图集ViewSet，仍在类视图的文档字符串中分开定义，但是应使用action名称区分，如
class BookInfoViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    list:
    返回图书列表数据

    retrieve:
    返回图书详情数据

    latest:
    返回最新的图书数据

    read:
    修改图书的阅读量
    """

