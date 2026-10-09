# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "ECOMARKET Details",
            {
                "fields": ("role", "seller_status"),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "ECOMARKET Details",
            {
                "fields": ("role", "seller_status"),
            },
        ),
    )