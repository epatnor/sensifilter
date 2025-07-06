# sensifilter

**Sensifilter** is a modular Python library for detecting sensitive content in images, such as nudity, violence, or graphic content.

It is designed to be fast, configurable, and easy to integrate into photo management systems, moderation pipelines, and desktop applications.

---

## 🔍 Features

- Early rejection of irrelevant images via metadata, skin detection, and human presence
- Detection of nudity, violence, and other sensitive content using keyword-driven analysis
- BLIP-based captioning and semantic filtering
- Customizable confidence thresholds and keyword lists
- Optional CLI for batch analysis
- Plug-and-play friendly: can be used as a standalone module or integrated into larger projects like Phunnel

---

## 🚀 Example usage

```python
from sensifilter import analyze_image

result = analyze_image("photo.jpg")

print(result["label"])  # "safe", "nudity", "violence", "review"
print(result["caption"])  # e.g. "a nude woman sitting on a bed"
```

## 🔧 Roadmap

* Modular structure
* BLIP/YOLO integration
* Scene & pose detection
* GUI-friendly progress callbacks
* JSON-configurable settings

## 📄 License
MIT – do what you want, but be respectful.
