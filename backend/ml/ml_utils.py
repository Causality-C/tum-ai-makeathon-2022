import cv2
import torch
import numpy as np
import glob
from torch.utils.data import Dataset, DataLoader
from io import StringIO
from torchvision import transforms

class DiseaseDataset(Dataset):
    def __init__(self, img_path, label_matrix):
        self.path = img_path
        self.folder = [p for p in glob.glob(img_path + '/**', recursive=True) if p.endswith('jpg')]
        self.labels = label_matrix
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            # transforms.CenterCrop(320),
            transforms.Resize((320, 320)),
            transforms.ToTensor(),
            ])

    def __len__(self):
        return len(self.folder)

    def __getitem__(self, idx):
        img_loc = self.folder[idx]
        image = cv2.imread(img_loc)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = self.transform(image)
        targets = self.labels[idx]

        return {
            'image': torch.tensor(image, dtype=torch.float32),
            'label': torch.tensor(targets, dtype=torch.float32)
        }


class TrainDiseaseDataset(Dataset):
    """
    Class to read images from a zip file.
    """
    def __init__(self, zip_file, img_list, label_matrix):
        self.zip_file = zip_file
        self.folder = img_list
        self.labels = label_matrix
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.CenterCrop(320),
            transforms.ToTensor(),
            ])

    def __len__(self):
        return len(self.folder)

    def __getitem__(self, idx):
        img_loc = self.folder[idx][0]
        im_file = self.zip_file.read(img_loc)
        image = cv2.imdecode(np.frombuffer(im_file, np.uint8), 1)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = self.transform(image)
        targets = self.labels[idx]
        return {
            'image': torch.tensor(image, dtype=torch.float32),
            'label': torch.tensor(targets, dtype=torch.float32)
        }