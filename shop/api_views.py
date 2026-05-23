from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from django.contrib.auth.models import User
from .models import Category, Product, Customer, Order
from .serializers import CategorySerializer, ProductSerializer, CustomerSerializer, OrderSerializer, UserSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        # Items with stock less than 5
        products = self.queryset.filter(stock_quantity__lt=5)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        # Set the user who created the order
        if self.request.user.is_authenticated:
            serializer.save(created_by=self.request.user)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        completed_orders = Order.objects.filter(status='Completed')

        daily_sales = completed_orders.filter(created_at__date=today).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        weekly_sales = completed_orders.filter(created_at__date__gte=week_start).aggregate(Sum('final_amount'))['final_amount__sum'] or 0
        monthly_sales = completed_orders.filter(created_at__date__gte=month_start).aggregate(Sum('final_amount'))['final_amount__sum'] or 0

        recent_orders = completed_orders.order_by('-created_at')[:5]
        recent_orders_data = self.get_serializer(recent_orders, many=True).data

        return Response({
            'daily_sales': daily_sales,
            'weekly_sales': weekly_sales,
            'monthly_sales': monthly_sales,
            'recent_orders': recent_orders_data
        })
