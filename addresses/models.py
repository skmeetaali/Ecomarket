from django.db import models
from accounts.models import Buyer

# Create your models here.
class address(models.Model):
    customer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    house = models.CharField(max_length=64, null=False)
    city = models.CharField(max_length=64, null=False)
    state = models.CharField(max_length=64, null=False)
    zipcode = models.CharField(max_length=64, null=False)
