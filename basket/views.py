from datetime import timedelta
from decimal import Decimal

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product
from .models import ConsolidatedBasket, BasketItem
from .serializers import ConsolidatedBasketSerializer
from .serializers import BasketItemSerializer



MAX_BASKET_WEIGHT = Decimal("5.000")
MAX_PRODUCT_WEIGHT = Decimal("3.000")


def get_active_basket(user):
    if user.role != "BUYER":
        return None

    basket = ConsolidatedBasket.objects.filter(
        buyer=user,
        is_checked_out=False,
        expires_at__gt=timezone.now()
    ).order_by("-created_at").first()

    if basket is None:
        basket = ConsolidatedBasket.objects.create(
            buyer=user,
            expires_at=timezone.now() + timedelta(days=14)
        )

    return basket


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_basket(request):
    basket = get_active_basket(request.user)

    if basket is None:
        return Response(
            {"error": "Only buyers can access a consolidated basket."},
            status=status.HTTP_403_FORBIDDEN
        )

    return Response(ConsolidatedBasketSerializer(basket).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_basket(request):
    basket = get_active_basket(request.user)

    if basket is None:
        return Response(
            {"error": "Only buyers can use a consolidated basket."},
            status=status.HTTP_403_FORBIDDEN
        )

    product_id = request.data.get("product")
    quantity = request.data.get("quantity", 1)

    if product_id is None:
        return Response(
            {"error": "Product ID is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return Response(
            {"error": "Quantity must be a positive integer."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if quantity < 1:
        return Response(
            {"error": "Quantity must be at least 1."},
            status=status.HTTP_400_BAD_REQUEST
        )

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    if product.weight >= MAX_PRODUCT_WEIGHT:
        return Response(
            {"error": "Products weighing 3 kg or more are ineligible."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if product.stock < quantity:
        return Response(
            {"error": "Not enough stock available."},
            status=status.HTTP_400_BAD_REQUEST
        )

    existing_item = BasketItem.objects.filter(
        basket=basket,
        product=product
    ).first()

    old_quantity = existing_item.quantity if existing_item else 0
    new_quantity = old_quantity + quantity

    other_items_weight = sum(
        (
            item.product.weight * item.quantity
            for item in basket.items.exclude(product=product)
        ),
        Decimal("0")
    )

    proposed_weight = (
        other_items_weight + product.weight * new_quantity
    )

    if proposed_weight > MAX_BASKET_WEIGHT:
        return Response(
            {
                "error": "Basket weight cannot exceed 5 kg.",
                "current_weight": str(basket.total_weight),
                "proposed_weight": str(proposed_weight),
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if existing_item:
        existing_item.quantity = new_quantity
        existing_item.save()
        item = existing_item
    else:
        expected_date = (
            timezone.localdate()
            + timedelta(days=product.godown_delivery_days + 1)
        )

        item = BasketItem.objects.create(
            basket=basket,
            product=product,
            quantity=quantity,
            price_at_addition=product.price,
            expected_delivery_date=expected_date,
        )

    return Response(
        {
            "message": "Product added to consolidated basket.",
            "item_id": item.id,
            "basket": ConsolidatedBasketSerializer(basket).data,
        },
        status=status.HTTP_201_CREATED
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_basket(request, item_id):
    basket = get_active_basket(request.user)

    if basket is None:
        return Response(
            {"error": "Only buyers can modify a basket."},
            status=status.HTTP_403_FORBIDDEN
        )

    item = get_object_or_404(
        BasketItem,
        id=item_id,
        basket=basket
    )

    if item.shipping_status != BasketItem.ShippingStatus.IN_BASKET:
        return Response(
            {
                "error": (
                    "This item cannot be removed because shipping "
                    "has already been initiated."
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    item.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_basket_item(request, item_id):
    if request.user.role != "BUYER":
        return Response(
            {"error": "Only buyers can confirm basket items."},
            status=status.HTTP_403_FORBIDDEN
        )

    item = get_object_or_404(
        BasketItem,
        id=item_id,
        basket__buyer=request.user
    )

    basket = item.basket

    if basket.is_checked_out:
        return Response(
            {"error": "This basket has already been checked out."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if basket.is_expired:
        return Response(
            {"error": "This basket has expired."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if item.shipping_status != BasketItem.ShippingStatus.IN_BASKET:
        return Response(
            {"error": "This item has already been confirmed."},
            status=status.HTTP_400_BAD_REQUEST
        )

    arrival_date = (
        timezone.localdate()
        + timedelta(days=item.product.godown_delivery_days)
    )

    item.shipping_status = BasketItem.ShippingStatus.IN_TRANSIT
    item.confirmed_at = timezone.now()
    item.expected_godown_arrival_date = arrival_date
    item.expected_delivery_date = arrival_date + timedelta(days=1)

    item.save(update_fields=[
        "shipping_status",
        "confirmed_at",
        "expected_godown_arrival_date",
        "expected_delivery_date",
    ])

    return Response(
        {
            "message": "Item confirmed. Shipping to the godown has been initiated.",
            "item": BasketItemSerializer(item).data,
        },
        status=status.HTTP_200_OK
    )