from django.contrib import admin
from .models import Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id','displayName', 'host', 'github','profileImage','page')
    search_fields = ('displayName', 'id','github')