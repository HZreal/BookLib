from django.db import models


class BookInfo(models.Model):
    name = models.CharField(max_length=10, unique=True, verbose_name='书籍名')
    pub_date = models.DateField(null=True, verbose_name='发表日期')
    read_count = models.IntegerField(default=0, verbose_name='阅读量')
    comment_count = models.IntegerField(default=0, verbose_name='评论量')
    is_delete = models.BooleanField(default=False, verbose_name='逻辑删除')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'tb_books'        # 修改表名
        verbose_name = '书籍信息'


class PersonInfo(models.Model):
    GENDER_CHOICES = (
        (0, 'male'),
        (1, 'female')
    )
    name = models.CharField(max_length=20, verbose_name='姓名', unique=True)
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, default=0, verbose_name='性别')
    book_id = models.ForeignKey(BookInfo, on_delete=models.CASCADE, verbose_name='书籍id', db_column='book_id')
    description = models.CharField(max_length=200, null=True, verbose_name='描述')
    is_delete = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_persons'
        verbose_name = '人物信息'

    def __str__(self):
        return self.name

