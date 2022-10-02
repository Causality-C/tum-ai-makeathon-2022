from ml_dev.utils import Model
from dotenv import load_dotenv
import os
from inspect import getsourcefile

load_dotenv()

basePath = os.path.dirname(os.path.abspath(getsourcefile(lambda: 0)))
model_path = os.path.join(basePath,os.environ["MODEL_PATH"])


ml_model = Model()
ml_model.load_model(model_path)
