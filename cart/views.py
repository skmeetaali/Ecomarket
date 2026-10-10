from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product
from .models import Cart, CartItem
from .serializers import CartSerializer


def get_buyer_cart(user):
    if user.role != "BUYER":
        return None
    cart, _ = Cart.objects.get_or_create(buyer=user)
    return cart


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_cart(request):
    cart = get_buyer_cart(request.user)

    if cart is None:
        return Response(
            {"error": "Only buyers can access a cart."},
            status=status.HTTP_403_FORBIDDEN
        )

    return Response(CartSerializer(cart).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    cart = get_buyer_cart(request.user)

    if cart is None:
        return Response(
            {"error": "Only buyers can add items to a cart."},
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

    if product.stock < quantity:
        return Response(
            {"error": "Not enough stock available."},
            status=status.HTTP_400_BAD_REQUEST
        )

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity}
    )

    if not created:
        new_quantity = item.quantity + quantity

        if new_quantity > product.stock:
            return Response(
                {"error": "Requested quantity exceeds available stock."},
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = new_quantity
        item.save()

    return Response(
        {
            "message": "Item added to cart.",
            "item": CartSerializer(cart).data
        },
        status=status.HTTP_201_CREATED
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    cart = get_buyer_cart(request.user)

    if cart is None:
        return Response(
            {"error": "Only buyers can manage a cart."},
            status=status.HTTP_403_FORBIDDEN
        )

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )
    item.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
