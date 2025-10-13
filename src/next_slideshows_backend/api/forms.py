import mimetypes

import cv2
from django.conf import settings
from django.forms import ModelForm
from PIL import Image

from next_slideshows_backend.api.models import SlideMediaItem
from next_slideshows_backend.api.widgets import SlideMediaItemFileInput


class SlideForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].required = False


class SlideMediaItemForm(ModelForm):
    class Meta:
        widgets = {"file": SlideMediaItemFileInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields["type"], self.fields["height"], self.fields["width"]:
            field.required = False

    # pylint: disable=no-member
    def save(self, commit=True):
        assert isinstance(self.instance, SlideMediaItem)

        if "file" in self.changed_data:
            mime, _ = mimetypes.guess_type(self.instance.file.name)
            if mime and mime.startswith("image"):
                self.instance.type = SlideMediaItem.Type.IMAGE
            elif mime and mime.startswith("video"):
                self.instance.type = SlideMediaItem.Type.VIDEO

            super().save(commit)

            previous_file = self.initial.get("file", None)
            if previous_file and previous_file.name != self.instance.file.name:
                self.instance.file.storage.delete(name=previous_file.name)
                for image_size in settings.IMAGE_SIZES:
                    self.instance.file.storage.delete(
                        self.instance.get_resized_filename(previous_file.name, image_size)
                    )

            if self.instance.type == SlideMediaItem.Type.IMAGE:
                with Image.open(self.instance.file) as image:
                    self.instance.width = image.width
                    self.instance.height = image.height
                self.instance.save(update_fields=("width", "height"))
                self.instance.generate_resized_images()
            elif self.instance.type == SlideMediaItem.Type.VIDEO:
                video = cv2.VideoCapture(self.instance.file.path)
                self.instance.width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.instance.height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
                video.release()
                self.instance.save(update_fields=("width", "height"))
        else:
            super().save(commit)

        return self.instance
