from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from next_slideshows_backend.api.models import SlideMediaItem


@receiver(pre_delete, sender=SlideMediaItem, dispatch_uid="on_slide_media_item_pre_delete")
def on_slide_media_item_pre_delete(sender, instance: SlideMediaItem, **kwargs):
    if instance.file and instance.file.name:
        instance.file.storage.delete(name=instance.file.name)
        for image_size in settings.IMAGE_SIZES:
            instance.file.storage.delete(instance.get_resized_filename(instance.file.name, image_size))
