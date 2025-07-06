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


def estimate_skin_percent(image_path):
    """
    Naiv uppskattning av hudpixlar baserat på färgintervall i RGB.
    Returnerar % av bilden som tros vara hud.
    """
    image = load_image(image_path)
    pixels = image.getdata()
    skin_pixels = 0

    for pixel in pixels:
        r, g, b = pixel
        if (r > 95 and g > 40 and b > 20 and
            max(pixel) - min(pixel) > 15 and
            abs(r - g) > 15 and r > g and r > b):
            skin_pixels += 1

    total_pixels = len(pixels)
    if total_pixels == 0:
        return 0.0

    return (skin_pixels / total_pixels) * 100
