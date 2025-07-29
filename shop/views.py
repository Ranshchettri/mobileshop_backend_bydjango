from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Product, Order, OrderItem, CartItem, ShippingAddress, Review, Notification
from .serializers import ProductSerializer, OrderSerializer, UserSerializer, ChatMessageSerializer, OrderItemSerializer, CartItemSerializer, ShippingAddressSerializer, ReviewSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer
from rest_framework.permissions import AllowAny
from rest_framework import generics
from rest_framework import viewsets, permissions, status
from rest_framework import generics
from rest_framework.filters import SearchFilter
from shop.models import ChatMessage

from django.db import models
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db.models import Sum

# Create your views here.

@api_view(['GET'])
def apiOverview(request):
    return Response({
        'List': '/product-list/',
        'Detail View': '/product-detail/<int:id>/',
        'Create': '/product-create/',
        'Update': '/product-update/<int:id>/',
        'Delete': '/product-delete/<int:id>/',
    })


# POST endpoint to add a product

# POST endpoint to add a product with image upload support
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def add_product(request):
    serializer = ProductSerializer(data=request.data, files=request.FILES)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_by_id(request, pk):
    try:
        product = Product.objects.get(id=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_orders(request):
    user = request.user
    if user.is_staff or user.is_superuser:
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(user=user)  # <-- FIXED HERE
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        data['user'] = {
            'username': user.username,
            'email': user.email,
            'full_address': getattr(user, 'full_address', ''),
            'contact': getattr(user, 'contact', ''),
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        print("LOGIN DATA RECEIVED:", request.data)
        return super().post(request, *args, **kwargs)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(customer=user)

# Update Product
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request, pk):
    try:
        product = Product.objects.get(id=pk)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete Product
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, pk):
    try:
        product = Product.objects.get(pk=pk)
        product.delete()
        return Response({"detail": "Product deleted."}, status=204)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=404)

from .models import Product
from .serializers import ProductSerializer

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name', 'brand', 'description']

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    if user.is_superuser or user.is_staff:
        role = "admin"
    else:
        role = "customer"
    return Response({
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "contact": user.contact,
        "address": user.address,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "role": role,  # <-- add this line
    })

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data
    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)
    user.contact = data.get("contact", user.contact)
    user.address = data.get("address", user.address)
    user.save()
    return Response(UserSerializer(user).data, status=200)

class ChatMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        other_user_id = self.request.query_params.get('with')
        if other_user_id:
            return ChatMessage.objects.filter(
                (models.Q(sender=user) & models.Q(recipient__id=other_user_id)) |
                (models.Q(sender__id=other_user_id) & models.Q(recipient=user))
            ).order_by('timestamp')
        return ChatMessage.objects.none()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

@api_view(['GET'])
def productList(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    data = request.data
    user = request.user
    items = data.get("items", [])

    # Calculate total price from items
    total_price = sum(
        int(item["quantity"]) * float(item["price"])
        for item in items
    )

    # Create Order
    order = Order.objects.create(
        user=user,
        total_price=total_price,
        payment_method=data.get("payment_method", "COD"),
        payment_status="pending",
        order_status="pending"
    )

    # Create OrderItem for each cart item
    for item in items:
        OrderItem.objects.create(
            order=order,
            product_id=item["product"],
            quantity=item["quantity"],
            price=item["price"]
        )

    serializer = OrderSerializer(order)
    return Response(serializer.data)

from rest_framework import generics
from .models import OrderItem, CartItem, ShippingAddress
from .serializers import OrderItemSerializer, CartItemSerializer, ShippingAddressSerializer
from rest_framework.permissions import IsAuthenticated

class OrderItemListCreateView(generics.ListCreateAPIView):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

class CartItemListCreateView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

class ShippingAddressListCreateView(generics.ListCreateAPIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

from .models import Review
from .serializers import ReviewSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

class ProductReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs["pk"])

    def perform_create(self, serializer):
        serializer.save(
            product_id=self.kwargs["pk"],
            user=self.request.user
        )

class UserListView(generics.ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Product, CartItem, ShippingAddress, Order, OrderItem
from .serializers import CartItemSerializer, ShippingAddressSerializer, OrderSerializer

# ✅ GET & ADD cart items
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    user = request.user

    if request.method == 'GET':
        cart_items = CartItem.objects.filter(user=user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=404)

        # Check if already in cart
        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()

        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=201)

# ✅ DELETE cart item
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_cart_item(request, pk):
    user = request.user
    try:
        item = CartItem.objects.get(user=user, id=pk)
        item.delete()
        return Response({'message': 'Item removed'}, status=204)
    except CartItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)

# ✅ ADD/UPDATE shipping address
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_shipping_address(request):
    user = request.user
    address = request.data.get('address')
    city = request.data.get('city')
    postal_code = request.data.get('postal_code')
    country = request.data.get('country')

    shipping, created = ShippingAddress.objects.get_or_create(user=user)
    shipping.address = address
    shipping.city = city
    shipping.postal_code = postal_code
    shipping.country = country
    shipping.save()

    serializer = ShippingAddressSerializer(shipping)
    return Response(serializer.data, status=201)

# ✅ PLACE ORDER from cart
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    user = request.user
    items = request.data.get('items', [])
    payment_method = request.data.get('payment_method', 'COD')

    total = sum([item['quantity'] * item['price'] for item in items])

    order = Order.objects.create(
        user=user,
        total_price=total,
        payment_method=payment_method,
        payment_status='pending',
        order_status='pending'
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product_id=item['product'],
            quantity=item['quantity'],
            price=item['price']
        )

    # Optionally clear cart
    CartItem.objects.filter(user=user).delete()

    serializer = OrderSerializer(order)
    return Response(serializer.data, status=201)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity', 1)

        # Check if item already in cart
        cart_item, created = CartItem.objects.get_or_create(
            user=self.request.user,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart_item

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart_item = self.perform_create(serializer)
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'])
    def clear(self, request):
        CartItem.objects.filter(user=request.user).delete()
        return Response({"status": "cart cleared"})
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer
from django.db import IntegrityError

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            # Role logic: admin/seller or customer
            if user.is_superuser or user.is_staff:
                role = "admin"
            else:
                role = "customer"

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'contact': user.contact,
                    'address': user.address,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser,
                    'role': role,  # <-- add this line
                }
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer

class UserView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_active:
            return Response({"detail": "Your account has been blocked by admin."}, status=403)
        serializer.save()

from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admin can update users

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    total_orders = Order.objects.count()
    total_revenue = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0

    # Most selling products
    product_sales = (
        OrderItem.objects.values(
            'product__id',
            'product__name',
            'product__image'
        )
        .annotate(quantity_sold=Sum('quantity'))
        .order_by('-quantity_sold')
    )

    most_selling_products = list(product_sales)
    best_product = most_selling_products[0] if most_selling_products else None

    return Response({
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "best_product": best_product,
        "most_selling_products": most_selling_products,
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

from rest_framework import serializers

class MostSellingProductSerializer(serializers.Serializer):
    product = serializers.IntegerField()
    quantity_sold = serializers.IntegerField()

class MostSellingProductsView(generics.ListAPIView):
    serializer_class = MostSellingProductSerializer

    def get_queryset(self):
        qs = (
            OrderItem.objects
            .values("product")
            .annotate(quantity_sold=Sum("quantity"))
            .order_by("-quantity_sold")
        )
        # Attach product name and image to each result
        product_ids = [item["product"] for item in qs]
        products = Product.objects.in_bulk(product_ids)
        result = []
        for item in qs:
            product = products.get(item["product"])
            result.append({
                "product": item["product"],
                "name": product.name if product else "",
                "image": product.image.url if product and product.image else "",
                "quantity_sold": item["quantity_sold"],
            })
        return result

def get_order_status_message(order, status):
    if status == "pending":
        return f"Your order #{order.id} has been placed."
    elif status == "processing":
        return f"Your order #{order.id} is being processed by the seller."
    elif status == "shipped":
        return f"Your order #{order.id} has been shipped from the seller's warehouse."
    elif status == "delivered":
        return f"Order #{order.id} delivered successfully! Thank you for choosing us. Don't forget to give a review for a better experience."
    elif status == "cancelled":
        return f"Your order #{order.id} was cancelled by the seller. Please contact or chat with the seller."
    else:
        return f"Your order #{order.id} status changed to {status.capitalize()}."

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request, pk):
    order = Order.objects.get(pk=pk)
    new_status = request.data.get('order_status')
    order.order_status = new_status
    order.save()
    message = get_order_status_message(order, new_status)
    Notification.objects.create(
        user=order.user,
        message=message
    )
    return Response({'success': True})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    data = [
        {"message": n.message, "created_at": n.created_at, "is_read": n.is_read}
        for n in notifications
    ]
    return Response(data)

from django.contrib.auth import get_user_model

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_admin_id(request):
    User = get_user_model()
    admin = User.objects.filter(is_staff=True).first()
    if admin:
        return Response({'admin_id': admin.id})
    return Response({'error': 'Admin not found'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_chat_users(request):
    # Only admin can access
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=403)
    # All users except admin
    users = User.objects.exclude(id=request.user.id)
    data = [{'id': u.id, 'email': u.email, 'full_name': u.full_name} for u in users]
    return Response(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_all_messages(request):
    if not request.user.is_staff:
        return Response({'error': 'Unauthorized'}, status=403)
    messages = ChatMessage.objects.filter(recipient=request.user).order_by('-timestamp')
    data = [
        {
            'id': m.id,
            'sender_id': m.sender.id,
            'sender_email': m.sender.email,
            'message': m.message,
            'timestamp': m.timestamp
        }
        for m in messages
    ]
    return Response(data)