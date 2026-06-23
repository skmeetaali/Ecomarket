from django.db import models
from accounts.models import Seller

# Create your models here.
class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    product_id = models.UUIDField(primary_key=True)
    product_name = models.CharField(max_length=128, unique=True, blank = True, null = True)
    brancd = models.CharField(max_length=64, blank = True, null = True)
    price = models.FloatField(blank=True)
    description = models.CharField(max_length=1024)
    delivery_days = models.IntegerField(blank=True)
    category = models.CharField(max_length= 64, blank = True, null = True)
    hsn_code = models.ForeignKey("HSNCode",on_delete=models.PROTECT)  
    
    def __str__(self):
        return self.product_name  
    
class Product_picturs(models.Model):
    product_id = models.ForeignKey(Product, primary_key=True, on_delete=models.CASCADE)
    picture = models.ImageField()
    is_default = models.BooleanField(default=False)
    

class HSNCode(models.Model):
    code = models.CharField(max_length=8)
    description = models.TextField()

class GSTRate(models.Model):
    hsn_code = models.ForeignKey(HSNCode, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=5, decimal_places=2)
    effective_from = models.DateField()
    effective_to = models.DateField(null=True)
    