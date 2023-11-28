from django.db import models
import uuid
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from .choice import PRODUCT_CHOICES, PRODUCT_TYPE
import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token


class Purchase(models.Model):
    Quantity = models.IntegerField(default=1, validators=[
        MinValueValidator(
            1, message="Quantity must be at least one"),
        MaxValueValidator(10, message="Quantity must not be more than 10")])
    Owner = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=datetime.datetime.now)

    def __str__(self) -> str:
        return "{}".format(self.Owner)


class Product(models.Model):
    id = models.UUIDField("user id", default=uuid.uuid4,
                          primary_key=True, unique=True)
    ProductName = models.CharField(max_length=200, unique=True)
    Price = models.IntegerField(default=200,
                                validators=[MinValueValidator(200, message="price is too low"),
                                            MaxValueValidator(10000, message="price is too high")])
    Purchases = models.OneToOneField(
        Purchase, null=True, on_delete=models.CASCADE, blank=True)
    Quality = models.CharField(max_length=200,
                               choices=PRODUCT_CHOICES, default=PRODUCT_TYPE.get("FIRST_CLASS"))
    Seller = models.ForeignKey(
        User, related_name="Seller", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=datetime.datetime.now)
    updated_at = models.DateTimeField(auto_now=datetime.datetime.now)

    def __str__(self) -> str:
        return "{}".format(self.ProductName)

    class Meta:
        ordering = ["updated_at", "Price"]


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def generate_user_token(sender, instance=None, created=False, *args, **kwargs):
    # generate a toeken each time a user is created or updated
    if created:
        Token.objects.create(user=instance)  # pylint: disable=no-member
