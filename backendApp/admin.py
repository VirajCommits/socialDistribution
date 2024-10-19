from django.contrib import admin
from .models import Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('displayName', 'host', 'github','profileImage','page')
    search_fields = ('displayName','github')