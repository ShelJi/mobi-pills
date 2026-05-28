from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Product, Customer, Order, OrderItem, Supplier

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True, use_url=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), required=False, allow_null=True
    )
    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Product
        fields = '__all__'

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price_at_time', 'total_price']
        read_only_fields = ['id']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)
    customer_details = CustomerSerializer(source='customer', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'invoice_number', 'customer', 'customer_details', 'created_by', 'created_by_name',
            'subtotal', 'tax_amount', 'discount', 'final_amount', 'status',
            'created_at', 'updated_at', 'items'
        ]
        read_only_fields = ['id', 'invoice_number', 'created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
            # If status is completed, deduct stock
            if order.status == 'Completed':
                product = item_data['product']
                product.stock_quantity -= item_data['quantity']
                product.save()
            
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        old_status = instance.status
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if items_data is not None:
            # Recreate items
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)
                
                # If changing status to Completed, deduct stock
                if old_status != 'Completed' and instance.status == 'Completed':
                    product = item_data['product']
                    product.stock_quantity -= item_data['quantity']
                    product.save()

        # Handle status change without item update
        elif old_status != 'Completed' and instance.status == 'Completed':
            for item in instance.items.all():
                product = item.product
                product.stock_quantity -= item.quantity
                product.save()
                
        return instance
