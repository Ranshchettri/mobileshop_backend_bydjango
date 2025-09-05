from django.contrib import admin
from .models import Product, Order, OrderItem, CartItem, ShippingAddress, ChatMessage, User, ChatThread, Message

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'order_status', 'payment_status', 'created_at']

admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(ShippingAddress)
admin.site.register(ChatMessage)
admin.site.register(User)
admin.site.register(ChatThread)
admin.site.register(Message)
