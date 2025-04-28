import datetime
from django.http import HttpResponseServerError
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework import serializers, status
from handcraftedprojectapi.models import Order, OrderProduct, Product, Store, ProductFavorite
from .product import ProductSerializer
from .order import OrderSerializer
from .store import StoreSerializer

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email"
        )
        depth = 1

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    store = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            "id",
            "url",
            "user",
            "payment",
            "store"
        )
        depth = 1

    def get_store(self, obj):
        try:
            store = Store.objects.filter(owner=obj).first()
            if store:
                return StoreSerializer(store).data
            return None
        
        except Exception:
            return Response({"message": "error in getting store"}, status=status.HTTP_404_NOT_FOUND)

class Profile(ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        try:
            print(f"request.auth = {request.auth}")
            print(f"request.user = {request.user}")
            print(f"is authenticated? {request.user.is_authenticated}")

            current_user = request.user

            if current_user.is_authenticated:
                return Response({"message": "User is not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

            serializer = ProfileSerializer(current_user, many=False, context={"request": request})

            return Response(serializer.data)
        
        except Exception:
            return HttpResponseServerError()
        
    
