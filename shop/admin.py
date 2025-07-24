from django.contrib import admin
from .models import Product, Order, OrderItem, CartItem, ShippingAddress, ChatMessage, User, ChatThread, Message

admin.site.register(Product)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer__username', 'product__name')

admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(ShippingAddress)
admin.site.register(ChatMessage)
admin.site.register(User)
admin.site.register(ChatThread)
admin.site.register(Message)
