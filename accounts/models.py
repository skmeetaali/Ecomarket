from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        BUYER = "BUYER", "Buyer"
        SELLER = "SELLER", "Seller"
        ADMIN = "ADMIN", "Admin"

    class SellerStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.BUYER,
    )

    seller_status = models.CharField(
        max_length=10,
        choices=SellerStatus.choices,
        default=SellerStatus.PENDING,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"