import math
import random
import time


def update_rating(current_rating, correct_answers, wrong_answers):

    correct_weight = min(125, 100000 // current_rating)
    accuracy_level = current_rating / 5000

    wrong_weight = math.ceil(correct_weight * accuracy_level / (1 - accuracy_level))

    new_rating = (
        current_rating + correct_answers * correct_weight - wrong_answers * wrong_weight
    )

    return new_rating


def generate_random_string():
    return "".join(
        random.choice("0123456789abcdefghijklmnopqrstuvwxyz") for _ in range(7)
    )
