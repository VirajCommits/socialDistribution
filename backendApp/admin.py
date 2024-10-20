from django.contrib import admin
from .models import Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    # Display fields
    list_display = ('displayName', 'host', 'github')
    search_fields = ('displayName', 'github')

    # Read-only fields
    readonly_fields = ('uuid', 'id', 'page')

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.id = f"{obj.host}api/authors/{obj.uuid}"
        super().save_model(request, obj, form, change)
