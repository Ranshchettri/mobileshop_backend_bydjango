from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    CustomTokenObtainPairView,
    OrderViewSet,
    ProductListView,
    update_profile,
    get_user_profile,
    ChatMessageListCreateView,
    OrderItemListCreateView,
    CartItemListCreateView,
    ShippingAddressListCreateView,
    ReviewListCreateView,
    ProductReviewListCreateView,
    UserListView,
    CartItemViewSet,
    RegisterView,
    LoginView,
    ProductViewSet,
    UserViewSet,
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'cart', CartItemViewSet, basename='cart')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Cart
    path('cart/', views.cart_view, name='cart-view'),
    path('cart/<int:pk>/', views.delete_cart_item, name='cart-item-delete'),

    # Order
    path('orders/', views.get_all_orders),
    path('orders/create/', views.create_order),

    # User
    path('me/', views.get_user_profile),
    path('me/update/', views.update_profile),
    path('users/', UserListView.as_view(), name='user-list'),

    # Reviews
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('products/<int:pk>/reviews/', ProductReviewListCreateView.as_view(), name='product-reviews'),

    # Chat
    path('chat/', views.ChatMessageListCreateView.as_view()),

    # Token
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Router URLs
    path('', include(router.urls)),
    path('order-items/', OrderItemListCreateView.as_view(), name='orderitem-list-create'),
    path('cart-items/', CartItemListCreateView.as_view(), name='cartitem-list-create'),
    path('shipping-addresses/', ShippingAddressListCreateView.as_view(), name='shippingaddress-list-create'),

    # Auth
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Additional URLs
    path('orders/<int:pk>/status/', views.update_order_status, name='update_order_status'),
    path('notifications/', views.user_notifications, name='user_notifications'),
]


