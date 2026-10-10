from django.urls import path
from . import views

urlpatterns = [

    path("checkout/", views.checkout, name="checkout"),
    path("<int:order_id>/pay/", views.initiate_payment, name="initiate_payment"),
    path(
        "payments/<int:payment_id>/confirm/",
        views.confirm_mock_payment,
        name="confirm_mock_payment"
    ),
    path(
    "cart-checkout/",
    views.cart_checkout,
    name="cart_checkout"
    ),
    path("", views.list_orders, name="list_orders"),
    path("<int:order_id>/", views.order_detail, name="order_detail"),
]