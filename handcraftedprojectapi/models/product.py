from django.db import models
from django.contrib.auth.models import User
from .productcategory import ProductCategory
from .orderproduct import OrderProduct
from .store import Store

class Product(models.Model):
    name = models.CharField(max_length=50,)
    description = models.CharField(max_length=250,)
    price = models.FloatField()
    quantity = models.IntegerField()
    image_path = models.ImageField(upload_to="products", height_field=None, width_field=None, max_length=None, null=True,)
    category = models.ForeignKey(ProductCategory, on_delete=models.DO_NOTHING, related_name="products")
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING, related_name="store")
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="products")

    @property
    def number_sold(self):
        sold = OrderProduct.objects.filter(product=self, order__payment__isnull=False)
        return sold.count()

    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"
