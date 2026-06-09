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

from django.shortcuts import get_object_or_404
from .models import Order, Customer

@login_required(login_url='/admin/login/')
def invoice_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    customers = Customer.objects.all()
    return render(request, 'shop/invoice_detail.html', {'order': order, 'customers': customers})

@login_required(login_url='/admin/login/')
def change_customer_view(request, order_id):
    if request.method == 'POST' and request.user.is_staff:
        customer_id = request.POST.get('customer_id')
        try:
            new_customer = Customer.objects.get(id=customer_id)
            order = Order.objects.get(id=order_id)
            order.customer = new_customer
            order.save()
        except Customer.DoesNotExist:
            pass
        except Order.DoesNotExist:
            pass
    return redirect('invoice_detail', order_id=order_id)

@login_required(login_url='/admin/login/')
def customers_view(request):
    return render(request, 'shop/customers.html')

@login_required(login_url='/admin/login/')
def categories_view(request):
    return render(request, 'shop/categories.html')

@login_required(login_url='/admin/login/')
def suppliers_view(request):
    return render(request, 'shop/suppliers.html')

@login_required(login_url='/admin/login/')
def productive_dashboard_view(request):
    return render(request, 'shop/productive_dashboard.html')

def login_view(request):
    return redirect('/admin/login/')