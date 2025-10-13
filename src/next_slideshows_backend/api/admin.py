from django.contrib import admin
from django.http import HttpRequest
from nested_admin import nested

from next_slideshows_backend.api.forms import SlideForm, SlideMediaItemForm
from next_slideshows_backend.api.models import (
    Slide,
    SlideGroup,
    SlideMediaItem,
    Slideshow,
)


class AdminMixin:
    save_on_top = True

    class Media:
        css = {"all": ["assets/css/admin.css"]}


class SlideMediaItemInline(nested.NestedTabularInline):
    model = SlideMediaItem
    form = SlideMediaItemForm
    show_change_link = True
    sortable_field_name = "order"

    def get_extra(self, request: HttpRequest, obj=None, **kwargs):
        return 1 if obj is None else 0


class SlideInline(nested.NestedTabularInline):
    model = Slide
    form = SlideForm
    show_change_link = True
    sortable_field_name = "order"
    extra = 0
    inlines = [SlideMediaItemInline]


class SlideGroupInline(nested.NestedTabularInline):
    model = SlideGroup
    show_change_link = True
    sortable_field_name = "order"
    extra = 0


@admin.register(SlideMediaItem)
class SlideMediaItemAdmin(AdminMixin, admin.ModelAdmin):
    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).select_related("slide__slideshow", "slide__group__slideshow")


@admin.register(Slide)
class SlideAdmin(AdminMixin, nested.NestedModelAdmin):
    inlines = [SlideMediaItemInline]
    list_display = ["__str__", "group__slideshow", "group", "order"]
    ordering = ["group__slideshow", "group", "order"]

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).select_related("group__slideshow")


@admin.register(SlideGroup)
class SlideGroupAdmin(AdminMixin, nested.NestedModelAdmin):
    inlines = [SlideInline]
    list_display = ["__str__", "slideshow", "order", "title", "slide_count"]
    ordering = ["slideshow", "order"]

    def get_queryset(self, request: HttpRequest):
        return super().get_queryset(request).select_related("slideshow").prefetch_related("slides__media_items")

    def slide_count(self, obj: SlideGroup):
        return obj.slides.count()


@admin.register(Slideshow)
class SlideshowAdmin(AdminMixin, nested.NestedModelAdmin):
    inlines = [SlideGroupInline]
