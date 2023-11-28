from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication
from view_api.models import Product, User, Purchase
from view_api.serializer import ProductSerializer, UserSerializer, PurchaseSerializer, PasswordSerializer
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from django.http import Http404
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.exceptions import ValidationError

"""
  a viewset is a type of class based views with only a minor difference on http methods that they each use
  cls provides with methods like get,post,update, delete whereas viesets use list,create,update,retrieve and destroy,
  the nicest part of the chess is that it automatically combines a set of related views into a single class 
"""


# now time to start writing viewsets class with less code by using built-in generics with Model viewset
class product_viewset(viewsets.ModelViewSet):
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    queryset = Product.objects.all()  # pylint: disable=no-member
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_permissions(self):
        if self.action == "list":
            permission_classes = [IsAuthenticatedOrReadOnly, IsAdminUser]
        else:
            permission_classes = [IsAdminUser, IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        user = self.request.user
        if not user:
            raise ValidationError(
                message="sorry product must have a seller", code=404)
        serializer.save(Seller=user)

    @action(detail=True, methods=["PUT"], url_name="purchasing", url_path="purchasing",
            authentication_classes=[
                TokenAuthentication], permission_classes=[IsAuthenticated],
            renderer_classes=[JSONRenderer], parser_classes=[JSONParser])
    def buy_product(self, request, pk=None):
        product_queryset = self.get_queryset()
        product = get_object_or_404(product_queryset, pk=pk)
        purchase = Purchase(Owner=request.user)
        serializer = PurchaseSerializer(purchase, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            Purchasing = Purchase.objects.filter(  # pylint: disable=no-member
                id=serializer.validated_data["id"])
            product.Seller = Purchasing
            product.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @buy_product.mapping.delete
    def product_objection(self, request, pk):
        product = Product.objects.filter(  # pylint: disable=no-member
            pk=pk).first()
        purchaser_id = product.Purchases.id
        purchase = Purchase.objects.filter(  # pylint: disable=no-member
            Owner=request.user, pk=int(purchaser_id))
        if not purchase:
            return Response({"message": "no owner for the purchase"}, status=status.HTTP_204_NO_CONTENT)
        serializer = ProductSerializer(product)
        purchase.delete()
        return Response(serializer.data, status=status.HTTP_200_OK)


class user_viewset(viewsets.ModelViewSet):
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["PUT"], renderer_classes=[JSONRenderer],
            url_name="change_password", url_path="change_password",
            permission_classes=[IsAuthenticated], authentication_classes=[TokenAuthentication])
    def change_password(self, request, pk=None):
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=pk)
        serializer = PasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data["new_password"]
            user.set_password(new_password)
            user.save()
            return Response({"message": "password set with success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["GET"], url_name="administrators", url_path="administrators",
            renderer_classes=[JSONRenderer], parser_classes=[JSONParser], authentication_classes=[TokenAuthentication], permission_classes=[IsAdminUser])
    def administrators(self, request):
        users = self.get_queryset()
        administrators = get_list_or_404(users, is_staff=True)
        if not administrators:
            return Response({"message": "no administrators"}, status=status.HTTP_204_NO_CONTENT)
        serializer = UserSerializer(administrators, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# an alternative to write viewset with more code snippets
# using Viewset not Modelviewset
class ProductViewsets(viewsets.ViewSet):
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsAdminUser]

    def list(self, request):
        product = Product.objects.all()  # pylint: disable=no-member
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        product = Product(Seller=request.user)
        serializer = ProductSerializer(product, data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        if not valid:
            return Response(serializer.errors, status=status.HTTP_501_NOT_IMPLEMENTED)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        product = Product.objects.filter(  # pylint: disable=no-member
            pk=pk).first()
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        product = Product.objects.filter(  # pylint: disable=no-member
            pk=pk).first()
        serializer = ProductSerializer(product, data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        if not valid:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        product = Product.objects.filter(  # pylint: disable=no-member
            pk=pk).first()
        product_name = product.ProductName
        product.delete()
        return Response({"message": "product %s is successfully deleted " % product_name}, status=status.HTTP_204_NO_CONTENT)


class buy_productViewset(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    def customization(self, pk, purchaser):
        try:
            product = Product.objects.filter(  # pylint: disable=no-member
                pk=pk).first()
            product.Purchases = purchaser
            product.save()
            return product
        except:
            raise Http404

    def update(self, request, pk=None):
        purchase = Purchase(Owner=request.user)
        serializer = PurchaseSerializer(purchase, data=request.data)
        valid = serializer.is_valid(raise_exception=True)
        if not valid:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        purchasing = Purchase.objects.filter(  # pylint: disable=no-member
            pk=pk).first()
        self.customization(pk, purchasing)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class usersviewset(viewsets.ViewSet):

    def list(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
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
            except user.DoesNotExist:
                data.pop("token")
                data["success"] = False
                return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user = User.objects.filter(pk=pk).first()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        old_password = request.data.get("password")
        newpassword = request.data.get("newpassword")
        user = User.objects.filter(pk=pk).first()
        if user.check_password(old_password):
            user.set_password(newpassword)
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
