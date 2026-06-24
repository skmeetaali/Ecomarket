from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Cart)
admin.site.register(Wishlist)
admin.site.register(CartItem)
admin.site.register(WishlistItem)