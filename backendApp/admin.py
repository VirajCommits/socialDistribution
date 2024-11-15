from django.contrib import admin
from .models import Author
from .models import AdminSettings, RemoteNode

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


class RemoteNodeAdmin(admin.ModelAdmin):
    list_display = ("url", "username", "connected")
    search_fields = ("url",)

    # Override the save_model method
    def save_model(self, request, obj, form, change):
        if not obj._password.startswith(
            "gAAAA"
        ):  # Check if the password is already encrypted
            obj.set_password(obj._password)  # Encrypt the password
        super().save_model(request, obj, form, change)


# Register the model with the customized admin class
admin.site.register(RemoteNode, RemoteNodeAdmin)
