import cv2
import os
import zipfile
import sys
import torch
import pandas as pd
import random
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

def load_chexpert_train(zip_path, data_percentage, batch_size=32):
    """
    To load train data of Chexpert.
    Return:
        Train DataLoader
    """
    if os.path.isfile(zip_path):
        z = zipfile.ZipFile(zip_path)
    else:
        print("No zip file exists! Please download.")
        return None

    zip_name_list = z.namelist()
    zip_train_list = [x for x in zip_name_list if x.startswith('CheXpert-v1.0-small/train') and x.endswith('.jpg')]

    # Train Image Names
    sorted_train_list = sorted(zip_train_list, key=lambda f: int(f[33:38]))[1:]
    # train.csv
    train_csv = 'CheXpert-v1.0-small/train.csv'
    df_train = pd.read_csv(z.open(train_csv))
    # Labels (#14)
    labels = list(df_train.columns[5:])
    # Label matrix
    label_arr_train = df_train[labels].to_numpy(na_value=0)
    label_arr_train = np.where(label_arr_train == -1, 0, label_arr_train)

    # Number of samples
    nr_train = len(sorted_train_list)
    idx_list = np.arange(nr_train)
    # Randomly chosen indices
    random_list= [random.sample(list(idx_list), int(nr_train * data_percentage))]
    # New labels
    train_labels = label_arr_train[tuple(random_list)]
    sorted_train_list = np.reshape(np.array(sorted_train_list), (-1, 1))
    train_img_list = sorted_train_list[tuple(random_list)]

    train_data = TrainDiseaseDataset(z, train_img_list, train_labels)
    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    return train_loader
