
from rest_framework import serializers
from .models import ConsolidatedBasket, BasketItem


class BasketItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )
    price = serializers.DecimalField(
        source="price_at_addition",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    weight = serializers.DecimalField(
        source="product.weight",
        max_digits=6,
        decimal_places=3,
        read_only=True
    )
    image = serializers.ImageField(
        source="product.image",
        read_only=True
    )

    class Meta:
        model = BasketItem
        fields = [
            "id",
            "product",
            "product_name",
            "price",
            "weight",
            "quantity",
            "image",
            "added_at",
            "shipping_status",
            "confirmed_at",
            "expected_godown_arrival_date",
            "expected_delivery_date",
        ]
        read_only_fields = fields


class ConsolidatedBasketSerializer(serializers.ModelSerializer):
    items = BasketItemSerializer(many=True, read_only=True)
    total_weight = serializers.DecimalField(
        max_digits=10,
        decimal_places=3,
        read_only=True
    )
    expected_delivery_date = serializers.DateField(read_only=True)

    class Meta:
        model = ConsolidatedBasket
        fields = [
            "id",
            "created_at",
            "expires_at",
            "is_checked_out",
            "total_weight",
            "expected_delivery_date",
            "items",
        ]
        read_only_fields = fields
