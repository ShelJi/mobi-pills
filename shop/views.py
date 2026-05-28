from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Product

def home_view(request):
    products = Product.objects.filter(is_visible=True).order_by('-created_at')
    return render(request, 'shop/home.html', {'products': products})

@login_required(login_url='/admin/login/')
def dashboard_view(request):
    return render(request, 'shop/dashboard.html')

@login_required(login_url='/admin/login/')
def products_view(request):
    return render(request, 'shop/products.html')

@login_required(login_url='/admin/login/')
def billing_view(request):
    return render(request, 'shop/billing.html')

@login_required(login_url='/admin/login/')
def sales_view(request):
    return render(request, 'shop/sales.html')

@login_required(login_url='/admin/login/')
def customers_view(request):
    return render(request, 'shop/customers.html')

@login_required(login_url='/admin/login/')
def categories_view(request):
    return render(request, 'shop/categories.html')

@login_required(login_url='/admin/login/')
def suppliers_view(request):
    return render(request, 'shop/suppliers.html')

def login_view(request):
    return redirect('/admin/login/')