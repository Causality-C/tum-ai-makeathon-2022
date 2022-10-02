from ml_dev.utils import Model
from dotenv import load_dotenv
import os

load_dotenv()

model_path = os.environ["MODEL_PATH"]

ml_model = Model()
ml_model.load_model(model_path)
