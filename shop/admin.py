from django.contrib import admin
from .models import Product, Order  # Make sure Order is imported

# Register Product (already registered)
admin.site.register(Product)

# ✅ Register Order so it appears in the Django Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'product__name')
