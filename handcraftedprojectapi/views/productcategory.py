from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from handcraftedprojectapi.models import ProductCategory

class ProductCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductCategory
        fields = (
            "id",
            "name"
        )
        depth = 1

class ProductCategories(ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        product_category = ProductCategory.objects.all()

        serializer = ProductCategorySerializer(product_category, many=True, context={"request": request})

        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        try:
            category = ProductCategory.objects.get(pk=pk)
            serializer = ProductCategorySerializer(category, context={"request": request})
            return Response(serializer.data)
        except Exception:
            return HttpResponseServerError()
