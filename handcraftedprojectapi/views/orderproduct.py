from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from handcraftedprojectapi.models import OrderProduct

class OrderProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = (
            "id",
            "order",
            "product",
            "customization"
        )

class OrderProducts(ViewSet):
    
    def retrieve(self, request, pk=None):
        try:
            current_user = request.user
            item = OrderProduct.objects.get(pk=pk, order__user=current_user)

            serializer = OrderProductItemSerializer(item, context={"request": request})

            return Response(serializer.data)
        
        except OrderProduct.DoesNotExist:
            return Response({"message": "order-product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
    def destroy(self, request, pk=None):
        try:
            current_user = request.user
            order_product = OrderProduct.objects.get(pk=pk, order__user=current_user)
            order_product.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        except OrderProduct.DoesNotExist:
            return Response({"message": "order-product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
