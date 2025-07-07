from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'price', 'quantity', 'discount', 'category', 'created_at')
    search_fields = ('name', 'brand', 'category')
    list_filter = ('brand', 'category', 'created_at')
