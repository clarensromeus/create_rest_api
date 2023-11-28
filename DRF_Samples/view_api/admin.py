from django.contrib import admin
from .models import Product, Purchase

# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["ProductName", "Price", "updated_at"]


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    ordering = ["Quantity"]
