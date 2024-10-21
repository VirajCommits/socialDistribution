from django.contrib import admin
from .models import Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('displayName', 'host', 'github')
    search_fields = ('displayName','github')

    # Read-only fields
    readonly_fields = ('id', 'page')
