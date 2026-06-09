import os
import django
from datetime import datetime, timedelta, date, timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobi_pills.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Category, Product, Supplier, Customer, Order, OrderItem, Expense

def seed():
    print("Starting dashboard data seeding...")
    
    # 1. Ensure suppliers exist
    sup1, _ = Supplier.objects.get_or_create(name='test sup 1', defaults={'phone1': '9876543210', 'email': 'sup1@example.com'})
    sup2, _ = Supplier.objects.get_or_create(name='test sup 2', defaults={'phone1': '9876543211', 'email': 'sup2@example.com'})
    
    # 2. Update existing products with buy_price and supplier
    p_updates = {
        'iPhone 15 Pro': {'buy_price': 800.00, 'supplier': sup1},
        'Galaxy S24 Ultra': {'buy_price': 950.00, 'supplier': sup2},
        'AirPods Pro 2': {'buy_price': 180.00, 'supplier': sup1},
        '20W USB-C Power Adapter': {'buy_price': 12.00, 'supplier': sup1},
        'Pixel 8 Pro': {'buy_price': 700.00, 'supplier': sup2},
    }
    
    for name, fields in p_updates.items():
        Product.objects.filter(name=name).update(buy_price=fields['buy_price'], supplier=fields['supplier'])
        
    print("Products updated.")

    # 3. Create Expenses
    Expense.objects.all().delete()
    
    # Current month expenses (June 2026)
    Expense.objects.create(title='Staff Salary', amount=15000.00, date=date(2026, 6, 1), description='Monthly staff salary payment')
    Expense.objects.create(title='Shop Rent', amount=8000.00, date=date(2026, 6, 1), description='Rent for main branch')
    Expense.objects.create(title='Electricity Bill', amount=1200.00, date=date(2026, 6, 5), description='Electricity bill for June')
    Expense.objects.create(title='Internet Charge', amount=600.00, date=date(2026, 6, 3), description='High-speed broadband internet')
    Expense.objects.create(title='Office Stationery', amount=350.00, date=date(2026, 6, 6), description='Pens, paper, registers')
    Expense.objects.create(title='Tea and Snacks', amount=150.00, date=date(2026, 6, 8), description='Daily basic charges for staff refresh')
    Expense.objects.create(title='Tea and Snacks', amount=150.00, date=date(2026, 6, 9), description='Daily basic charges for staff refresh')

    # Previous month expenses (May 2026)
    Expense.objects.create(title='Staff Salary', amount=15000.00, date=date(2026, 5, 1), description='Monthly staff salary payment')
    Expense.objects.create(title='Shop Rent', amount=8000.00, date=date(2026, 5, 1), description='Rent for main branch')
    Expense.objects.create(title='Electricity Bill', amount=1100.00, date=date(2026, 5, 5), description='Electricity bill for May')
    Expense.objects.create(title='Internet Charge', amount=600.00, date=date(2026, 5, 3), description='High-speed broadband internet')
    Expense.objects.create(title='Tea and Snacks', amount=180.00, date=date(2026, 5, 12), description='Daily basic charges for staff refresh')
    
    print("Expenses created.")

    # 4. Check/update order dates and create some May (previous month) orders
    # Let's adjust existing orders to have different dates in June 2026
    orders = list(Order.objects.all().order_by('id'))
    june_dates = [
        datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
        datetime(2026, 6, 3, 11, 30, tzinfo=timezone.utc),
        datetime(2026, 6, 5, 14, 15, tzinfo=timezone.utc),
        datetime(2026, 6, 7, 16, 45, tzinfo=timezone.utc),
        datetime(2026, 6, 8, 9, 0, tzinfo=timezone.utc),
        datetime(2026, 6, 9, 12, 0, tzinfo=timezone.utc),
        datetime(2026, 6, 9, 15, 30, tzinfo=timezone.utc),
    ]
    for idx, order in enumerate(orders):
        if idx < len(june_dates):
            Order.objects.filter(id=order.id).update(created_at=june_dates[idx])
            
    # Now create some May 2026 orders (previous month)
    cust = Customer.objects.first()
    if not cust:
        cust = Customer.objects.create(name='Walk-in Customer', phone='0000000000')
        
    admin_user = User.objects.filter(is_superuser=True).first()
    
    # May Orders (P&L calculations)
    # Order 1: iphone (buy 800, sell 999) + AirPods (buy 180, sell 249) -> Final Amount 1248
    o1 = Order.objects.create(
        customer=cust,
        created_by=admin_user,
        subtotal=1248.00,
        final_amount=1248.00,
        status='Completed'
    )
    Order.objects.filter(id=o1.id).update(created_at=datetime(2026, 5, 10, 10, 0, tzinfo=timezone.utc))
    OrderItem.objects.create(order=o1, product=Product.objects.get(name='iPhone 15 Pro'), quantity=1, price_at_time=999.00)
    OrderItem.objects.create(order=o1, product=Product.objects.get(name='AirPods Pro 2'), quantity=1, price_at_time=249.00)

    # Order 2: Galaxy (buy 950, sell 1199) -> Final Amount 1199
    o2 = Order.objects.create(
        customer=cust,
        created_by=admin_user,
        subtotal=1199.00,
        final_amount=1199.00,
        status='Completed'
    )
    Order.objects.filter(id=o2.id).update(created_at=datetime(2026, 5, 20, 14, 0, tzinfo=timezone.utc))
    OrderItem.objects.create(order=o2, product=Product.objects.get(name='Galaxy S24 Ultra'), quantity=1, price_at_time=1199.00)

    # Order 3: Pixel (buy 700, sell 899) + Adapter (buy 12, sell 19) -> Final Amount 918
    o3 = Order.objects.create(
        customer=cust,
        created_by=admin_user,
        subtotal=918.00,
        final_amount=918.00,
        status='Completed'
    )
    Order.objects.filter(id=o3.id).update(created_at=datetime(2026, 5, 25, 16, 30, tzinfo=timezone.utc))
    OrderItem.objects.create(order=o3, product=Product.objects.get(name='Pixel 8 Pro'), quantity=1, price_at_time=899.00)
    OrderItem.objects.create(order=o3, product=Product.objects.get(name='20W USB-C Power Adapter'), quantity=1, price_at_time=19.00)

    print("Dashboard seeding complete!")

if __name__ == '__main__':
    seed()
