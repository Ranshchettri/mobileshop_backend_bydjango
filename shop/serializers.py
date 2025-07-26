from rest_framework import serializers
from .models import Product, Order, OrderItem, CartItem, ShippingAddress, Review
from django.contrib.auth import get_user_model
from shop.models import ChatMessage
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# ✅ Product Serializer (already used in Home.jsx)
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


# ✅ Cart Item Serializer
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = '__all__'


# ✅ Shipping Address Serializer
class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'


# ✅ Order Item Serializer
class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='product.name', read_only=True)
    image = serializers.ImageField(source='product.image', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'name', 'image', 'quantity', 'price']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'full_name', 'contact', 'address', 'is_active')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            contact=validated_data.get('contact', ''),
            address=validated_data.get('address', ''),
        )
        return user

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password', 'contact', 'address')

    def create(self, validated_data):
        validated_data['is_active'] = True  # always active by default
        return User.objects.create(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid login credentials")
        return {'user': user}

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['username'] = user.username
        token['is_seller'] = user.is_seller
        return token

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Fix: username/full_address हटाउनुहोस्, role थप्नुहोस्
        if user.is_superuser or user.is_staff:
            role = "admin"
        else:
            role = "customer"

        data['user'] = {
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'contact': user.contact,
            'address': user.address,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'role': role,
        }
        return data

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.email', read_only=True)
    recipient_name = serializers.CharField(source='recipient.email', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'recipient', 'message', 'timestamp', 'sender_name', 'recipient_name']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'contact', 'address')

# ✅ Order Serializer
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()  # Add this

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "total_price",
            "order_status",
            "payment_status",
            "created_at",
            "date",         # Add this
            "items",
        ]

    def get_user(self, obj):
        user = obj.user
        return {
            "full_name": getattr(user, "full_name", ""),
            "email": getattr(user, "email", ""),
            "contact": getattr(user, "contact", ""),
            "address": getattr(user, "address", ""),
        }

    def get_items(self, obj):
        return [
            {
                "name": getattr(item.product, "name", ""),
                "quantity": item.quantity,
                "price": item.price,
            }
            for item in obj.items.all()
        ]

    def get_date(self, obj):
        # Format date as string, e.g. "2025-07-26 19:45"
        return obj.created_at.strftime("%Y-%m-%d %H:%M") if obj.created_at else "N/A"
