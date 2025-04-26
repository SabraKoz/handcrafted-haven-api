from django.db import models
from django.contrib.auth.models import User
from .productcategory import ProductCategory

class Product(models.Model):
    name = models.CharField(max_length=50,)
    description = models.CharField(max_length=250,)
    price = models.FloatField()
    quantity = models.IntegerField()
    image_path = models.ImageField(upload_to="products", height_field=None, width_field=None, max_length=None, null=True,)
    category = models.ForeignKey(ProductCategory, on_delete=models.DO_NOTHING, related_name="products")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="products")

    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"
