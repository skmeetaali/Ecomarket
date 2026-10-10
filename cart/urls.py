from django.urls import path
from . import views

urlpatterns = [
    path("", views.view_cart, name="view_cart"),
    path("items/", views.add_to_cart, name="add_to_cart"),
    path(
        "items/<int:item_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),
]