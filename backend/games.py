from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
import random
import os
from inspect import getsourcefile

from auth import tokenRequired
from aws import (
    dataset_table,
    user_table,
    s3_dataset_url,
    s3_client,
    s3_dataset_bucket,
    dynamo_client,
    scan_table,
)

from utils import update_rating, generate_random_string


class wrongGameId(Exception):
    """Throw in case used game id is not the current one"""

    pass


class duellFull(Exception):
    """Raise error in case the duell is already full"""

    pass


# Blueprints modularize code
dataset = Blueprint("dataset", __name__)
game_id = ""

basePath = os.path.dirname(os.path.abspath(getsourcefile(lambda: 0)))

# Admin Required
@dataset.route("/upload_files/<string:dataset_name>", methods=["POST"])
@tokenRequired
def upload_files(username, dataset_name):
    try:
        files = request.files.getlist("file")
        res = dataset_table.get_item(Key={"dataset_name": dataset_name})["Item"]
        i = int(res["images"])
        img_ids = []
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
            img_ids.append(i)
            i += 1
        # Run ML Model with images
        success = dataset_table.update_item(
            Key={"dataset_name": dataset_name},
            UpdateExpression="SET images = :newImages",
            ExpressionAttributeValues={":newImages": i},
            ReturnValues="UPDATED_NEW",
        )
        # Send list of predictions back to the frontend
        predictions = [None] * len(files)
        return {"predictions": predictions, "id": img_ids}
    except Exception as e:
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e),
        }, 500


@dataset.route("/upload_files/verification/<string:dataset_name>", methods=["PUT"])
@tokenRequired
def verify_upload(username, dataset_name):
    try:
        req = request.get_json()
        new_labels = req["labels"]
        img_ids = req["id"]
        res = dataset_table.get_item(Key={"dataset_name": dataset_name})["Item"]
        labels = res["labels"]
        labels += new_labels

        success = dataset_table.update_item(
            Key={"dataset_name": dataset_name},
            UpdateExpression="SET labels = :newLabels",
            ExpressionAttributeValues={":newLabels": labels},
            ReturnValues="UPDATED_NEW",
        )
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
    res = dataset_table.get_item(Key={"dataset_name": dataset_name})["Item"]
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
        res = dataset_table.get_item(Key={"dataset_name": dataset_name})["Item"]
        # randomly sample images and labels from storage
        image_idxs = random.sample(range(0, res["nr_of_images"]), img_nr)
        image_labels = res["labels"][image_idxs]
        bucket_url = res["bucket_url"]
        # create a unique game id
        game_id = generate_random_string()
        success = dataset_table.update_item(
            Key={"dataset_name": dataset_name},
            UpdateExpression="SET games_made = :newGames_made",
            ExpressionAttributeValues={":newGames_made": res["games_made"] + 1},
            ReturnValues="UPDATED_NEW",
        )
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


@dataset.route("/game_end/<string:req_game_id>", methods=["PUT"])
@tokenRequired
def game_end(username, req_game_id):
    try:
        if req_game_id != game_id:
            raise wrongGameId
        req = request.get_json()
        # read score and update database
        user = user_table.get_item(Key={"username": username})["Item"]

        curr_score = user["score"]
        correct_answers, wrong_answers = req["correct_answers"], req["wrong_answers"]
        score = update_rating(curr_score, correct_answers, wrong_answers)

        updated = user_table.update_item(
            Key={"username": username},
            UpdateExpression="SET score = :newScore",
            ExpressionAttributeValues={":newScore": score},
            ReturnValues="UPDATED_NEW",
        )

        return {"new_score": score}
    except wrongGameId:
        return ({"message": "Game id not currently active", "data": req_game_id}, 404)
    except Exception as e:
        print("Error", str(e))
        return (
            {
                "message": "Something went wrong",
                "data": None,
                "error": str(e),
            },
            500,
        )


@dataset.route("/leaderboard", methods=["GET"])
@tokenRequired
def leaderboard():
    try:
        # query leaderboard from database
        items = scan_table(dynamo_client)
        return "Success"
    except Exception as e:
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e),
        }, 500


@dataset.route("/create_duell_room", methods=["GET"])
@tokenRequired
def create_duell_room():
    try:
        # read amount of images user wants
        req = request.get_json()
        img_nr = req["images"]
        dataset_name = req["dataset"]
        dataset = dataset_table.get_item(Key={"dataset_name": dataset_name})["Item"]
        # randomly sample images and labels from storage
        image_idxs = random.sample(range(0, dataset["nr_of_images"]), img_nr)
        image_labels = dataset["labels"][image_idxs]
        bucket_url = dataset["bucket_url"]
        # create a unique game id
        game_id = generate_random_string()

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


@dataset.route("/join_duell_room/<string:game_id>", methods=["GET"])
@tokenRequired
def join_duell_room(username, game_id):
    try:
        # read amount of images user wants
        req = request.get_json()

        game = game_table.get_item(Key={"game_id": game_id})["Item"]
        image_labels = game["image_labels"]
        image_idxs = game["subset_index"]

        bucket_url = game["bucket_url"]

        player_1 = game["player_1"]
        player_2 = game["player_2"]

        game_id = game["game_id"]

        if not player_1:
            player_1 = username
            return jsonify(
                {
                    "player_1": player_1,
                    "subset": image_idxs,
                    "labels": image_labels,
                    "bucket_url": bucket_url,
                    "id": game_id,
                }
            )
        elif not player_2:
            player_2 = username
            return jsonify(
                {
                    "player_2": player_2,
                    "subset": image_idxs,
                    "labels": image_labels,
                    "bucket_url": bucket_url,
                    "id": game_id,
                }
            )
        else:
            raise duellFull
    except duellFull:
        return ({"message": "Duell is already full", "data": game_id}, 404)
    except Exception as e:
        print("Error", str(e))
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e),
        }, 500
