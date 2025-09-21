from django.contrib import admin
from .models import Product, ToBeDelivered, User, Delivery, ProductDelivery


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'price']
    search_fields = ['name']


@admin.register(ToBeDelivered)
class ToBeDeliveredAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'price']
    list_filter = ['product']


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_type']
    list_filter = ['user_type']


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'courier', 'store', 'time_created', 'delivered']
    list_filter = ['delivered', 'time_created']


@admin.register(ProductDelivery)
class ProductDeliveryAdmin(admin.ModelAdmin):
    list_display = ['items', 'delivery']