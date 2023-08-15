from __future__ import annotations

import json
import logging
import os
import random
from logging.config import dictConfig

from flask import Flask, request

# logger = logging.getLogger(__name__)


dictConfig(
    {
        "version": 1,
        "root": {
            "level": "INFO",
        },
    }
)


app = Flask(__name__)

number_store_p = "number_store.json"


def save_number(user_id: str, number: int | None):
    app.logger.info(f"Saving number {number} for user {user_id}")

    current_data = {}
    if os.path.exists(number_store_p):
        try:
            with open(number_store_p) as f:
                current_data = json.load(f)
        except json.decoder.JSONDecodeError:
            app.logger.exception("Error reading number store")

    app.logger.info(f"Current data: {current_data}")

    current_data[user_id] = number

    with open(number_store_p, "w") as f:
        json.dump(current_data, f)


def try_read_number(user_id: str) -> int | None:
    app.logger.info(f"Reading number for user {user_id}")
    try:
        with open(number_store_p) as f:
            current_data = json.load(f)
        return current_data.get(user_id)
    except (ValueError, FileNotFoundError):
        app.logger.exception("Error reading number")
        return None


@app.route("/start_game")
def start_game():
    user_id = request.headers.get("X-User-Id")
    app.logger.info(f"Starting game for user {user_id}")

    current_number = random.randint(0, 100)
    app.logger.info(f"Generated number {current_number}")

    save_number(user_id, current_number)

    return "Game started"


@app.route("/guess/<int:guess_number>")
def guess(guess_number):
    user_id = request.headers.get("X-User-Id")
    current_number = try_read_number(user_id)

    if current_number is None:
        return "Game not started"

    app.logger.info(
        f"User {user_id} guessed {guess_number} for number {current_number}"
    )

    if guess_number == current_number:
        save_number(user_id, None)
        return "You win!"
    elif guess_number < current_number:
        return "Your guess is too low"
    else:
        return "Your guess is too high"
