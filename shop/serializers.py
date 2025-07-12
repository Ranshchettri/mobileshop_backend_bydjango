from rest_framework import serializers
from .models import Product, Order

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'
