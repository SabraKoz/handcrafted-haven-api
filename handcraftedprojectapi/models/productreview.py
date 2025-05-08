from django.db import models
from django.contrib.auth.models import User

class ProductReview(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.CharField(max_length=100)

    class Meta:
        verbose_name = ("productreview")
        verbose_name_plural = ("productreviews")

    def __str__(self):
        return self.review
    