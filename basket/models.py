
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta

from products.models import Product

class ShippingStatus(models.TextChoices):
    IN_BASKET = "IN_BASKET", "In Basket"
    IN_TRANSIT = "IN_TRANSIT", "Shipping to Godown"
    AT_GODOWN = "AT_GODOWN", "Arrived at Godown"

class ConsolidatedBasket(models.Model):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="consolidated_baskets"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_checked_out = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def total_weight(self):
        return sum(
            (item.product.weight * item.quantity
             for item in self.items.all()),
            start=0
        )

    @property
    def expected_delivery_date(self):
        dates = [
            item.expected_godown_arrival_date
            for item in self.items.all()
            if item.shipping_status in (
                BasketItem.ShippingStatus.IN_TRANSIT,
                BasketItem.ShippingStatus.AT_GODOWN,
            )
            and item.expected_godown_arrival_date is not None
        ]
        return max(dates) + timedelta(days=1) if dates else None

    def __str__(self):
        return f"Consolidated basket - {self.buyer.username}"

class BasketItem(models.Model):
    class ShippingStatus(models.TextChoices):
        IN_BASKET = "IN_BASKET", "In Basket"
        IN_TRANSIT = "IN_TRANSIT", "Shipping to Godown"
        AT_GODOWN = "AT_GODOWN", "Arrived at Godown"

    basket = models.ForeignKey(
        ConsolidatedBasket,
        on_delete=models.CASCADE,
        related_name="items",
        blank=True,
        null=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )
    quantity = models.PositiveIntegerField(default=1)
    price_at_addition = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    expected_delivery_date = models.DateField(null=True, blank=True)
    shipping_status = models.CharField(
        max_length=20,
        choices=ShippingStatus.choices,
        default=ShippingStatus.IN_BASKET
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    expected_godown_arrival_date = models.DateField(
        null=True,
        blank=True
    )
    added_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["basket", "product"],
                name="unique_product_per_basket"
            )
        ]