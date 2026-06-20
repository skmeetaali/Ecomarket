from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

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
    
    phone_number = PhoneNumberField()    
    profile_picture = models.ImageField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    
    
    
class Buyer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    birth_date = models.DateField(null=True, blank=True)
    
    total_order = models.IntegerField(null=True, blank=True)
    total_spent = models.IntegerField(null=True, blank=True)

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    shop_name = models.CharField(max_length=256, null=True, blank=True, unique=True)
    gst_number = models.CharField(max_length= 15, blank=True, null=True)
    is_gst_registered = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    description = models.CharField(max_length=1024)
    