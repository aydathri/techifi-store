from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, unique=True)
    avatar = models.ImageField(upload_to="users/images/", null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username




class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username




class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ('can_view', 'Can view'),
            ('can_manage', 'Can manage'),
            ('can_edit', 'Can edit'),
            ('can_delete', 'Can delete'),
            ('can_add', 'Can add'),
        ]

    def __str__(self):
        return self.user.username




class Category(models.Model):
    title = models.CharField(max_length=120)

    def __str__(self):
        return self.title




class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    image = models.ImageField(upload_to="products/images/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title




class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name = 'reviews')
    SCORE_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    score = models.IntegerField(null=False, blank=False, choices=SCORE_CHOICES)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} , {self.product.title} , {self.score or '---'}'




class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} , {self.user.email}'




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICE = [
        ('pending' , 'Pending'),
        ('paid' , 'Paid'),
        ('cancelled' , 'Cancelled'),
        ('confirmed' , 'Confirmed'),
    ]
    status = models.CharField(default = 'pending', blank=True, choices=STATUS_CHOICE)

    @property
    def total_price(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return f'{self.product.title} , {self.quantity}'






class EmailToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


