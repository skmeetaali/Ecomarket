from django.db import models
from accounts.models import Buyer
from products.models import Product

# Create your models here.
class Wishlist(models.Model):
    customer = models.OneToOneField(Buyer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    added_at = models.DateTimeField(auto_now_add=True)
    
class Cart(models.Model):
    customer = models.OneToOneField(Buyer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0, blank=True,null=False)
    selected = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)
    
    