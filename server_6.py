from __future__ import annotations

import random
import sqlite3
from logging.config import dictConfig

from flask import Flask, request

DB_FILENAME = "number_guessing.db"

dictConfig(
    {
        "version": 1,
        "root": {
            "level": "INFO",
        },
    }
)


app = Flask(__name__)


def create_database():
    with sqlite3.connect(DB_FILENAME) as db_con:
        with open("create_tables.sql") as f:
            db_con.executescript(f.read())
            app.logger.info(f"Creating tables {db_con.in_transaction=}...")


create_database()


def get_or_create_user(*, user_name: str, password: str) -> int:
    with sqlite3.connect(DB_FILENAME) as db_con:
        user = db_con.execute(
            "select * from user where name = ?", (user_name,)
        ).fetchone()

        if not user:
            db_con.execute(
                """
                INSERT INTO user (name, password) VALUES (?, ?)
                """,
                (user_name, password),
            )

            user = db_con.execute(
                "select * from user where name = ?", (user_name,)
            ).fetchone()
            app.logger.info(f"Created user {user=}")
        else:
            app.logger.info(f"Found user {user=}")

        return user[0]


def create_or_update_game(*, user_id: int, status: str, number: int) -> None:
    with sqlite3.connect(DB_FILENAME) as db_con:
        current_game = db_con.execute(
            "select * from game where player_id = ?", (user_id,)
        ).fetchone()

        if not current_game:
            db_con.execute(
                """
                INSERT INTO game (player_id, status, number) VALUES (?, ?, ?)
                """,
                (user_id, status, number),
            )
            app.logger.info(
                f"Created new game for user {user_id=}: {status=}, {number=}"
            )
        else:
            app.logger.info(f"Found game for user {user_id=}: {status=}, {number=}")
            db_con.execute(
                """
                UPDATE game SET status = ?, number = ? WHERE player_id = ?
                """,
                (status, number, user_id),
            )
            app.logger.info(f"Updated game for user {user_id=}: {status=}, {number=}")


def get_current_number(*, user_id: int) -> int | None:
    with sqlite3.connect(DB_FILENAME) as db_con:
        current_game = db_con.execute(
            "select * from game where player_id = ? and status = 'in_progress'",
            (user_id,),
        ).fetchone()

        if not current_game:
            return None
        else:
            return current_game[2]


@app.route("/start_game")
def start_game():
    user_name = request.headers.get("X-User-Name")
    app.logger.info(f"Starting game for user {user_name}")
    user_id = get_or_create_user(user_name=user_name, password="1234")

    current_number = random.randint(0, 100)
    app.logger.info(f"Generated number {current_number}")

    create_or_update_game(user_id=user_id, status="in_progress", number=current_number)

    return "Game started"


@app.route("/guess/<int:guess_number>")
def guess(guess_number):
    user_name = request.headers.get("X-User-Name")
    user_id = get_or_create_user(user_name=user_name, password="1234")

    current_number = get_current_number(user_id=user_id)

    if current_number is None:
        return "Game not started"

    app.logger.info(
        f"User {user_id} guessed {guess_number} for number {current_number}"
    )

    if guess_number == current_number:
        create_or_update_game(user_id=user_id, status="finished", number=current_number)
        return "You win!"
    elif guess_number < current_number:
        return "Your guess is too low"
    else:
        return "Your guess is too high"
