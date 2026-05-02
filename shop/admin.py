from django.contrib import admin
from .models import Category, Product, Customer, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'price', 'stock_quantity', 'category')
    search_fields = ('name', 'brand', 'imei')
    list_filter = ('category', 'brand')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created_at')
    search_fields = ('name', 'phone')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer', 'status', 'final_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('invoice_number', 'customer__name', 'customer__phone')
    inlines = [OrderItemInline]
