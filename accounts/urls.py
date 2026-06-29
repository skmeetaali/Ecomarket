from django.urls import path
from . import views

urlpatterns = [
    path('signup',name='signup'),
    path('signup',views.signup, name="signup"),
]