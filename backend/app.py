from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from auth import auth
from games import dataset

# Add some boilerplate
app = Flask(__name__)
app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(dataset, url_prefix="/dataset")
CORS(app)
load_dotenv()


@app.get("/")
def getReq():
    return "Hello World"
