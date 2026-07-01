from django.urls import path
from . import views

urlpatterns = [
    path('signup',views.signup, name="signup"),
    path("buyer_signup", views.buyer_signup, name="buyer_signup"),
    path("seller_signup", views.seller_signup, name="seller_signup"),
    path("login/", views.login_view, name="login"),
]