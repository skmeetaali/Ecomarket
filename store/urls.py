from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("seller_dashboard/",views.seller_dashboard, name="seller_dashboard"),
    path("buyer_dashboard/",views.buyer_dashboard, name="buyer_dashboard"),
    path("add_product", views.add_product, name="add_product")
]