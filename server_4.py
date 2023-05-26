import random
import json
import os
from flask import Flask, request

app = Flask(__name__)

number_store_p = "number_store.txt"


def save_number(user_id: int, number: int):
    current_data = {}
    if os.path.exists(number_store_p):
        with open(number_store_p, "r") as f:
            current_data = json.load(f)

    current_data[user_id] = number

    with open(number_store_p, "w") as f:
        json.dump(current_data, f)


def try_read_number(user_id: int) -> int | None:
    try:
        with open(number_store_p, "r") as f:
            current_data = json.load(f)
        return current_data[user_id]
    except (ValueError, FileNotFoundError):
        return None


@app.route("/start_game")
def start_game():
    user_id = request.headers.get("X-User-Id")
    current_number = random.randint(0, 100)
    save_number(user_id, current_number)

    return "Game started"


@app.route("/guess/<int:guess_number>")
def guess(guess_number):
    user_id = request.headers.get("X-User-Id")
    current_number = try_read_number(user_id)

    if current_number is None:
        return "Game not started"

    if guess_number == current_number:
        current_number = None
        return "You win!"
    elif guess_number < current_number:
        return "Your guess is too low"
    else:
        return "Your guess is too high"
