from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(
        source='seller.username',
        read_only=True,
    )
    category_name = serializers.CharField(
        source='category.name',
        read_only=True,
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'seller',
            'seller_name',
            'category',
            'category_name',
            'name',
            'description',
            'price',
            'weight',
            'stock',
            'delivery_rate_per_kg',
            'godown_delivery_days',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'seller',
            'seller_name',
            'created_at',
            'updated_at',
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Price must be greater than zero.'
            )
        return value

    def validate_weight(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Weight must be greater than zero.'
            )
        return value

    def validate_delivery_rate_per_kg(self, value):
        if value < 10 or value > 15:
            raise serializers.ValidationError(
                'Delivery rate must be between ₹10 and ₹15 per kg.'
            )
        return value