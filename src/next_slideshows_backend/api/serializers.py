from rest_framework import serializers

from next_slideshows_backend.api.models import SlideMediaItem, Slideshow


class SlideshowListSerializer(serializers.ModelSerializer[Slideshow]):
    class Meta:
        model = Slideshow
        fields = ["title", "slug", "cover"]


class SlideMediaItemSerializer(serializers.ModelSerializer[SlideMediaItem]):
    class Meta:
        model = SlideMediaItem
        fields = ["id", "href", "height", "width", "type"]


class SlideshowSerializer(serializers.ModelSerializer[Slideshow]):
    slides = serializers.SerializerMethodField()

    class Meta:
        model = Slideshow
        fields = ["title", "slug", "slides", "cover"]

    def get_slides(self, obj: Slideshow):
        slides = []
        for group in obj.groups.all():
            slides.append({"mediaItems": [], "title": group.title, "isSpecial": True})
            for slide in group.slides.all():
                media_items_serializer = SlideMediaItemSerializer(slide.media_items.all(), many=True)
                slides.append({"mediaItems": media_items_serializer.data})
        return slides
