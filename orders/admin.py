
from django.contrib import admin
from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "product",
        "product_name",
        "price_at_purchase",
        "quantity",
        "weight_at_purchase",
        "shipping_status",
        "expected_delivery_date",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "buyer",
        "source",
        "status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "source", "created_at")
    search_fields = ("buyer__username", "buyer__email")
    readonly_fields = ("created_at",)
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("order__id", "order__buyer__username")
    readonly_fields = (
        "order",
        "amount",
        "status",
        "gateway_order_id",
        "gateway_payment_id",
        "created_at",
        "updated_at",
    )
