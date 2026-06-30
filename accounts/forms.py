from .models import User, Seller, Buyer
from django.contrib.auth.forms import UserCreationForm

class UserSigninForm(UserCreationForm):
    class Meta:
        model = User 
        fields = ["username", "email", "role", "password1", "password2"]
        
