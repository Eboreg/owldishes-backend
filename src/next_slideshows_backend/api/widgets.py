from django.forms import ClearableFileInput


class SlideMediaItemFileInput(ClearableFileInput):
    template_name = "slide_media_item_file_input.html"
