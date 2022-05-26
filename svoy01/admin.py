from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *


# class productAdmin(admin.ModelAdmin):
#     list_display = ("id", "title", 'slug', 'cost', 'cat', 'get_html_photo')
#     list_display_links = ("id", "title")
#     search_fields = ('title', 'text')
#     prepopulated_fields = {"slug": ("title",)}
#     fields = ('title', 'slug', 'cost', 'text', 'condition', 'cat', 'get_html_photo',)
#     readonly_fields = ('text', 'get_html_photo')
#     save_on_top = True
#
#     def get_html_photo(self, object):
#         if object.photo:
#             return mark_safe(f"<img src='{object.photo.url}' width=50>")
#
#     get_html_photo.short_description = 'photo'
#
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name')
    search_fields = ('name',)
#
#
# admin.site.register(Category, CategoryAdmin)
# admin.site.register(product, productAdmin)
#
#
# admin.site.site_title = 'Админ-панель 1'
# admin.site.site_header = 'Админ-панель 2'


class PostImageAdmin(admin.StackedInline):
    model = PostImage
    readonly_fields = ('id', 'get_html_photo')

    def get_html_photo(self, object):
        if object.image:
            return mark_safe(f"<img src='{object.image.url}' width=50>")

    get_html_photo.short_description = 'image'


class PostAdmin(admin.ModelAdmin):
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
        model = product


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'photo', )
    list_display_links = ('user', 'photo', )


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    pass


admin.site.register(Profile, ProfileAdmin)
admin.site.register(product, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Messages)
admin.site.register(Chat)
