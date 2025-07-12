from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import get_all_orders, CustomTokenObtainPairView, OrderViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('products/', views.get_all_products),  # GET all products
    path('products/<int:pk>/', views.get_product_by_id),  # GET product by ID
    path('products/add/', views.add_product),  # POST new product
    path('products/update/<int:pk>/', views.update_product, name='update_product'),  # PUT update product
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),  # DELETE product
    path('orders/', get_all_orders, name='get_all_orders'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('', include(router.urls)),
]


