# sensifilter/caption.py

# BLIP captioning logic
# caption.py

def generate_caption(image_path):
    """
    Generates a semantic description of the image using a vision-language model.
    Returns (caption:str, confidence:float)

    In this stub version, it returns a mock caption with 0.9 confidence.
    """

    # TODO: Replace with real BLIP / BLIP2 model call
    caption = "a person standing near water wearing a swimsuit"
    confidence = 0.90
    return caption, confidence
