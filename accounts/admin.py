from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Buyer)
admin.site.register(Seller)
admin.site.register(User)