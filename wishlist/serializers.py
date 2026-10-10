from rest_framework import serializers
from .models import Wishlist, WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )
    price = serializers.DecimalField(
        source="product.price",
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    image = serializers.ImageField(
        source="product.image",
        read_only=True
    )

    class Meta:
        model = WishlistItem
        fields = [
            "id",
            "product",
            "product_name",
            "price",
            "image",
            "added_at",
        ]


class WishlistSerializer(serializers.ModelSerializer):
    items = WishlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "items", "created_at"]