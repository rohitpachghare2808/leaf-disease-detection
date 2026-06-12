import os

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from model import LeafCNN


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_dataloaders(data_root, batch_size=32):
    train_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(20),
            transforms.RandomVerticalFlip(),
            transforms.ColorJitter(brightness=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    val_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    train_dir = os.path.join(data_root, "train")
    val_dir = os.path.join(data_root, "val")

    train_ds = datasets.ImageFolder(train_dir, transform=train_transform, allow_empty=True)
    val_ds = datasets.ImageFolder(val_dir, transform=val_transform, allow_empty=True)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, train_ds.classes


def train_model(data_root, epochs=20, lr=0.001, batch_size=32, device=None):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    train_loader, val_loader, classes = get_dataloaders(data_root, batch_size=batch_size)

    model = LeafCNN(num_classes=len(classes)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0

        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)

        epoch_loss = running_loss / len(train_loader.dataset)

        # Simple validation accuracy
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, preds = torch.max(outputs, 1)
                total += labels.size(0)
                correct += (preds == labels).sum().item()

        val_acc = correct / total if total > 0 else 0.0
        print(f"Epoch {epoch+1}/{epochs} - loss: {epoch_loss:.4f} - val_acc: {val_acc:.4f}")

    # Build per-class feature prototypes and distance thresholds for unknown detection.
    infer_transform = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )
    train_dir = os.path.join(data_root, "train")
    proto_ds = datasets.ImageFolder(train_dir, transform=infer_transform, allow_empty=True)
    proto_loader = DataLoader(proto_ds, batch_size=batch_size, shuffle=False)

    class_features = {i: [] for i in range(len(classes))}
    model.eval()
    with torch.no_grad():
        for images, labels in proto_loader:
            images = images.to(device)
            features = model.extract_features(images).cpu()
            for feature, label in zip(features, labels):
                class_features[int(label)].append(feature)

    prototypes = {}
    thresholds = {}
    for class_idx in range(len(classes)):
        name = classes[class_idx]
        feats = class_features.get(class_idx, [])
        if not feats:
            continue
        stacked = torch.stack(feats)
        centroid = stacked.mean(dim=0)
        dists = torch.norm(stacked - centroid, dim=1)
        if len(dists) > 1:
            base = float(torch.quantile(dists, 0.95).item())
        else:
            base = float(dists[0].item())
        threshold = max(base * 1.35, 1.0)
        prototypes[name] = centroid.tolist()
        thresholds[name] = threshold

    # Save checkpoint where app.py expects it, including class order metadata.
    weights_path = os.path.join(BASE_DIR, "leaf_model.pth")
    torch.save(
        {
            "state_dict": model.state_dict(),
            "classes": classes,
            "feature_prototypes": prototypes,
            "feature_distance_thresholds": thresholds,
        },
        weights_path,
    )
    print(f"Saved trained checkpoint to {weights_path}")
    print("Classes order:", classes)


if __name__ == "__main__":
    # Put your dataset under: project_root/data/train and project_root/data/val
    # with subfolders: Healthy, Early Blight, Late Blight, Leaf Spot, Powdery Mildew, Rust, Bacterial Spot, Leaf Curl, Mosaic Virus, Septoria Leaf Spot
    data_root = os.path.join(BASE_DIR, "data")
    train_model(data_root)

