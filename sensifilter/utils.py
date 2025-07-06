# sensifilter/utils.py

# Common helper functions (e.g., resize, image loader)
# utils.py

from PIL import Image


def load_image(image_path):
    """
    Loads an image using PIL and converts to RGB.
    """
    with Image.open(image_path) as img:
        return img.convert("RGB")


def resize_image(image, size=(224, 224)):
    """
    Resizes an image to a given size.
    """
    return image.resize(size)
