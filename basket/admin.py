from django.contrib import admin
from .models import ConsolidatedBasket, BasketItem

admin.site.register(ConsolidatedBasket)
admin.site.register(BasketItem)