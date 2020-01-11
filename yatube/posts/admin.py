from django.contrib import admin
from .models import Post
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "publication_date", "author")
    search_fields = ("text",)
    list_filter = ("publication_date",)
    empty_value_display = "-empty-"

admin.site.register(Post, PostAdmin)    