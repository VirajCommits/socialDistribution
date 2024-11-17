from django.contrib import admin
from .models import Author, RemoteNode, toWhichitsConnected
from .models import AdminSettings

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "displayName",
        "host",
        "github",
        "is_approved",
    )  # Added 'is_approved'
    search_fields = ("displayName", "github")
    list_filter = ("is_approved",)  # Added filter to easily filter by approval status

    # Read-only fields
    readonly_fields = ("id", "page")

    # Custom action to approve users
    actions = ["approve_users"]

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected users have been approved.")

    approve_users.short_description = "Approve selected users"


@admin.register(AdminSettings)
class AdminSettingsAdmin(admin.ModelAdmin):
    list_display = ("user_approval_required",)

@admin.register(RemoteNode)
class RemoteNodeAdmin(admin.ModelAdmin):
    list_display = ['url', 'username']
    list_filter = ['username']
    search_fields = ['url', 'username']

@admin.register(toWhichitsConnected)
class towhichitsconnected(admin.ModelAdmin):
    list_display = ['url', 'username']
    list_filter = ['username']
    search_fields = ['url', 'username']
