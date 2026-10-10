from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product
from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer


def get_buyer_wishlist(user):
    if user.role != "BUYER":
        return None

    wishlist, _ = Wishlist.objects.get_or_create(buyer=user)
    return wishlist


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def view_wishlist(request):
    wishlist = get_buyer_wishlist(request.user)

    if wishlist is None:
        return Response(
            {"error": "Only buyers can access a wishlist."},
            status=status.HTTP_403_FORBIDDEN
        )

    return Response(WishlistSerializer(wishlist).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_to_wishlist(request):
    wishlist = get_buyer_wishlist(request.user)

    if wishlist is None:
        return Response(
            {"error": "Only buyers can manage a wishlist."},
            status=status.HTTP_403_FORBIDDEN
        )

    product_id = request.data.get("product")

    if product_id is None:
        return Response(
            {"error": "Product ID is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )

    return Response(
        {
            "message": (
                "Product added to wishlist."
                if created else "Product is already in your wishlist."
            ),
            "wishlist": WishlistSerializer(wishlist).data
        },
        status=(
            status.HTTP_201_CREATED
            if created else status.HTTP_200_OK
        )
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def remove_from_wishlist(request, item_id):
    wishlist = get_buyer_wishlist(request.user)

    if wishlist is None:
        return Response(
            {"error": "Only buyers can manage a wishlist."},
            status=status.HTTP_403_FORBIDDEN
        )

    item = get_object_or_404(
        WishlistItem,
        id=item_id,
        wishlist=wishlist
    )
    item.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)