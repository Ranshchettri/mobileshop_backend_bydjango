from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import viewsets, permissions, status

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
        serializer = ProductSerializer(product, many=False)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_orders(request):
    orders = Order.objects.all().order_by('-ordered_at')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'email': self.user.email,
            'isAdmin': self.user.is_staff,
        }
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only admin can see all orders
        if self.request.user.is_staff:
            return Order.objects.all()
        # Regular users see only their orders
        return Order.objects.filter(customer=self.request.user)

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
        product = Product.objects.get(id=pk)
        product.delete()
        return Response({'message': 'Product deleted'}, status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response({'detail': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
