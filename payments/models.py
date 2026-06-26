from django.db import models
from orders.models import Order

# Create your models here.
class Payment(models.Model):       
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_provider = models.CharField(max_length=128)
    transaction_id = models.CharField(max_length=200)
    amount = models.FloatField(blank=True, null=False)
    payment_status = models.CharField(max_length=64)
