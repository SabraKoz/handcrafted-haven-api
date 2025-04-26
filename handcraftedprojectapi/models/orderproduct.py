from django.db import models

class OrderProduct(models.Model):
    order = models.ForeignKey("Order", on_delete=models.DO_NOTHING, related_name="items")
    product = models.ForeignKey("Product", on_delete=models.DO_NOTHING, related_name="items")
    customization = models.CharField(max_length=300)
    