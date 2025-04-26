from django.db import models
from django.contrib.auth.models import User

class Payment(models.Model):
    merchant = models.CharField(max_length=25)
    number = models.CharField(max_length=25)
    expiration = models.DateField(default="0000-00-00")
    address = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="payment_types")
    