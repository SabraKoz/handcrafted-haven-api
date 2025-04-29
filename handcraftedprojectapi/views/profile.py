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
from .payment import PaymentSerializer

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    store = serializers.SerializerMethodField()
    payment = PaymentSerializer(many=True, source="payment_types")

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "store",
            "payment"
        )

    def get_store(self, obj):
        store = Store.objects.filter(owner=obj).first()
        return StoreSerializer(store).data if store else None
    
class Profile(ViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request):
        try:
            current_user = request.user

            serializer = ProfileSerializer(current_user, many=False, context={"request": request})

            return Response(serializer.data)
        
        except Exception:
            return HttpResponseServerError()
        