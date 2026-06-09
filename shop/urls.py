from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CategoryViewSet, ProductViewSet, CustomerViewSet, OrderViewSet, UserViewSet, SupplierViewSet, productive_dashboard_data, create_expense_api
from . import views

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'suppliers', SupplierViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('productive-dashboard/', views.productive_dashboard_view, name='productive_dashboard'),
    path('api/productive-dashboard/', productive_dashboard_data, name='productive_dashboard_data'),
    path('api/productive-dashboard/create-expense/', create_expense_api, name='create_expense_api'),
    path('products/', views.products_view, name='products'),
    path('customers/', views.customers_view, name='customers'),
    path('suppliers/', views.suppliers_view, name='suppliers'),
    path('billing/', views.billing_view, name='billing'),
    path('billing/change_customer/<int:order_id>/', views.change_customer_view, name='change_customer'),
    path('sales/', views.sales_view, name='sales'),
    path('sales/invoice/<int:order_id>/', views.invoice_detail_view, name='invoice_detail'),
    path('categories/', views.categories_view, name='categories'),
    path('api/', include(router.urls)),
    path('login/', views.login_view, name='login'),
]
