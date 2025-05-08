from django.db import models
from django.contrib.auth.models import User

class ProductFavorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorited_products")
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="favorites")
