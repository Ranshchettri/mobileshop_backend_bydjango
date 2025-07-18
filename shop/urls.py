from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import get_all_orders, CustomTokenObtainPairView, OrderViewSet, ProductListView, update_profile, get_user_profile, ChatMessageListCreateView

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),  # GET all products
    path('products/<int:pk>/', views.get_product_by_id),  # GET product by ID
    path('products/add/', views.add_product),  # POST new product
    path('products/update/<int:pk>/', views.update_product, name='update_product'),  # PUT update product
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),  # DELETE product
    path('orders/', get_all_orders, name='get_all_orders'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('me/update/', update_profile),
    path('me/', get_user_profile),
    path('chat/', ChatMessageListCreateView.as_view(), name='chat'),
    path('', include(router.urls)),
]


