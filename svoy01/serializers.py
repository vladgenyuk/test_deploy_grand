from rest_framework.fields import CharField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, Serializer
from .models import product, PostImage


class AllProductSerializer(ModelSerializer):
    class Meta:
        model = product
        exclude = ['photo']


class PostImageSerializer(ModelSerializer):
    class Meta:
        model = PostImage
        fields = "__all__"


class DetailProductSerializer(ModelSerializer):
    postimages = PostImageSerializer(many=True)

    class Meta:
        model = product
        fields = "__all__"
