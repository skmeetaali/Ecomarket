from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from basket.models import ConsolidatedBasket, BasketItem
from .models import Order, OrderItem, Payment

from cart.models import Cart, CartItem
from products.models import Product


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def checkout(request):
    if request.user.role != "BUYER":
        return Response(
            {"error": "Only buyers can checkout."},
            status=status.HTTP_403_FORBIDDEN
        )

    with transaction.atomic():
        basket = get_object_or_404(
            ConsolidatedBasket.objects.select_for_update(),
            buyer=request.user,
            is_checked_out=False,
            expires_at__gt=timezone.now()
        )

        if hasattr(basket, "order"):
            return Response(
                {"error": "An order already exists for this basket."},
                status=status.HTTP_400_BAD_REQUEST
            )

        confirmed_items = list(
            BasketItem.objects.select_for_update().filter(
                basket=basket,
                shipping_status__in=[
                    BasketItem.ShippingStatus.IN_TRANSIT,
                    BasketItem.ShippingStatus.AT_GODOWN,
                ]
            ).select_related("product")
        )

        if not confirmed_items:
            return Response(
                {"error": "No confirmed items are available for checkout."},
                status=status.HTTP_400_BAD_REQUEST
            )

        product_total = sum(
            (
                item.price_at_addition * item.quantity
                for item in confirmed_items
            ),
            Decimal("0.00")
        )

        delivery_total = sum(
            (
                item.product.delivery_rate_per_kg
                * item.product.weight
                * item.quantity
                for item in confirmed_items
            ),
            Decimal("0.00")
        )

        total_amount = product_total + delivery_total

        order = Order.objects.create(
            buyer=request.user,
            basket=basket,
            total_amount=total_amount,
            status=Order.Status.PENDING_PAYMENT
        )

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price_at_purchase=item.price_at_addition,
                quantity=item.quantity,
                weight_at_purchase=item.product.weight,
                shipping_status=item.shipping_status,
                expected_delivery_date=item.expected_delivery_date,
            )
            for item in confirmed_items
        ])

        basket.is_checked_out = True
        basket.save(update_fields=["is_checked_out"])

    return Response(
        {
            "message": "Order created. Payment is pending.",
            "order_id": order.id,
            "status": order.status,
            "total_amount": str(order.total_amount),
            "items": [
                {
                    "product": item.product_name,
                    "quantity": item.quantity,
                    "subtotal": str(item.subtotal),
                    "shipping_status": item.shipping_status,
                    "expected_delivery_date": (
                        item.expected_delivery_date
                    ),
                }
                for item in order.items.all()
            ],
        },
        status=status.HTTP_201_CREATED
    )





@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initiate_payment(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        buyer=request.user
    )

    if order.status != Order.Status.PENDING_PAYMENT:
        return Response(
            {"error": "This order is not awaiting payment."},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            status=Payment.Status.CREATED
        )

    return Response(
        {
            "message": "Mock payment initiated.",
            "payment_id": payment.id,
            "order_id": order.id,
            "amount": str(payment.amount),
            "status": payment.status,
            "mode": "MOCK"
        },
        status=status.HTTP_201_CREATED
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_mock_payment(request, payment_id):
    outcome = request.data.get("outcome")

    if outcome not in ["SUCCESS", "FAILED"]:
        return Response(
            {"error": "outcome must be SUCCESS or FAILED."},
            status=status.HTTP_400_BAD_REQUEST
        )

    with transaction.atomic():
        payment = get_object_or_404(
            Payment.objects.select_for_update(),
            id=payment_id,
            order__buyer=request.user
        )

        if payment.status != Payment.Status.CREATED:
            return Response(
                {"error": "This payment has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = payment.order

        if order.status != Order.Status.PENDING_PAYMENT:
            return Response(
                {"error": "This order is not awaiting payment."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if outcome == "SUCCESS":
            order_items = list(order.items.all())

            if not order_items:
                return Response(
                    {"error": "Cannot pay for an order with no items."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Aggregate quantities in case a product appears
            # in more than one order item.
            required_stock = {}

            for item in order_items:
                required_stock[item.product_id] = (
                    required_stock.get(item.product_id, 0)
                    + item.quantity
                )

            # Lock product rows in a consistent order.
            products = Product.objects.select_for_update().filter(
                id__in=sorted(required_stock.keys())
            ).order_by("id")

            products_by_id = {
                product.id: product for product in products
            }

            # Validate all products before changing any stock.
            for product_id, quantity in required_stock.items():
                product = products_by_id.get(product_id)

                if product is None or not product.is_active:
                    return Response(
                        {"error": "A product in this order is unavailable."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if product.stock < quantity:
                    return Response(
                        {
                            "error": (
                                f"Insufficient stock for {product.name}. "
                                f"Available: {product.stock}, "
                                f"required: {quantity}."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Deduct stock only after all products pass validation.
            for product_id, quantity in required_stock.items():
                product = products_by_id[product_id]
                product.stock -= quantity
                product.save(update_fields=["stock"])

            payment.status = Payment.Status.SUCCESS
            order.status = Order.Status.PAID

        else:
            payment.status = Payment.Status.FAILED

        payment.save(update_fields=["status", "updated_at"])

        if outcome == "SUCCESS":
            order.save(update_fields=["status"])

    return Response(
        {
            "message": (
                "Mock payment successful."
                if outcome == "SUCCESS"
                else "Mock payment failed."
            ),
            "payment_id": payment.id,
            "payment_status": payment.status,
            "order_id": order.id,
            "order_status": order.status
        },
        status=status.HTTP_200_OK
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cart_checkout(request):
    if request.user.role != "BUYER":
        return Response(
            {"error": "Only buyers can checkout."},
            status=status.HTTP_403_FORBIDDEN
        )

    with transaction.atomic():
        cart = get_object_or_404(
            Cart.objects.select_for_update(),
            buyer=request.user
        )

        cart_items = list(
            CartItem.objects.select_for_update()
            .filter(cart=cart)
            .select_related("product")
        )

        if not cart_items:
            return Response(
                {"error": "Your cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate products and stock before creating the order.
        for item in cart_items:
            product = item.product

            if not product.is_active:
                return Response(
                    {"error": f"{product.name} is no longer available."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if item.quantity > product.stock:
                return Response(
                    {"error": f"Insufficient stock for {product.name}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        product_total = sum(
            (
                item.product.price * item.quantity
                for item in cart_items
            ),
            Decimal("0.00")
        )
        delivery_total = Decimal("69.00") * sum(
            item.quantity for item in cart_items
        )

        total_amount = product_total + delivery_total

        order = Order.objects.create(
            buyer=request.user,
            basket=None,
            source=Order.Source.CART,
            total_amount=total_amount,
            status=Order.Status.PENDING_PAYMENT
        )

        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price_at_purchase=item.product.price,
                quantity=item.quantity,
                weight_at_purchase=item.product.weight,
                shipping_status="IN_BASKET",
                expected_delivery_date=None,
            )
            for item in cart_items
        ])

        # Remove cart items only after the order has been created.
        CartItem.objects.filter(cart=cart).delete()

    return Response(
        {
            "message": "Cart order created. Payment is pending.",
            "order_id": order.id,
            "source": order.source,
            "status": order.status,
            "product_total": str(product_total),
            "delivery_total": str(delivery_total),
            "total_amount": str(order.total_amount),
            "items": [
                {
                    "product": item.product_name,
                    "quantity": item.quantity,
                    "subtotal": str(item.subtotal),
                }
                for item in order.items.all()
            ],
        },
        status=status.HTTP_201_CREATED
    )



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_orders(request):
    if request.user.role != "BUYER":
        return Response(
            {"error": "Only buyers can view their orders."},
            status=403
        )

    orders = Order.objects.filter(
        buyer=request.user
    ).order_by("-created_at")

    data = []

    for order in orders:
        items = []

        for item in order.items.all():
            items.append({
                "product_name": item.product_name,
                "price_at_purchase": str(item.price_at_purchase),
                "quantity": item.quantity,
                "subtotal": str(item.subtotal),
                "shipping_status": item.shipping_status,
                "expected_delivery_date": item.expected_delivery_date,
            })

        data.append({
            "id": order.id,
            "source": order.source,
            "status": order.status,
            "total_amount": str(order.total_amount),
            "created_at": order.created_at,
            "items": items,
        })

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    if request.user.role != "BUYER":
        return Response(
            {"error": "Only buyers can view order details."},
            status=403
        )

    order = get_object_or_404(
        Order,
        id=order_id,
        buyer=request.user
    )

    items = []

    for item in order.items.all():
        items.append({
            "product_name": item.product_name,
            "price_at_purchase": str(item.price_at_purchase),
            "quantity": item.quantity,
            "subtotal": str(item.subtotal),
            "shipping_status": item.shipping_status,
            "expected_delivery_date": item.expected_delivery_date,
        })

    return Response({
        "id": order.id,
        "source": order.source,
        "status": order.status,
        "total_amount": str(order.total_amount),
        "created_at": order.created_at,
        "items": items,
    })
