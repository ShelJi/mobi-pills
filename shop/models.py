from django.db import models
from django.contrib.auth.models import User
import uuid

from PIL import Image, ImageOps
from django.core.files.base import ContentFile
from io import BytesIO
import os


class Category(models.Model):
    name = models.CharField(max_length=100)
    # description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        
class Supplier(models.Model):
    name = models.CharField(max_length=200)
    # description = models.TextField(blank=True, null=True)
    # company_name = models.CharField(max_length=200, blank=True, null=True)
    phone1 = models.CharField(max_length=20, blank=True, null=True)
    phone2 = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    name = models.CharField(max_length=200)
    # description = models.TextField(blank=True, null=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100, blank=True, null=True)
    imei = models.CharField(max_length=50, blank=True, null=True, help_text="Optional IMEI number")
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, related_name='products')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    is_visible = models.BooleanField(default=True)
    quick_product = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        if self.image:

            img = Image.open(self.image)

            # Auto rotate using EXIF
            img = ImageOps.exif_transpose(img)

            # Preserve transparency
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")

            # Resize image
            max_size = (800, 800)
            img.thumbnail(
                max_size,
                Image.Resampling.LANCZOS
            )

            # Convert to WEBP
            img_io = BytesIO()

            img.save(
                img_io,
                format="WEBP",
                quality=75,
                optimize=True,
                method=6,
            )

            img_io.seek(0)

            # Rename file
            file_name = os.path.splitext(
                self.image.name
            )[0] + ".webp"

            # Replace image
            self.image = ContentFile(
                img_io.getvalue(),
                name=file_name
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand} {self.name}"

class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"

class Order(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='orders')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number and self.status == 'Completed':
            # Generate unique invoice number only when completed, or generate temp one for draft
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.invoice_number or self.id} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the product when the order was placed")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.price_at_time
