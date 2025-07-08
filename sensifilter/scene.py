# scene.py

import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import os
import urllib.request

# === Filvägar för modell och etiketter ===
MODEL_PATH = os.path.join(os.path.dirname(__file__), "resnet18_places365.pth.tar")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "categories_places365.txt")

def load_labels():
    """
    Ladda kategorietiketter från Places365.
    Laddar ner filen om den saknas.
    """
    if not os.path.exists(LABELS_PATH):
        print(f"📥 Laddar ner etiketter från GitHub: {LABELS_PATH}")
        url = "https://raw.githubusercontent.com/csailvision/places365/master/categories_places365.txt"
        urllib.request.urlretrieve(url, LABELS_PATH)

    with open(LABELS_PATH) as f:
        labels = [line.strip().split(" ")[0][3:] for line in f]
    print(f"✅ Etiketter laddade: {len(labels)} st")
    return labels

def load_model():
    """
    Ladda ResNet18-modell tränad på Places365.
    Laddar ner viktfilen om den saknas.
    """
    if not os.path.exists(MODEL_PATH):
        print(f"📥 Laddar ner modellvikter från MIT: {MODEL_PATH}")
        url = "http://places2.csail.mit.edu/models_places365/resnet18_places365.pth.tar"
        urllib.request.urlretrieve(url, MODEL_PATH)

    print("⚙️ Laddar modell från disk...")
    model = models.resnet18(num_classes=365)

    checkpoint = torch.load(MODEL_PATH, map_location=torch.device('cpu'))
    # Rensa bort ev. "module." prefix från keys (om tränad med DataParallel)
    state_dict = {k.replace("module.", ""): v for k, v in checkpoint['state_dict'].items()}
    model.load_state_dict(state_dict)
    model.eval()
    print("✅ Modell laddad och klar för inferens")
    return model

# === Ladda modell och etiketter EN gång globalt ===
_MODEL = load_model()
_LABELS = load_labels()

# === Bildtransform för ResNet ===
_transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

def classify_scene(image_path):
    """
    Klassificerar scenen i bilden med hjälp av Places365 ResNet18.
    Returnerar etikett och konfidens.
    """
    print(f"🔍 Klassificerar scen för bild: {image_path}")
    img = Image.open(image_path).convert('RGB')
    input_tensor = _transform(img).unsqueeze(0)

    with torch.no_grad():
        output = _MODEL(input_tensor)
        probs = torch.nn.functional.softmax(output[0], dim=0)
        top_idx = probs.argmax().item()
        top_label = _LABELS[top_idx]
        confidence = probs[top_idx].item()

    print(f"🏷️ Scen: {top_label} ({confidence:.2f})")
    return f"{top_label} ({confidence:.2f})"
