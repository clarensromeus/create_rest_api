from rest_framework import routers
from .views import user_viewset, product_viewset

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"users", user_viewset, basename="user")
router.register(r"products", product_viewset, basename="product")
urlpatterns = router.urls
