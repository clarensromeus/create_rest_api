from django.urls import path
from .views import products, update_product, delete_product, one_product, login, change_password, create_product, buy_product, register


urlpatterns = [
    path("", products, name="products"),
    path("register", register, name="register"),
    path('login', login, name="login"),
    path('change_password', change_password, name="change_password"),
    path("create", create_product, name="create"),
    path("<str:pk>", one_product, name="one_product"),
    path("update/<str:pk>", update_product, name="update"),
    path("delete/<str:pk>", delete_product, name="delete"),
    path("buy_product/<str:pk>", buy_product, name="buy")
]
