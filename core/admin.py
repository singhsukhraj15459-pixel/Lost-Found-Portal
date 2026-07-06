from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, LostItem, FoundItem, Message, MatchNotification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('mobile_number', 'profile_photo')}),
    )
    list_display = ('email', 'username', 'is_staff', 'is_active')


admin.site.register(Category)
admin.site.register(LostItem)
admin.site.register(FoundItem)
admin.site.register(Message)
admin.site.register(MatchNotification)