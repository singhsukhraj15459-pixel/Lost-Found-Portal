from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from .models import User, Category, LostItem, FoundItem, Message, MatchNotification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('mobile_number', 'profile_photo')}),
    )
    list_display = ('email', 'username', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    actions = ['suspend_users', 'reactivate_users']

    @admin.action(description="Suspend selected users")
    def suspend_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} user(s) suspended.")

    @admin.action(description="Reactivate selected users")
    def reactivate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} user(s) reactivated.")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'lost_item_count', 'found_item_count')
    search_fields = ('category_name',)

    def lost_item_count(self, obj):
        return obj.lostitem_set.count()
    lost_item_count.short_description = "Lost Reports"

    def found_item_count(self, obj):
        return obj.founditem_set.count()
    found_item_count.short_description = "Found Reports"


@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'area', 'status', 'created_at')
    list_filter = ('status', 'category', 'area')
    search_fields = ('title', 'description', 'area', 'user__email')
    actions = ['mark_recovered', 'delete_selected_reports']
    date_hierarchy = 'created_at'

    @admin.action(description="Mark selected items as Recovered")
    def mark_recovered(self, request, queryset):
        updated = queryset.update(status='recovered')
        self.message_user(request, f"{updated} item(s) marked as recovered.")

    @admin.action(description="Delete selected reports (e.g. fake listings)")
    def delete_selected_reports(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} report(s) deleted.")


@admin.register(FoundItem)
class FoundItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'area', 'status', 'created_at')
    list_filter = ('status', 'category', 'area')
    search_fields = ('title', 'description', 'area', 'user__email')
    actions = ['mark_recovered', 'delete_selected_reports']
    date_hierarchy = 'created_at'

    @admin.action(description="Mark selected items as Recovered")
    def mark_recovered(self, request, queryset):
        updated = queryset.update(status='recovered')
        self.message_user(request, f"{updated} item(s) marked as recovered.")

    @admin.action(description="Delete selected reports (e.g. fake listings)")
    def delete_selected_reports(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} report(s) deleted.")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'short_message', 'timestamp', 'is_read')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__email', 'receiver__email', 'message')

    def short_message(self, obj):
        return obj.message[:50]
    short_message.short_description = "Message"


@admin.register(MatchNotification)
class MatchNotificationAdmin(admin.ModelAdmin):
    list_display = ('lost_item', 'found_item', 'created_at', 'is_seen')
    list_filter = ('is_seen', 'created_at')