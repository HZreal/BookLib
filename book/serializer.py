from book.models import BookInfo, PersonInfo
from rest_framework import serializers


# 定义嵌套序列化器，需在被嵌套的之前
class PersonInfoSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=20, label='姓名')
    description = serializers.CharField(max_length=200, label='描述')

    # book_id = serializers.PrimaryKeyRelatedField()
    # book_id = serializers.StringRelatedField()


# 定义一般形式序列化器：自定义序列化器需要将好多字段在序列化器中定义
class BookInfoSerializer1(serializers.Serializer):
    # write_only表示字段只用于反序列化，不用于序列化
    name = serializers.CharField(max_length=10, min_length=5, label='书籍名', write_only=True, help_text='书名')
    # read_only表示字段只用于序列化，不用于反序列化，即反序列化不验证保存
    pub_date = serializers.DateField(label='发表日期', read_only=True)
    read_count = serializers.IntegerField(max_value=100, min_value=5, required=False, label='阅读量')
    comment_count = serializers.IntegerField(default=0, required=False, label='评论量')
    is_delete = serializers.BooleanField(required=False, label='逻辑删除')

    # 关联对象数据的序列化三种方式：
    # 1.返回人物模型类的id值
    # personinfo_set = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    # 2.返回关联人物模型类的__str__方法值
    # personinfo_set = serializers.StringRelatedField(read_only=True, many=True)

    # 3.嵌套序列化器，定义需要在此之前
    personinfo_set = PersonInfoSerializer(many=True)

    # 单一字段验证
    def validated_name(self, value):
        if value == 'python':
            raise serializers.ValidationError('书名不能是python')
        return value

    # 多个字段验证
    def validate(self, attrs):
        if attrs['read_count'] > attrs['comment_count']:
            raise serializers.ValidationError('阅读量大于评论的错误')
        return attrs

    # 保存数据
    def create(self, validated_data):
        book = BookInfo.objects.create(**validated_data)
        return book

    # 更新数据
    def update(self, instance, validated_data):
        instance.name = validated_data['name']
        instance.save()
        return instance


# 模型类序列化器：直接继承序列化器类Serializers
class BookInfoSerializer(serializers.ModelSerializer):
    # 显示修改指明字段的选项参数
    # read_count = serializers.IntegerField(max_value=100, min_value=5, required=False, label='阅读量')

    # 增加的新字段(必须在下面field中声明！)
    sms_code = serializers.CharField(max_length=6, min_length=6)

    class Meta():
        # model 指明参照哪个模型类，则自动生成其系列字段
        model = BookInfo

        # fields 指明为模型类的哪些字段生成
        # fields = ('id', 'name', 'pub_date', sms_code)
        field = '__all__'  # 声明sms_code
        # 可以明确排除掉哪些字段
        exclude = ('image',)

        # 指明只读字段，即仅用于序列化输出的字段
        read_only_fields = ('id', 'read_count', 'comment_count')

        # 为ModelSerializer添加或修改原有的选项参数
        extra_kwargs = {
            'read_count': {'min_value': 0, 'required': True},
            'comment_count': {'min_value': 0, 'required': True},

        }

    # 验证
    # 若某字段有unique值设定，则自动生成该字段对应的校验方法

    def validate_name(self, date):
        pass

    def validate(self, attrs):
        pass

    # 内部封装了create, update方法


