from django.urls import path
from .views import CustomAuthToken, userDetailViewGenerics, productListViewGenerics, productDetailViewGenerics, userListCreateViewGenerics

urlpatterns = [
    path("login", CustomAuthToken.as_view(), name="login"),
    path("product_create_list_view", productListViewGenerics.as_view(), name="plv"),
    path("product_detail_view/<str:pk>",
         productDetailViewGenerics.as_view(), name="pdv"),
    path("user_create_list_view", userListCreateViewGenerics.as_view(), name="ulc"),
    path("user_detail_view/<username>",
         userDetailViewGenerics.as_view(), name="udv"),
]
