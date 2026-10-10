
from django.urls import path
from . import views

urlpatterns = [
    path("", views.view_basket, name="view_basket"),
    path("items/", views.add_to_basket, name="add_to_basket"),
    path(
        "items/<int:item_id>/",
        views.remove_from_basket,
        name="remove_from_basket"
    ),
    path(
    "items/<int:item_id>/confirm/",
    views.confirm_basket_item,
    name="confirm_basket_item"
    ),
]
