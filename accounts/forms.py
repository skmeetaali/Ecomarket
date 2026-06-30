from .models import User, Seller, Buyer
from django.contrib.auth.forms import UserCreationForm

class UserSigninForm(UserCreationForm):
    class Meta:
        model = User 
        fields = ["username", "email", "role", "password1", "password2"]
        
        
from django import forms
from .models import Buyer

class BuyerSignupForm(forms.ModelForm):
    class Meta:
        model = Buyer
        fields = ["birth_date", "profile_picture"]
        
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }
        
class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Username or Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput
    )
    
    