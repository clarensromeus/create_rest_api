from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Purchase


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]


class PasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ["password", "new_password"]


class ProductSerializer(serializers.ModelSerializer):
    Quality_choice = serializers.CharField(
        source="get_Quality_display",  read_only=True)
    Seller = UserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "ProductName", "Price",
                  "Quality", "Quality_choice", "Seller", "created_at", "updated_at"]

    def validate_Quality_choice(self, value):
        if value is None:
            raise serializers.ValidationError(
                "sorry you got to pick a quality")
        return value


class PurchaseSerializer(serializers.ModelSerializer):
    Owner = UserSerializer()

    class Meta:
        modle = Purchase
        fields = ["id", "Quantity", "created_at", "Owner"]
        depth = 1
