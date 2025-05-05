from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers, status
from handcraftedprojectapi.models import Order, Payment, OrderProduct, Product
from .product import ProductSerializer
import datetime

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = OrderProduct
        fields = (
            "id",
            "product"
        )
        depth = 1

class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(many=True)
    total = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    completed_on = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "payment",
            "created_on",
            "user",
            "items",
            "completed_on",
            "status",
            "total"
        )
        depth = 1

    def get_total(self, obj):
        items = OrderProduct.objects.filter(order=obj)
        return round(sum(item.product.price for item in items), 2)
    
    def get_status(self, obj):
        return "complete" if obj.payment else "incomplete"
    
    def get_completed_on(self, obj):
        if obj.payment:
            return datetime.datetime.now().strftime("%m/%d/%Y")
        return None
    
class Orders(ViewSet):

    def list(self, request):
        current_user = request.user
        orders = Order.objects.filter(user=current_user, payment__isnull=False)
        payment = self.request.query_params.get("payment", None)

        if payment is not None:
            orders = orders.filter(payment__id=payment)

        serializer = OrderSerializer(orders, many=True, context={"request": request})

        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        try:
            current_user = request.user
            order = Order.objects.get(pk=pk, user=current_user)
            serializer = OrderSerializer(order, context={"request": request})
            return Response(serializer.data)
        
        except Order.DoesNotExist:
            return Response({"message": "order does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception:
            return HttpResponseServerError()
        
    def update(self, request, pk=None):
        current_user = request.user
        order = Order.objects.get(pk=pk, user=current_user)
        payment_type = Payment.objects.get(pk=request.data["payment"])
        order.payment = payment_type

        order.save()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
    @action(methods=["get", "post", "delete"], detail=False)
    def cart(self, request):

        current_user = request.user

        if request.method == "GET":
            try:
                open_order = Order.objects.get(user=current_user, payment=None)
                order_items = OrderProduct.objects.filter(order=open_order)
                order_items = OrderItemSerializer(order_items, many=True, context={"request": request})

                cart = {}
                cart["order"] = OrderSerializer(open_order, many=False, context={"request": request}).data
                cart["order"]["size"] = len(order_items.data)

            except Order.DoesNotExist:
                final = {}
                return Response(final)
            
            return Response(cart["order"])

        if request.method == "POST":
            try:
                open_order = Order.objects.get(user=current_user, payment=None)
            
            except Order.DoesNotExist:
                open_order = Order()
                open_order.created_on = datetime.datetime.now()
                open_order.user = current_user
                open_order.save()

            item = OrderProduct()
            item.product = Product.objects.get(pk=request.data["product"])
            item.order = open_order
            item.save()

            item_json = OrderItemSerializer(item, many=False, context={"request": request})

            return Response(item_json.data)
        
        if request.method == "DELETE":
            try:
                open_order = Order.objects.get(user=current_user, payment=None)
                order_items = OrderProduct.objects.filter(order=open_order)
                order_items.delete()
                open_order.delete()

            except Order.DoesNotExist:
                return Response({}, status=status.HTTP_204_NO_CONTENT)
        
