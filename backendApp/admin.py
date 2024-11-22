from django.contrib import admin
from .models import (
    Author,
    AdminSettings,
    Post,
    FollowRequest,
    Comment,
    Like,
    RemoteNode,
    ToWhichItsConnected,
    GitHubPost,
)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        "displayName",
        "host",
        "github",
        "is_approved",
    )
    search_fields = ("displayName", "github")
    list_filter = ("is_approved",)
    readonly_fields = ("id", "page")
    actions = ["approve_users"]

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Selected users have been approved.")

    approve_users.short_description = "Approve selected users"


@admin.register(AdminSettings)
class AdminSettingsAdmin(admin.ModelAdmin):
    list_display = ("user_approval_required",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "visibility", "published", "edited_at")
    search_fields = ("title", "author__displayName")
    list_filter = ("visibility", "published")
    readonly_fields = ("id", "page", "published", "edited_at")


@admin.register(FollowRequest)
class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ("actor", "object", "accepted", "created_at")
    search_fields = ("actor__displayName", "object__displayName")
    list_filter = ("accepted", "created_at")

    # Remove 'id' from readonly_fields
    readonly_fields = ("created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "content", "published")
    search_fields = ("post__title", "author__displayName", "content")
    list_filter = ("published",)
    readonly_fields = ("id", "published")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("post", "author", "published")
    search_fields = ("post__title", "author__displayName")
    list_filter = ("published",)
    readonly_fields = ("id", "published")



@admin.register(RemoteNode)
class RemoteNodeAdmin(admin.ModelAdmin):
    list_display = ['url', 'username']
    list_filter = ['active']
    search_fields = ['url', 'username']

@admin.register(ToWhichItsConnected)
class ToWhichItsConnected(admin.ModelAdmin):
    list_display = ['url', 'username']
    list_filter = ['active']
    search_fields = ['url', 'username']


@admin.register(GitHubPost)
class GitHubPostAdmin(admin.ModelAdmin):
    list_display = ("author", "activity_type", "created_at", "github_event_id")
    search_fields = ("author__displayName", "activity_type", "github_event_id")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)


# class RemoteNodeAdmin(admin.ModelAdmin):
#     list_display = ("url", "username", "connected")
#     search_fields = ("url",)

#     # Override the save_model method
#     def save_model(self, request, obj, form, change):
#         if not obj._password.startswith(
#             "gAAAA"
#         ):  # Check if the password is already encrypted
#             obj.set_password(obj._password)  # Encrypt the password
#         super().save_model(request, obj, form, change)


# # Register the model with the customized admin class
# admin.site.register(RemoteNode, RemoteNodeAdmin)
