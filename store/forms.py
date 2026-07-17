# store/forms.py

from django import forms
from products.models import Product, HSNCode


class HSNChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.code} - {obj.description}"


class ProductForm(forms.ModelForm):
    hsn_code = HSNChoiceField(
        queryset=HSNCode.objects.all(),
        widget=forms.Select(attrs={
            "class": "form-select"
        })
    )

    class Meta:
        model = Product
        exclude = ["seller"]

        widgets = {
            "product_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Product Name"
            }),
            "brancd": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Brand"
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4
            }),
            "delivery_days": forms.NumberInput(attrs={
                "class": "form-control"
            }),
            "category": forms.TextInput(attrs={
                "class": "form-control"
            }),
        }
        
        
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
        
class ProductPictureForm(forms.Form):
    pictures = forms.ImageField(
        widget=MultipleFileInput(
            attrs={
                "class": "form-control",
                "accept": "image/*",
            }
        ),
        required=False,
    )
    
    
    