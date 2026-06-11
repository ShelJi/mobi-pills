from django.contrib import admin
from .models import Category, Product, Customer, Order, OrderItem, Supplier, Expense
from django.contrib.auth.models import Group

admin.site.unregister(Group)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

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


admin.site.register(Supplier)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'date', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('title', 'description')