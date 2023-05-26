import random
from flask import Flask

app = Flask(__name__)

number_store_p = "number_store.txt"


def save_number(number):
    with open(number_store_p, "w") as f:
        f.write(str(number))


def try_read_number():
    try:
        with open(number_store_p, "r") as f:
            return int(f.read())
    except (ValueError, FileNotFoundError):
        return None


@app.route("/start_game")
def start_game():
    current_number = random.randint(0, 100)
    save_number(current_number)

    return "Game started"


@app.route("/guess/<int:guess_number>")
def guess(guess_number):
    current_number = try_read_number()

    if current_number is None:
        return "Game not started"

    if guess_number == current_number:
        current_number = None
        return "You win!"
    elif guess_number < current_number:
        return "Your guess is too low"
    else:
        return "Your guess is too high"
