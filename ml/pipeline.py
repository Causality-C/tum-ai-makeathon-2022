# Check core SDK version number
import azureml.core
print("SDK version:", azureml.core.VERSION)
from azureml.core import Workspace, Dataset
import azure
import sys
import cv2
import matplotlib.pyplot as plt
import os
from os import listdir
from os.path import isfile, join
import zipfile
import random
import pandas as pd
from tqdm import tqdm
import torch
import torchvision
from torch.utils.data import Dataset, DataLoader
import glob
import numpy as np
from PIL import Image
from io import StringIO
from torchvision import transforms
from ml_utils import DiseaseDataset, load_chexpert_train


# azureml-core of version 1.0.72 or higher is required
# azureml-dataprep[pandas] of version 1.1.34 or higher is required

subscription_id = 'c0e252b0-50d3-44e6-bb79-a007a94e3a9e'
resource_group = 'ml_rg'
workspace_name = 'machine_learning1'

ws = Workspace(subscription_id, resource_group, workspace_name)

print('Workspace name: ' + ws.name, 
      'Azure region: ' + ws.location, 
      'Subscription id: ' + ws.subscription_id, 
      'Resource group: ' + ws.resource_group, sep='\n')

# ds2: valid image folder
ds2 = azureml.core.Dataset.get_by_name(ws, name='chexpert2')
try:
    ds2.download(target_path='.', overwrite=False)
except:
    print("Dataset already downloaded!")
    sys.exit(0)

# ds1: valid.csv
ds1 = azureml.core.Dataset.get_by_name(ws, name='chexpert')
df_valid = ds1.to_pandas_dataframe()
df = df_valid
for i, p in enumerate(df_valid["Path"]):
    df["Path"][i] = p[20:]

# READ ZIP FILE
zip_path = 'CheXpert-v1.0-small.zip'
# Train Loader (from zip file)
train_loader = load_chexpert_train(zip_path, data_percentage=0.5, batch_size=32)

######  TEST DATA  ######
# Test Labels
labels = list(df.columns[5:])
label_arr_test = df[labels].to_numpy()
# Test Data Loader
batch_size = 5
test_data = DiseaseDataset('valid', label_arr_test)
test_loader = DataLoader(test_data, batch_size=batch_size, shuffle=False)

######  MODEL   #####
# Check if the model exists
def train():
    pretrained = "models/pretrained_densenet121.pth"
    if os.path.isfile(zip_path):
        model = torch.load(pretrained) # to load
    else:
        print("ERROR:")
        print("Downloading DenseNet121 model..")
        ds_model = Dataset.get_by_name(ws, name='densenet121')
        ds_model.download(target_path='.', overwrite=False)

    num_output_classes = 14

    for param in model.parameters():
        param.requires_grad = False
        
    new_classifier = torch.nn.Sequential(
        torch.nn.Linear(1024, 512),
        torch.nn.ReLU(),
        torch.nn.Linear(512, num_output_classes),
        torch.nn.Sigmoid()
    )

    model.classifier = new_classifier

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    # device = torch.device('cpu')
    print("Device: ", device)
    model.to(device)

    #####   TRAINING   ######
    n_epoch = 3
    criterion = torch.nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    n_total_steps = len(train_loader)

    for epoch in range(n_epoch):
        running_loss = 0.0
        with tqdm(train_loader, unit="batch") as tepoch:
            for data in tepoch:
                # get the inputs; data is a list of [inputs, labels]
                inputs, labels = data['image'], data['label']
                inputs, labels = inputs.to(device), labels.to(device)
                # zero the parameter gradients
                optimizer.zero_grad()

                # forward + backward + optimize
                outputs = model(inputs)
                loss = criterion(outputs, labels)

                loss.backward()
                optimizer.step()

                tepoch.set_postfix(loss=loss.item())

    print('Finished Training')
    print("Saving model")
    torch.save(model, "models/densenet121_valid.pth")
    print('Model saved in "models/densenet121_valid.pth"')

    return model
