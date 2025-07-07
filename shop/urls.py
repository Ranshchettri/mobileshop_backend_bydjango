from django.urls import path
from . import views
from .views import get_all_orders, CustomTokenObtainPairView

urlpatterns = [
    path('products/', views.get_all_products),  # GET all products
    path('products/<int:pk>/', views.get_product_by_id),  # GET product by ID
    path('products/add/', views.add_product),  # POST new product
    path('orders/', get_all_orders, name='get_all_orders'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]


