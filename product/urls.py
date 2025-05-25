from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CategoryViewSet, ProductViewSet, ProductAttributeViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)
router.register('attributes', ProductAttributeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]