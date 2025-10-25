from django.shortcuts import redirect
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request

from next_slideshows_backend.api.models import SlideMediaItem, Slideshow
from next_slideshows_backend.api.serializers import (
    SlideMediaItemSerializer,
    SlideshowListSerializer,
    SlideshowSerializer,
)


class SlideshowViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Slideshow.objects.prefetch_related("groups__slides__media_items")

    def get_serializer_class(self):
        if self.action == "list":
            return SlideshowListSerializer
        return SlideshowSerializer


class SlideMediaItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SlideMediaItem.objects.all()
    serializer_class = SlideMediaItemSerializer

    @action(methods=["get"], detail=True)
    def file(self, request: Request, pk: str):
        instance: SlideMediaItem = self.get_object()

        try:
            width, height = (
                int(request.query_params.get("clientWidth", "")),
                int(request.query_params.get("clientHeight", "")),
            )
        except ValueError:
            width, height = None, None

        return redirect(instance.get_url(client_width=width, client_height=height))
