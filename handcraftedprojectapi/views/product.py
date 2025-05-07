import uuid
import base64
from django.core.files.base import ContentFile
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from handcraftedprojectapi.models import Product, ProductCategory, ProductFavorite, ProductReview, Store

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "price",
            "description",
            "quantity",
            "image_path",
            "number_sold",
            "category",
            "store",
            "user"
        )
        depth = 2

class ProductDetailSerializer(ProductSerializer):
    is_favorited = serializers.SerializerMethodField()
    available_quantity = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + ("is_favorited", "reviews", "favorites", "available_quantity")
    
    def get_is_favorited(self, obj):
        request = self.context.get("request")

        current_user = request.user

        is_it_favorited = ProductFavorite.objects.filter(user=current_user, product=obj.pk).exists()

        return is_it_favorited
    
    def get_available_quantity(self, obj):
        return max(obj.quantity - obj.number_sold, 0)


class Products(ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):

        products = Product.objects.all()

        category =  self.request.query_params.get("category", None)

        if category is not None:
            products = products.filter(category__id=category)

        sort_order = request.query_params.get("sort", None)
        if sort_order == "low":
            products = products.order_by("price")
        elif sort_order == "high":
            products = products.order_by("-price")

        serializer = ProductSerializer(products, many=True, context={"request": request})

        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):

        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductDetailSerializer(product, context={"request": request})
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"message": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return HttpResponseServerError()
        
    def create(self, request):

        data = request.data.copy()
        data["image_path"] = None

        serializer = ProductSerializer(data=data, context={"request": request})

        errors = {}
        if not serializer.is_valid():
            errors = serializer.errors.copy()

        if "category" in data and data["category"] == "0":
            errors["category"] = ["Select a category"]

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_product = Product()
        new_product.name = request.data["name"]
        new_product.price = request.data["price"]
        new_product.description = request.data["description"]
        new_product.quantity = request.data["quantity"]
        new_product.store = Store.objects.get(owner=request.user)

        new_product.user = request.user

        try:
            product_category = ProductCategory.objects.get(pk=request.data["category"])
        except ProductCategory.DoesNotExist:
            return Response({"category": "Please select a category"}, status=status.HTTP_400_BAD_REQUEST)
        
        new_product.category = product_category

        if "image_path" in request.data:
            format, imgstr = request.data["image_path"].split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{new_product.id}-{request.data["name"]}-{uuid.uuid4()}.{ext}',)
            new_product.image_path = data

        new_product.save()

        result_serializer = ProductSerializer(new_product, context={"request": request})

        return Response(result_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        product = Product.objects.get(pk=pk)
        product.name = request.data["name"]
        product.price = request.data["price"]
        product.description = request.data["description"]
        product.quantity = request.data["quantity"]

        product.user = request.user

        product_category = ProductCategory.objects.get(pk=request.data["category"])
        product.category = product_category

        if "image_path" in request.data:
            format, imgstr = request.data["image_path"].split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'{product.id}-{request.data["name"]}-{uuid.uuid4()}.{ext}',)

            product.image_path = data

        product.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, pk=None):

        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        except Product.DoesNotExist:
            return Response({"message": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
    @action(methods=["post", "delete"], detail=True)
    def favorite(self, request, pk=None):
        current_user = request.user
        product = Product.objects.get(pk=pk)

        if request.method == "POST":
            product_favorite = ProductFavorite()
            product_favorite.user = current_user
            product_favorite.product = product

            product_favorite.save()

            return Response(None, status=status.HTTP_201_CREATED)
        
        if request.method == "DELETE":
            try:
                product_favorite = ProductFavorite.objects.get(user=current_user, product=pk)
                product_favorite.delete()

                return Response({}, status=status.HTTP_204_NO_CONTENT)
            
            except ProductFavorite.DoesNotExist:
                return Response({"message": "ProductFavorite does not exist"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @action(methods=["get"], detail=False)
    def favorited(self, request):
        current_user = request.user

        if request.method == "GET":
            try:
                favorited_products = Product.objects.filter(favorites__user=current_user)
                json_favorites = ProductSerializer(favorited_products, many=True, context={"request": request})

                return Response(json_favorites.data, status=status.HTTP_200_OK)
            
            except Exception:
                return HttpResponseServerError()
            
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @action(methods=["post", "delete"], detail=True)
    def review(self, request, pk=None):
        current_user = request.user
        product = Product.objects.get(pk=pk)

        if request.method == "POST":
            review_text = request.data["review"]

            try:
                product_review = ProductReview.objects.get(user=current_user, product=product)
                product_review.review = review_text
                product_review.save()

                return Response({"message": "review updated"}, status=status.HTTP_200_OK)
            
            except ProductReview.DoesNotExist:
                ProductReview.objects.create(user=current_user, product=product, review=review_text)

                return Response({"message": "review added"}, status=status.HTTP_201_CREATED)
            
        if request.method == "DELETE":
            try:
                product_review = ProductReview.objects.get(user=current_user, product=product)
                product_review.delete()
                return Response({"message": "review deleted"}, status=status.HTTP_200_OK)
            
            except ProductReview.DoesNotExist:
                return Response({"Review not found"}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    