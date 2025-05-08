from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from handcraftedprojectapi.models import Store
from .product import ProductSerializer

class StoreSerializer(serializers.ModelSerializer):
    store_products = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = (
            "id",
            "name",
            "description",
            "owner",
            "size",
            "store_products",
            "owner_name"
        )
        depth = 1

    def get_store_products(self, obj):
        products = obj.owner.products.all()
        return ProductSerializer(products, many=True).data
    
    def get_size(self, obj):
        product_count = obj.owner.products.count()
        return product_count
    
    def get_owner_name(self, obj):
        user = obj.owner
        first_name = user.first_name if user.first_name else ""
        last_name = user.last_name if user.last_name else ""
        if first_name == "" and last_name == "":
            return user.username
        
        return f"{first_name} {last_name}".strip()
    
class Stores(ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True, context={"request": request})
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        try:
            store = Store.objects.get(pk=pk)
            serializer = StoreSerializer(store, many=False, context={"request": request})
            return Response(serializer.data)
        except Store.DoesNotExist:
            return Response({"message": "Store does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
    def create(self, request):
        current_user = request.user

        if Store.objects.filter(owner=current_user).exists():
            return Response({"message": "store already exists for this user"}, status=status.HTTP_409_CONFLICT)
        
        new_store = Store()
        new_store.name = request.data["name"]
        new_store.description = request.data["description"]
        new_store.owner = current_user

        new_store.save()

        serializer = StoreSerializer(new_store, context={"request": request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        store = Store.objects.get(pk=pk)
        store.name = request.data["name"]
        store.description = request.data["description"]
        
        user = request.user
        store.owner = user

        store.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
