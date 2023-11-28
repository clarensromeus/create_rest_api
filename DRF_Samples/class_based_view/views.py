from rest_framework.decorators import APIView
from rest_framework import status, generics
from django.http import Http404
from django.contrib.auth.models import User
from rest_framework.response import Response
from view_api.models import Product, Purchase
from view_api.serializer import ProductSerializer, PurchaseSerializer, UserSerializer, PasswordSerializer
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from django.shortcuts import get_object_or_404
from .pagination import Limit_offset_pagination, Page_numer_pagination
from rest_framework import filters


# after showing the accomplishment of function based view  now
# time to make the code simpler and more viewable using generics in class based views
class productListViewGenerics(generics.ListCreateAPIView):
    queryset = Product.objects.all()  # pylint: disable=no-member
    serializer_class = ProductSerializer
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = Limit_offset_pagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["Price"]

    def perform_create(self, serializer):
        user = self.request.user
        if not user:
            raise ValidationError(
                message="sorry product must have a seller", code=404)
        serializer.save(Seller=user)


class productDetailViewGenerics(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()  # pylint: disable=no-member
    serializer_class = ProductSerializer
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ["username"]


class userListCreateViewGenerics(generics.ListCreateAPIView):
    queryset = User.objects.all()
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = Page_numer_pagination


class userDetailViewGenerics(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = ["username"]

    # i instead use the alternative get_object method

    def get_object(self):
        username = self.kwargs["username"]
        queryset = self.get_queryset()  # pylint: disable=no-member
        user_object = get_object_or_404(queryset, username=username)
        return user_object


class CustomAuthToken(ObtainAuthToken):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(  # pylint: disable=no-member
            user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class change_passwordViewGenerics(generics.UpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    parser_classes = [JSONParser]

    # i override the update method to change user password
    def update(self, request, pk):
        queryset = self.get_queryset()
        user = get_object_or_404(queryset, pk=pk)
        serializer = PasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data["new_password"]
            user.set_password(new_password)
            user.save()
            return Response({"message": "password set with success"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# another way to write class based view that is a bit using more lines code
# it is king of like function based view but using bits of reusable components


class ProductListView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        queryset = Product.objects.all()  # pylint: disable=no-member
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = User.objects.filter(pk=request.user.id).first()
        product = Product(Seller=user)
        serializer = ProductSerializer(product, data=request)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser, IsAuthenticated]
    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]

    def get_object(self, pk):
        try:
            product = Product.objects.filter(  # pylint: disable=no-member
                pk=pk).first()
            return product
        except product.DoesNotExist:
            raise Http404

    def get(self, request, pk=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        product = self.get_object(pk)
        product_name = product.ProductName
        product.delete()
        return Response({"message": "product %s is deleted with success" % product_name}, status=status.HTTP_204_NO_CONTENT)


class buyPoductDetailview(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    def get_object(self, pk, purchaser):
        try:
            product = Product.objects.filter(  # pylint: disable=no-member
                pk=pk).first()
            product.Purchases = purchaser
            product.save()
            return product
        except:
            raise Http404

    def put(self, request, pk=None):
        purchase = Purchase(Owner=request.user)
        serializer = PurchaseSerializer(purchase, data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                serializer.save()
                purchasing = Purchase.objects.filter(  # pylint: disable=no-member
                    pk=pk).first()
                self.get_object(pk, purchasing)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except purchase.DoesNotExist:  # pylint: disable=no-member
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class userListview(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        queryset = User.objects.all
        serializer = UserSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
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


class userDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    def get_object(self, pk):
        try:
            return User.objects.filter(pk=pk).first()
        except User.DoesNotExist:  # pylint: disable=no-member
            raise Http404

    def put(self, request, pk=None):
        old_password = request.data.get("password")
        newpassword = request.data.get("newpassword")
        user = self.get_object(pk)
        if user.check_password(old_password):
            user.set_password(newpassword)
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
