from django.urls import include, path
from rest_framework.routers import DefaultRouter

from next_slideshows_backend.api.views import (
    SlideMediaItemViewSet,
    SlideshowViewSet,
)


router = DefaultRouter()

router.register(prefix="slideshows", viewset=SlideshowViewSet, basename="slideshow")
router.register(prefix="media-items", viewset=SlideMediaItemViewSet, basename="media-item")

urlpatterns = [
    path("", include(router.urls)),
]
