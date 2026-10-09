"""Data augmentation and preprocessing transforms for training, validation, and inference."""
import torchvision.transforms as T
from PIL import Image


def get_train_transforms(image_size: int = 224) -> T.Compose:
    """Robust training augmentations to reduce lab background shortcut learning."""
    return T.Compose([
        T.RandomResizedCrop(image_size, scale=(0.7, 1.0), ratio=(0.8, 1.25)),
        T.RandomHorizontalFlip(p=0.5),
        T.RandomVerticalFlip(p=0.3),
        T.RandomRotation(degrees=30),
        T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1),
        T.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        T.GaussianBlur(kernel_size=(3, 3), sigma=(0.1, 2.0)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        T.RandomErasing(p=0.2, scale=(0.02, 0.2), ratio=(0.3, 3.3), value="random"),
    ])


def get_eval_transforms(image_size: int = 224) -> T.Compose:
    """Standard evaluation/inference preprocessing."""
    return T.Compose([
        T.Resize(int(image_size * 1.14)),  # e.g., 256 for 224
        T.CenterCrop(image_size),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
