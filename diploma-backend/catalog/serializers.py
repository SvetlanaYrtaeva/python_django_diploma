from rest_framework import serializers
from .models import Category


class SubCategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image']

    def get_image(self, obj):
        if obj.image:
            return {
                "src": obj.image.url,
                "alt": obj.title
            }
        return {"src": "", "alt": ""}


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'title', 'image', 'subcategories']

    def get_image(self, obj):
        if obj.image:
            return {
                "src": obj.image.url,
                "alt": obj.title
            }
        return {"src": "", "alt": ""}

    def get_subcategories(self, obj):

        subs = obj.subcategories.all() if hasattr(obj, 'subcategories') else Category.objects.filter(parent=obj)

        return SubCategorySerializer(subs, many=True).data
