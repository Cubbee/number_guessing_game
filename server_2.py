import random
from flask import Flask

app = Flask(__name__)

current_number = None


@app.route("/start_game")
def start_game():
    global current_number
    current_number = random.randint(0, 100)
    return "Game started"


@app.route("/guess/<int:guess_number>")
def guess(guess_number):
    global current_number
    if not current_number:
        return "Game not started"

    if guess_number == current_number:
        current_number = None
        return "You win!"
    elif guess_number < current_number:
        return "Your guess is too low"
    else:
        return "Your guess is too high"
