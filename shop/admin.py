from django.contrib import admin
from .models import Product, Order, OrderItem, CartItem, ShippingAddress, ChatMessage, User, ChatThread, Message

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_price', 'status', 'created_at', 'order_items')

    def order_items(self, obj):
        return ", ".join([f"{item.product.name} x {item.quantity}" for item in obj.items.all()])

admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(ShippingAddress)
admin.site.register(ChatMessage)
admin.site.register(User)
admin.site.register(ChatThread)
admin.site.register(Message)
