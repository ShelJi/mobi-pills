from .models import Product

def low_stock_products(request):
    """
    Context processor to provide low stock product information to all templates.
    Products with stock_quantity < 5 are considered low stock.
    """
    LOW_STOCK_THRESHOLD = 5
    low_stock_items = Product.objects.filter(
        stock_quantity__lt=LOW_STOCK_THRESHOLD
    ).order_by('stock_quantity')
    
    return {
        'low_stock_products': low_stock_items,
        'low_stock_count': low_stock_items.count(),
        'low_stock_threshold': LOW_STOCK_THRESHOLD,
    }
