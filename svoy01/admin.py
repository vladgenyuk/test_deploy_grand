from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name')
    search_fields = ('name',)


class PostImageAdmin(admin.StackedInline):
    model = PostImage
    readonly_fields = ('id', 'get_html_photo')

    def get_html_photo(self, object):
        if object.image:
            return mark_safe(f"<img src='{object.image.url}' width=50>")

    get_html_photo.short_description = 'image'


class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", 'slug', 'cost', 'cat', 'get_html_photo', 'author' )
    list_display_links = ("id", "title")
    search_fields = ('title', 'text')
    prepopulated_fields = {"slug": ("title",)}
    fields = ('title', 'slug', 'cost', 'text', 'condition', 'cat', 'get_html_photo', )
    readonly_fields = ('id', 'get_html_photo', )
    save_on_top = True
    inlines = [PostImageAdmin]

    def get_html_photo(self, object):
        if object.photo:
            return mark_safe(f"<img src='{object.photo.url}' width=50>")

    get_html_photo.short_description = 'photo'

    class Meta:
        model = Product


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'photo', )
    list_display_links = ('user', 'photo', )


class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat_id', 'author', 'text', 'created')


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Messages, MessageAdmin)
admin.site.register(Chat)
