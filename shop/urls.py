from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CategoryViewSet, ProductViewSet, CustomerViewSet, OrderViewSet, UserViewSet
from . import views

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('products/', views.products_view, name='products'),
    path('customers/', views.customers_view, name='customers'),
    path('billing/', views.billing_view, name='billing'),
    path('sales/', views.sales_view, name='sales'),
    path('api/', include(router.urls)),
    path('login/', views.login_view, name='login'),
]
