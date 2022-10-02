from multiprocessing.connection import answer_challenge
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
    game_table,
)
from ml import ml_model

from utils import update_rating, generate_random_string


class wrongGameId(Exception):
    """Throw in case used game id is not the current one"""

    pass


class duellFull(Exception):
    """Raise error in case the duell is already full"""

    pass


# Blueprints modularize code
dataset = Blueprint("dataset", __name__)

basePath = os.path.dirname(os.path.abspath(getsourcefile(lambda: 0)))


def generate_answers(labels, nr_of_choices):
    possible_classes = ml_model.get_classes()
    answer_choices = []
    for idx, label in enumerate(labels):
        choices = possible_classes.copy()
        # remove the true label from random choices
        choices.remove(label)
        choices = random.sample(choices, nr_of_choices)
        insert = random.choice(range(0, nr_of_choices))
        choices.insert(insert, label)
        answer_choices.append(choices)
    return answer_choices


# Admin Required
@dataset.route("/upload_files/<string:dataset_name>", methods=["POST"])
@tokenRequired
def upload_files(username, dataset_name):
    try:
        files = request.files.getlist("file")
        res = dataset_table.get_item(Key={"dataset_name": dataset_name})["Item"]
        i = int(res["images"])
        img_ids = []
        images = []
        for file in files:
            filename = secure_filename(file.filename)
            file_path = os.path.join(basePath, "local_images", filename)
            file.save(file_path)
            s3_client.upload_file(
                file_path,
                s3_dataset_bucket,
                f"{dataset_name}/{i}.jpeg",
                ExtraArgs={"ACL": "public-read"},
            )
            img_ids.append(i)

            i += 1

        # Send list of predictions back to the frontend
        predictions = ml_model.inference_multiple_images(
            os.path.join(basePath, "local_images")
        )

        # Run ML Model with images
        success = dataset_table.update_item(
            Key={"dataset_name": dataset_name},
            UpdateExpression="SET images = :newImages, labels = :newLabels",
            ExpressionAttributeValues={
                ":newImages": i,
                ":newLabels": res["labels"] + predictions,
            },
            ReturnValues="UPDATED_NEW",
        )
        # clean up temporary image directory
        files_list = os.listdir(os.path.join(basePath, "local_images"))
        for file in files_list:
            os.remove(os.path.join(basePath, "local_images", file))
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
        "creator": username,
    }

    # Upload
    dataset_table.put_item(Item=dataset)
    return jsonify(dataset)


@dataset.route("/datasets", methods=["GET"])
@tokenRequired
def get_datasets(username):
    res = dataset_table.scan()["Items"]
    return jsonify(res)


@dataset.route("/datasets/<string:dataset_name>", methods=["GET"])
@tokenRequired
def get_dataset(username, dataset_name):
    res = dataset_table.get_item(Key={"dataset_name": dataset_name})["Item"]
    return jsonify(res)


@dataset.route("/create_game", methods=["POST"])
@tokenRequired
def create_game(username):
    try:
        # read amount of images user wants
        req = request.get_json()
        img_nr = req["images"]
        dataset_name = req["dataset"]
        res = dataset_table.get_item(Key={"dataset_name": dataset_name})["Item"]

        # randomly sample images and labels from storage
        image_idxs = random.sample(range(0, int(res["images"])), img_nr)
        image_labels = [res["labels"][i] for i in image_idxs]
        bucket_url = res["bucket_url"]
        success = dataset_table.update_item(
            Key={"dataset_name": dataset_name},
            UpdateExpression="SET games_made = :newGames_made",
            ExpressionAttributeValues={":newGames_made": res["games_made"] + 1},
            ReturnValues="UPDATED_NEW",
        )
        # generate answer choices
        answer_choices = generate_answers(image_labels, 4)
        return jsonify(
            {
                "subset": image_idxs,
                "answer_choices": answer_choices,
                "true_labels": image_labels,
                "bucket_url": bucket_url,
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
        # read score and update database
        req = request.get_json()
        user = user_table.get_item(Key={"username": username})["Item"]

        # Score the game
        correct, received = req["correct"], req["received"]
        game_score = sum(
            [1 if correct[i] == received[i] else 0 for i in range(len(correct))]
        )

        curr_score = int(user["score"])
        correct_answers, wrong_answers = (
            game_score,
            len(received) - game_score,
        )

        # Sets the new score based on algorithm
        score = update_rating(curr_score, correct_answers, wrong_answers)

        updated = user_table.update_item(
            Key={"username": username},
            UpdateExpression="SET score = :newScore",
            ExpressionAttributeValues={":newScore": score},
            ReturnValues="UPDATED_NEW",
        )
        return jsonify(
            {
                "new_score": score,
                "num_correct": correct_answers,
                "num_incorrect": wrong_answers,
                "username": username,
            }
        )

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
def leaderboard(username):
    try:
        # query leaderboard from database
        items = user_table.scan()["Items"]
        scores_list = [(int(item["score"]), idx) for idx, item in enumerate(items)]
        scores_list.sort(reverse=True)  # Top players come first
        scores_sorted, permutation = zip(*scores_list)
        items_sorted = [
            {
                "username": items[i]["username"],
                "score": items[i]["score"],
                "games_played": items[i]["games_played"],
            }
            for i in permutation
        ]
        return jsonify(items_sorted)
    except Exception as e:
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e),
        }, 500


@dataset.route("/create_duell_room", methods=["POST"])
@tokenRequired
def create_duell_room(username):
    try:
        # read amount of images user wants
        req = request.get_json()
        img_nr = req["images"]
        dataset_name = req["dataset"]
        res = dataset_table.get_item(Key={"dataset_name": dataset_name})["Item"]

        # randomly sample images and labels from storage
        image_idxs = random.sample(range(0, int(res["images"])), img_nr)
        image_labels = [res["labels"][i] for i in image_idxs]
        bucket_url = res["bucket_url"]
        success = dataset_table.update_item(
            Key={"dataset_name": dataset_name},
            UpdateExpression="SET games_made = :newGames_made",
            ExpressionAttributeValues={":newGames_made": res["games_made"] + 1},
            ReturnValues="UPDATED_NEW",
        )

        # create a unique game id
        game_id = generate_random_string()
        answer_choices = generate_answers(image_labels, 4)
        duel = {
            "subset": image_idxs,
            "answer_choices": answer_choices,
            "true_labels": image_labels,
            "bucket_url": bucket_url,
            "game_id": game_id,
            "game_status": "pending",
            "players": [],
        }
        game_table.put_item(Item=duel)

        return jsonify({"game_id": game_id})

    except Exception as e:
        print("Error", str(e))
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e),
        }, 500


@dataset.route("/duell_room/<string:game_id>", methods=["GET"])
@tokenRequired
def get_duel_room(username, game_id):
    try:
        duel = game_table.get_item(Key={"game_id": game_id})["Item"]
        return jsonify(duel)
    except Exception as e:
        print("Error", str(e))
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e),
        }, 500


@dataset.route("/join_duell_room/<string:game_id>", methods=["POST"])
@tokenRequired
def join_duel_room(username, game_id):
    try:
        # read amount of images user wants
        req = request.get_json()
        game = game_table.get_item(Key={"game_id": game_id})["Item"]
        if game["game_status"] == "started":
            if username not in game["players"]:
                return {
                    "message": "Game either started or finished already, you cannot join",
                    "data": None,
                    "error": str(e),
                }, 400
            else:
                return jsonify(game)
        elif game["game_status"] == "finished":
            return {
                "message": "Game finished already, you cannot join",
                "data": None,
                "error": str(e),
            }, 400
        elif game["game_status"] == "pending":
            if len(game["players"]) >= 2 and username not in game["players"]:
                return {
                    "message": "Duel is already full",
                    "data": None,
                    "error": str(e),
                }, 400
            elif username not in game["players"]:
                game["players"].append(username)
                success = game_table.update_item(
                    Key={"game_id": game_id},
                    UpdateExpression="SET players = :newPlayers",
                    ExpressionAttributeValues={":newPlayers": game["players"]},
                    ReturnValues="UPDATED_NEW",
                )
            return jsonify(game)
    except Exception as e:
        print("Error", str(e))
        return {
            "message": "Something went wrong",
            "data": None,
            "error": str(e),
        }, 500


@dataset.route("/start_duel/<string:game_id>", methods=["POST"])
@tokenRequired
def start_duel(username, game_id):
    game = game_table.get_item(Key={"game_id": game_id})["Item"]
    if len(game['players']) != 2:
        return {
            "message": "You need two players to start at duel",
            "data": None,
        }, 400
    if game['game_status'] == "pending":
        success = game_table.update_item(
            Key={"game_id": game_id},
            UpdateExpression="SET game_status = :newStatus",
            ExpressionAttributeValues={":newStatus": "started"},
            ReturnValues="ALL_NEW",
        )['Atrributes']
        return jsonify(success)
    else:
        return {
                "message": "Duel was not pending",
                "data": None,
            }, 400
    pass
