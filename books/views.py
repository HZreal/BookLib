import json

from django.views import View
from books.models import BookInfo, PersonInfo
from django import http
# 设计接口：
#     请求方式
#     请求路径
#     请求参数
#     返回结果



class BooksView(View):
    def get(self, request):
        # 查询所有图书
        books = BookInfo.objects.all()
        book_list = [{'id': book.id, 'name': book.name, 'pub_date': book.pub_date, 'read_count': book.read_count, 'comment_count': book.comment_count} for book in books]
        # 返回json，列表无法直接转json，需设置safe=False
        return http.JsonResponse(book_list, safe=False)

    def post(self, request):
        # 获取前端数据
        json_data = request.body.decode()
        data = json.loads(json_data)
        name = data.get('name')
        pub_date = data.get('pub_date')
        read_count = data.get('read_count')
        comment_count = data.get('comment_count')

        # 验证数据...
        if not all([name, pub_date, read_count, comment_count]):
            return http.JsonResponse({'error': '数据有误'}, status=400)
        if pub_date is None:
            return http.JsonResponse({'error': '数据有误'}, status=400)

        # 保存数据
        book = BookInfo.objects.create(name=name, pub_date=pub_date, read_count=read_count, comment_count=comment_count)

        # 返回结果
        return http.JsonResponse({'id': book.id, 'name': book.name, 'pub_date': book.pub_date, 'read_count': book.read_count, 'comment_count': book.comment_count})


class BookView(View):
    def get(self, request, pk):
        try:
            book = BookInfo.objects.get(id=pk)
        except Exception:
            return http.JsonResponse({'error': '错误'})

        return http.JsonResponse({'id': book.id, 'name': book.name, 'pub_date': book.pub_date, 'read_count': book.read_count, 'comment_count': book.comment_count})


    def put(self, request, pk):
        # 获取前端数据
        json_data = request.body.decode()
        data = json.loads(json_data)
        name = data.get('name')
        pub_date = data.get('pub_date')
        read_count = data.get('read_count')
        comment_count = data.get('comment_count')

        # 验证数据...
        if not all([name, pub_date, read_count, comment_count]):
            return http.JsonResponse({'error': '数据有误'}, status=400)
        if pub_date is None:
            return http.JsonResponse({'error': '数据有误'}, status=400)

        # 更新数据
        try:
            book = BookInfo.objects.get(id=pk)
        except Exception:
            return
        book.name = name
        book.pub_date = pub_date
        book.read_count = read_count
        book.comment_count = comment_count
        book.save()

        # 返回结果
        return http.JsonResponse({'id': book.id, 'name': book.name, 'pub_date': book.pub_date, 'read_count': book.read_count, 'comment_count': book.comment_count})

    def delete(self, request, pk):
        try:
            book = BookInfo.objects.get(id=pk)
        except Exception:
            return http.JsonResponse({'error': '错误'})
        book.is_delete = True
        book.save()
        return http.JsonResponse({'msg': 'OK'})


