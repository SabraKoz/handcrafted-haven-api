from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from handcraftedprojectapi.models import Payment

class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            "id",
            "merchant",
            "number",
            "expiration",
            "address",
            "user"
        )

class Payments(ViewSet):
    def list(self, request):
        payments = Payment.objects.all()
        user = request.user.id

        if user is not None:
            payments = payments.filter(user__id=user)

        serializer = PaymentSerializer(payments, many=True, context={"request": request})

        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        try:
            payment = Payment.objects.get(pk=pk)
            serializer = PaymentSerializer(payment, context={"request": request})

            return Response(serializer.data)
        except Exception:
            return HttpResponseServerError()
        
    def create(self, request):
        new_payment = Payment()
        new_payment.merchant = request.data["merchant"]
        new_payment.number = request.data["number"]
        new_payment.expiration = request.data["expiration"]
        new_payment.address = request.data["address"]
        new_payment.user = request.user

        new_payment.save()

        serializer = PaymentSerializer(new_payment, context={"request": request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        try:
            payment = Payment.objects.get(pk=pk)
            payment.delete()

            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        except Payment.DoesNotExist:
            return Response({"message": "payment type does not exist"}, status=status.HTTP_404_NOT_FOUND)
