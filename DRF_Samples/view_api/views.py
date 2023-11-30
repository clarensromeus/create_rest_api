from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Product, Purchase
from django.contrib.auth.models import User
from .serializer import ProductSerializer, UserSerializer, PurchaseSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, parser_classes, renderer_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db.models.functions import Greatest, Lower
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

# Create your views here.

# there's a better pre-conceived way using by drf for loging in a user that i use in the class based view demo
# just a sample for using login strategy in function based view


@api_view(["POST"])
@parser_classes([JSONParser])
@renderer_classes([JSONRenderer])
def login(request):
    user = get_object_or_404(User, username=request.data["username"])
    data = {}
    if not user.check_password(request.data["password"]):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    token, __ = Token.objects.get_or_create(  # pylint: disable=no-member
        user=user)
    serializer = UserSerializer(instance=user)
    data["token"] = token.key
    data["user"] = serializer.data
    return Response(data, status=status.HTTP_200_OK)


@api_view(["POST"])
@parser_classes([JSONParser])
@renderer_classes([JSONRenderer])
def register(request):
    serializer = UserSerializer(data=request.data)
    data = {}
    if serializer.is_valid(raise_exception=True):
        try:
            serializer.save()
            user = User.objects.get(pk=serializer.data["id"])
            data["success"] = True
            data["token"] = Token.objects.get(  # pylint: disable=no-member
                user=user).key
            return Response(data, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:  # pylint: disable=no-member
            data.pop("token")
            data["success"] = False
            return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def all_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONParser])
def products(request):
    all_products = Product.objects.all().order_by(  # pylint: disable=no-member
        "-updated_at")
    serializer = ProductSerializer(all_products, many=True)
    return Response(serializer.data)


@api_view(["PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
@renderer_classes([JSONRenderer])
def change_password(request):
    old_password = request.data["password"]
    new_password = request.data["newpassword"]
    user = User.objects.get(pk=request.user.id)
    if not user.check_password(old_password):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    user.set_password(new_password)
    user.save()
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
@renderer_classes([JSONRenderer])
def create_product(request):
    user = User.objects.filter(pk=request.user.id).first()
    product = Product(Seller=user)
    serializer = ProductSerializer(product, data=request.data)
    if serializer.is_valid(raise_exception=True):
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except product.DoesNotExist:  # pylint: disable=no-member
            return Response("no content modified", status=status.HTTP_405_METHOD_NOT_ALLOWED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer])
def one_product(request, pk):
    product = Product.objects.get(pk=pk)  # pylint: disable=no-member
    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view(["PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
@parser_classes([JSONParser])
def update_product(request, pk):
    product = Product.objects.filter(   # pylint: disable=no-member
        pk=pk).first()
    serializer = ProductSerializer(
        product, data=request.data)
    if serializer.is_valid(raise_exception=True):
        ProductName = serializer.validated_data["ProductName"]
        serializer.save()
        try:
            return Response(ProductName, status=status.HTTP_200_OK)
        except product.DoesNotExist:
            return Response(status=status.HTTP_304_NOT_MODIFIED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_product(request, pk):
    if pk is not None:
        product = Product.objects.filter(  # pylint: disable=no-member
            pk=pk).first()
        product_name = product.ProductName
        product.delete()
        return Response(product_name, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser])
@renderer_classes([JSONRenderer])
def buy_product(request, pk):
    purchase = Purchase(Owner=request.user)
    product = Product.objects.filter(  # pylint: disable=no-member
        pk=pk).first()
    serializer = PurchaseSerializer(purchase, data=request.data)
    if serializer.is_valid(raise_exception=True):
        try:
            serializer.save()
            purchasing = Purchase.objects.filter(  # pylint: disable=no-member
                pk=pk).first()
            product.Purchase = purchasing
            product.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except purchase.DoesNotExist:  # pylint: disable=no-member
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
