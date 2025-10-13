from pathlib import Path
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from django.urls import reverse
from PIL import Image, ImageOps


if TYPE_CHECKING:
    from django.db.models.fields.related_descriptors import RelatedManager


class Slideshow(models.Model):
    slug = models.SlugField(primary_key=True)
    title = models.CharField(max_length=200)
    cover = models.ImageField(null=True, default=None)

    groups: "RelatedManager[SlideGroup]"

    def __str__(self) -> str:
        return self.title


class SlideGroup(models.Model):
    slideshow = models.ForeignKey("Slideshow", on_delete=models.CASCADE, related_name="groups")
    order = models.PositiveSmallIntegerField(default=0)
    title = models.CharField(max_length=200, blank=True, default="")

    slides: "RelatedManager[Slide]"

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        if self.title:
            return f"{self.slideshow}: {self.order}: {self.title}"
        return f"{self.slideshow}: {self.order}"


class Slide(models.Model):
    group = models.ForeignKey("SlideGroup", on_delete=models.CASCADE, related_name="slides")
    order = models.PositiveSmallIntegerField(default=0)

    media_items: "RelatedManager[SlideMediaItem]"

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.group}: {self.order}"


class SlideMediaItem(models.Model):
    class Type(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    slide = models.ForeignKey("Slide", on_delete=models.CASCADE, related_name="media_items")
    order = models.PositiveSmallIntegerField(default=0)
    file = models.FileField()
    height = models.PositiveSmallIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=0)
    type = models.CharField(max_length=6, choices=Type.choices)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.slide}: {self.order}"

    @property
    def href(self):
        path = reverse("media-item-file", args=(self.pk,))
        return settings.ROOT_URL.rstrip("/") + "/" + path.lstrip("/")

    def generate_resized_images(self):
        if self.type == self.Type.IMAGE:
            original_size = max(self.width, self.height)

            with Image.open(self.file) as image:
                exif = image.getexif()
                orientation = exif.get(274)
                for image_size in [s for s in settings.IMAGE_SIZES if s < original_size]:
                    if self.width > self.height:
                        resized_image = image.resize((image_size, round(image_size * (self.height / self.width))))
                    else:
                        resized_image = image.resize((round(image_size * (self.width / self.height)), image_size))

                    if orientation in (2, 5, 7):
                        resized_image = ImageOps.mirror(resized_image)
                    elif orientation == 4:
                        resized_image = ImageOps.flip(resized_image)

                    if orientation == 3:
                        resized_image = resized_image.rotate(180, expand=True)
                    elif orientation in (6, 7):
                        resized_image = resized_image.rotate(270, expand=True)
                    elif orientation in (5, 8):
                        resized_image = resized_image.rotate(90, expand=True)

                    with self.file.storage.open(
                        self.get_resized_filename(self.file.name, image_size),
                        "wb",
                    ) as resized_file:
                        resized_image.save(resized_file, format="jpeg")

    def get_resized_filename(self, filename: str, image_size: int):
        path = Path(filename)
        return f"{path.stem}-{image_size}p{path.suffix}"

    def get_resized_url(self, image_size: int):
        parent, filename = self.split_url()
        return f"{parent}{self.get_resized_filename(filename, image_size)}"

    # pylint: disable=no-member
    def get_url(self, client_width: int | None, client_height: int | None):
        url = self.file.url

        if self.type == self.Type.IMAGE and client_width and client_height:
            client_size = max(client_width, client_height)
            image_sizes = [s for s in sorted(settings.IMAGE_SIZES) if s >= client_size]

            if image_sizes:
                url = self.get_resized_url(image_sizes[0])

        if url.startswith("/"):
            return settings.ROOT_URL + url
        return url

    # pylint: disable=no-member
    def split_url(self):
        if "/" in self.file.url:
            parent, filename = self.file.url.rsplit("/", 1)
            return parent + "/", filename
        return "", self.file.url
