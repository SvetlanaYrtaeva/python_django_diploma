from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'subcategories']

    def get_image(self, obj):
        if obj.icon:
            return {
                "src": obj.icon.url,
                "alt": obj.name
            }
        return {"src": "", "alt": ""}

    def get_subcategories(self, obj):
        children = Category.objects.filter(parent=obj, is_deleted=False, is_active=True)
        return CategorySerializer(children, many=True).data
