from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta, date
from django.contrib.auth.models import User
from .models import Category, Product, Customer, Order, Supplier, Expense, OrderItem
from .serializers import CategorySerializer, ProductSerializer, CustomerSerializer, OrderSerializer, UserSerializer, SupplierSerializer
from django.contrib.auth.mixins import LoginRequiredMixin


class UserViewSet(LoginRequiredMixin, viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CategoryViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        # Items with stock less than 5
        products = self.queryset.filter(stock_quantity__lt=5)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class CustomerViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class SupplierViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class OrderViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def productive_dashboard_data(request):
    try:
        days = int(request.GET.get('days', 30))
    except ValueError:
        days = 30

    today = timezone.now().date()
    start_date = today - timedelta(days=days)
    end_date = today

    # Helper function to calculate P&L for a date range
    def calculate_pl_for_period(s_date, e_date):
        orders = Order.objects.filter(status='Completed', created_at__date__range=(s_date, e_date))
        revenue = orders.aggregate(total=Sum('final_amount'))['total'] or 0
        
        # Calculate COGS (buy_price * quantity)
        order_items = OrderItem.objects.filter(order__in=orders)
        cogs = 0
        for item in order_items:
            buy_price = item.product.buy_price or 0
            cogs += item.quantity * buy_price
            
        # Calculate Expenses
        expenses = Expense.objects.filter(date__range=(s_date, e_date)).aggregate(total=Sum('amount'))['total'] or 0
        
        net_profit = revenue - cogs - expenses
        total_costs = cogs + expenses
        
        # Profit/Loss Margin % (relative to Revenue)
        margin_pct = (net_profit / revenue * 100) if revenue > 0 else 0
        # Return on Cost %
        roi_pct = (net_profit / total_costs * 100) if total_costs > 0 else 0
        
        return {
            'revenue': float(revenue),
            'cogs': float(cogs),
            'expenses': float(expenses),
            'net_profit': float(net_profit),
            'margin_percentage': round(float(margin_pct), 2),
            'roi_percentage': round(float(roi_pct), 2),
        }

    # 1. Filtered period data
    period_pl = calculate_pl_for_period(start_date, end_date)

    # 2. Previous vs Current Month data
    current_month_start = today.replace(day=1)
    previous_month_end = current_month_start - timedelta(days=1)
    previous_month_start = previous_month_end.replace(day=1)

    current_month_pl = calculate_pl_for_period(current_month_start, today)
    previous_month_pl = calculate_pl_for_period(previous_month_start, previous_month_end)

    # 3. Supplier Products details
    supplier_products = []
    for supplier in Supplier.objects.all():
        products = Product.objects.filter(supplier=supplier)
        prod_list = []
        for p in products:
            prod_list.append({
                'id': p.id,
                'name': p.name,
                'brand': p.brand,
                'model': p.model,
                'buy_price': float(p.buy_price or 0),
                'price': float(p.price),
                'stock_quantity': p.stock_quantity,
            })
        supplier_products.append({
            'supplier_id': supplier.id,
            'supplier_name': supplier.name,
            'products_count': products.count(),
            'products': prod_list
        })

    # 4. Daily basic charges list and timeline
    expenses_in_period = Expense.objects.filter(date__range=(start_date, end_date)).order_by('-date')
    expenses_list = [{
        'id': exp.id,
        'title': exp.title,
        'amount': float(exp.amount),
        'date': exp.date.isoformat(),
        'description': exp.description or ''
    } for exp in expenses_in_period]

    daily_expenses = {}
    for i in range((end_date - start_date).days + 1):
        d = start_date + timedelta(days=i)
        daily_expenses[d.isoformat()] = 0.0

    for exp in expenses_in_period:
        date_str = exp.date.isoformat()
        if date_str in daily_expenses:
            daily_expenses[date_str] += float(exp.amount)

    daily_expenses_list = [{'date': k, 'amount': v} for k, v in sorted(daily_expenses.items())]

    return Response({
        'period_days': days,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'period_pl': period_pl,
        'current_month_pl': current_month_pl,
        'previous_month_pl': previous_month_pl,
        'supplier_products': supplier_products,
        'expenses': expenses_list,
        'daily_expenses_timeline': daily_expenses_list,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_expense_api(request):
    title = request.data.get('title')
    amount = request.data.get('amount')
    date_val = request.data.get('date', timezone.now().date().isoformat())
    description = request.data.get('description', '')

    if not title or not amount:
        return Response({'error': 'Title and Amount are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        expense = Expense.objects.create(
            title=title,
            amount=float(amount),
            date=date_val,
            description=description
        )
        return Response({
            'id': expense.id,
            'title': expense.title,
            'amount': float(expense.amount),
            'date': expense.date.isoformat() if isinstance(expense.date, date) else expense.date,
            'description': expense.description
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
