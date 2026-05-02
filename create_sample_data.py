import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mobi_pills.settings')
django.setup()

from django.contrib.auth.models import User
from shop.models import Category, Product

def run():
    # Create Superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Superuser created: admin / admin123")

    # Create Category
    cat1, _ = Category.objects.get_or_create(name='Smartphones', description='Mobile Phones')
    cat2, _ = Category.objects.get_or_create(name='Accessories', description='Chargers, Cases, etc.')

    # Create Products
    products_data = [
        {'name': 'iPhone 15 Pro', 'brand': 'Apple', 'imei': '358901234567890', 'price': 999.00, 'stock_quantity': 10, 'category': cat1},
        {'name': 'Galaxy S24 Ultra', 'brand': 'Samsung', 'imei': '351234567890123', 'price': 1199.00, 'stock_quantity': 5, 'category': cat1},
        {'name': 'AirPods Pro 2', 'brand': 'Apple', 'imei': '', 'price': 249.00, 'stock_quantity': 20, 'category': cat2},
        {'name': '20W USB-C Power Adapter', 'brand': 'Apple', 'imei': '', 'price': 19.00, 'stock_quantity': 50, 'category': cat2},
        {'name': 'Pixel 8 Pro', 'brand': 'Google', 'imei': '359876543210987', 'price': 899.00, 'stock_quantity': 3, 'category': cat1},
    ]

    for p in products_data:
        Product.objects.get_or_create(name=p['name'], defaults=p)
    print("Sample data created.")

if __name__ == '__main__':
    run()
