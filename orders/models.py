
from django.conf import settings
from django.db import models
from products.models import Product
from basket.models import ConsolidatedBasket


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "PENDING_PAYMENT", "Pending Payment"
        PAID = "PAID", "Paid"
        PAYMENT_FAILED = "PAYMENT_FAILED", "Payment Failed"
        CANCELLED = "CANCELLED", "Cancelled"

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders"
    )

    basket = models.OneToOneField(
        ConsolidatedBasket,
        on_delete=models.PROTECT,
        related_name="order",
        null=True,
        blank=True,
    )

    class Source(models.TextChoices):
        CART = "CART", "Regular Cart"
        CONSOLIDATED_BASKET = "CONSOLIDATED_BASKET", "Consolidated Basket"

    source = models.CharField(
        max_length=25,
        choices=Source.choices,
        default=Source.CONSOLIDATED_BASKET
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    product_name = models.CharField(max_length=200)
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    quantity = models.PositiveIntegerField()
    weight_at_purchase = models.DecimalField(
        max_digits=6,
        decimal_places=3
    )
    shipping_status = models.CharField(max_length=20)
    expected_delivery_date = models.DateField(
        null=True,
        blank=True
    )

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity


class Payment(models.Model):
    class Status(models.TextChoices):
        CREATED = "CREATED", "Created"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name="payments"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CREATED
    )
    gateway_order_id = models.CharField(
        max_length=100,
        blank=True
    )
    gateway_payment_id = models.CharField(
        max_length=100,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
