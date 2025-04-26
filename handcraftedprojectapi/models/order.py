from django.db import models
from django.contrib.auth.models import User
from .payment import Payment

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_on = models.DateField(default="0000-00-00")
    payment = models.ForeignKey(Payment, on_delete=models.DO_NOTHING, null=True)
