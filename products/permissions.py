from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsApprovedSellerOrReadOnly(BasePermission):
    """
    Anyone can read active products.
    Only approved sellers can create products.
    Sellers can modify only their own products.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        user = request.user

        return (
            user.is_authenticated
            and user.role == 'SELLER'
            and user.seller_status == 'APPROVED'
        )

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.seller_id == request.user.id