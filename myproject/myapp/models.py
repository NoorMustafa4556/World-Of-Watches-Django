from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User Model (if extending)
class User(AbstractUser):
    
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)


    def __str__(self):
        return self.email


class Watch(models.Model):
    CATEGORY_CHOICES = [
        ('Analog', 'Analog'),
        ('Digital', 'Digital'),
        ('Sports', 'Sports'),
    ]

    watch_name = models.CharField(max_length=100)
    watch_description = models.TextField(blank=True, null=True)
    watch_price = models.DecimalField(max_digits=10, decimal_places=2)
    watch_brand = models.CharField(max_length=100)
    watch_image = models.ImageField(upload_to='watch_images/', null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Analog')

    def __str__(self):
        return f"{self.watch_brand} - {self.watch_name} ({self.category})"



class ManualPaymentMethod(models.Model):
    name = models.CharField(max_length=50) # e.g., JazzCash
    account_title = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE, related_name='orders')
    
    status_choices = [
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled')
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Cash on Delivery', 'Cash on Delivery'),
        ('Online Payment', 'Online Payment'),
    ]

    status = models.CharField(max_length=10, choices=status_choices, default='PENDING')
    order_date = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1, null=True)
    address = models.TextField(default='Not Provided') 
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHOD_CHOICES)
    
    # Linked to dynamic payment methods
    online_wallet = models.ForeignKey(ManualPaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    payment_screenshot = models.ImageField(upload_to='payment_screenshots/', null=True, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"
    


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    message = models.TextField()
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)

    def __str__(self):
        return self.name



class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Cart"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    watch = models.ForeignKey(Watch, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.watch.watch_name}"

    def total_price(self):
        return self.quantity * self.watch.watch_price
