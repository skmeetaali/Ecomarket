from django.db import models
from accounts.models import Buyer
from products.models import Product

# Create your models here.
class Order(models.Model):
    customer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=200, null=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    
