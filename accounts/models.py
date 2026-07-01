from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your views here.

class User(AbstractUser):
    class Role(models.TextChoices):
        BUYER = 'BUYER', 'buyer',
        SELLER = "SELLER", 'seller'
        
    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.BUYER
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    email = models.EmailField(unique=True)

    
    
class Buyer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(null=True, blank=True)
    total_order = models.IntegerField(null=True, blank=True)
    total_spent = models.IntegerField(null=True, blank=True)
    

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_picture = models.ImageField(null=True, blank=True)
    shop_name = models.CharField(max_length=256, null=True, blank=True, unique=True)
    gst_number = models.CharField(max_length= 15, blank=True, null=True)
    is_gst_registered = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    description = models.CharField(max_length=1024)
    