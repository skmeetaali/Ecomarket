from .models import User, Seller, Buyer
from django.contrib.auth.forms import UserCreationForm

class UserSigninForm(UserCreationForm):
    class Meta:
        model = User 
        fields = ["email","username","password","confirm_password"]
