from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import random
import os
from inspect import getsourcefile

from auth import tokenRequired
from aws import dataset_table, user_table, s3_dataset_url, s3_client, s3_dataset_bucket

# Blueprints modularize code
dataset = Blueprint("dataset", __name__)
game_id = 0

basePath = os.path.dirname(os.path.abspath(getsourcefile(lambda: 0)))

# Admin Required
@dataset.route("/upload_files/<string:dataset_name>", methods=["POST"])
@tokenRequired
def upload_files(username, dataset_name):
    try:
        files = request.files.getlist("file")
        res = dataset_table.get_item(Key={"dataset_name": dataset_name})["Item"]
        i = int(res["images"])

        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(basePath, "local_images", filename)
            file.save(file_path)
            s3_client.upload_file(
                file_path,
                s3_dataset_bucket,
                f"{dataset_name}/{i}.png",
                ExtraArgs={"ACL": "public-read"},
            )
            i += 1
        success = dataset_table.update_item(
            Key={"dataset_name": dataset_name},
            UpdateExpression="SET images = :newImages",
            ExpressionAttributeValues={":newImages": i},
            ReturnValues="UPDATED_NEW",
        )
        #                 id_filename = str(self.id) + "_" + filename
        #                 file.save(os.path.join(path, UPLOAD_FOLDER, id_filename))
        #                 infos = (self.id, id_filename, "")
        #                 with open(
        #                     os.path.join(
        #                         path, LOGIC_FOLDER, "Storage", PREDICT_FILES_CSV
        #                     ),
        #                     "a",
        #                 ) as f:
        #                     writer = csv.writer(f)
        #                     writer.writerow(infos)
        #                 imgs.append(filename)
        #                 self.id += 1
        #             else:
        #                 raise BadRequest
        return "Success"
    except Exception as e:
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e),
        }, 500


@dataset.route("/datasets", methods=["POST"])
@tokenRequired
def create_dataset(username):
    req = request.get_json()
    if "dataset_name" not in req:
        return (
            jsonify({"message": f"Dataset does not have a name"}),
            400,
        )
    # Check if dataset already exists
    dataset_name = req["dataset_name"]
    res = dataset_table.get_item(Key={"dataset_name": dataset_name})
    if "Item" in res:
        return (
            jsonify({"message": f"Dataset with name {dataset_name} already exists"}),
            400,
        )

    dataset = {
        "dataset_name": dataset_name,
        "images": 0,
        "labels": [],
        "bucket_url": f"{s3_dataset_url}{dataset_name}",
        "games_made": 0,
    }
    # Upload
    dataset_table.put_item(Item=dataset)
    return jsonify(dataset)


@dataset.route("/datasets", methods=["GET"])
@tokenRequired
def get_datasets(username):
    res = dataset_table.scan()["Items"]
    return jsonify(res)


@dataset.route("/create_game", methods=["GET"])
@tokenRequired
def create_game():
    try:
        # read amount of images user wants
        req = request.get_json()
        img_nr = req["images"]
        dataset_name = req["dataset"]
        dataset = dataset_table.get_item(Key={"dataset_name": dataset_name})
        # randomly sample images and labels from storage
        image_idxs = random.sample(range(0, dataset["nr_of_images"]), img_nr)
        image_labels = dataset["labels"][image_idxs]
        bucket_url = dataset["bucket_url"]
        # create a unique game id
        game_id += 1
        return jsonify(
            {
                "subset": image_idxs,
                "labels": image_labels,
                "bucket_url": bucket_url,
                "id": game_id,
            }
        )
    except Exception as e:
        print("Error", str(e))
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e),
        }, 500


@dataset.route("/game_end", methods=["PUT"])
@tokenRequired
def game_end(username):
    try:
        req = request.get_json()
        # read score and update database
        user = user_table.get_item(Key={"username": username})
        curr_score = user["score"]
        score = req["score"] + curr_score
        username = "dummy"
        updated = user_table.update_item(
            Key={"username": username},
            UpdateExpression="SET score = :newScore",
            ExpressionAttributeValues={":newScore": score},
            ReturnValues="UPDATED_NEW",
        )

        return {"new_score": score}
    except Exception as e:
        print("Error", str(e))
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e),
        }, 500


@dataset.route("/leaderboard", methods=["GET"])
@tokenRequired
def leaderboard():
    try:
        # query leaderboard from database
        return "Success"
    except Exception as e:
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e),
        }, 500
