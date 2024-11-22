from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image =models.CharField(max_length=255, default='images/default.webp')

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Product, through='CartItem')

    def get_cart_total(self):
        return sum(item.get_total() for item in self.cartitem_set.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total(self):
        return self.product.price * self.quantity

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User
    item=models.CharField(max_length=250)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    totalprice=models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    cname = models.CharField(max_length=250)
    phno = models.CharField(max_length=10)
    email = models.EmailField()
    houseno=models.CharField(max_length=250)
    roadno=models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    pin = models.CharField(max_length=6)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=5, default='India')

    def __str__(self):
        return f"{self.cname} ({self.email})"


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')  # Correct use of through model
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default='Pending')

    def __str__(self):
        return f"Order #{self.id} for {self.customer.cname}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total(self):
        return self.product.price * self.quantity  # Correct calculation of total



