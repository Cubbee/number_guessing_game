from __future__ import annotations

import random
from logging.config import dictConfig

from flask import Flask, request
from sqlalchemy import ForeignKey, String, create_engine, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

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
engine = create_engine("sqlite:///number_guessing_orm.db", echo=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(30))

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}"


class Game(Base):
    __tablename__ = "game"
    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    player: Mapped[User] = relationship("User", backref="games")
    number: Mapped[int]
    status: Mapped[str] = mapped_column(String(30))

    def __repr__(self) -> str:
        return f"Game(id={self.id!r}, player_id={self.player_id!r}, number={self.number!r}, status={self.status!r}"


def create_database():
    Base.metadata.create_all(engine)
    app.logger.info("Creating tables...")


create_database()


def get_or_create_user(*, user_name: str, password: str) -> User:
    with Session(engine) as session:
        q = select(User).where(User.name == user_name)
        user = session.execute(q).first()

        if not user:
            user = User(name=user_name, password=password)
            session.add(user)
            session.commit()
            app.logger.info(f"Created user {user=}")
        else:
            user = user[0]
            app.logger.info(f"Found user {user=}")

        return user


def create_or_update_game(*, user: User, status: str, number: int) -> None:
    with Session(engine) as session:
        q = select(Game).where(Game.player == user)
        current_game = session.execute(q).first()

        if not current_game:
            game = Game(player=user, status=status, number=number)
            session.add(game)
            session.commit()

            app.logger.info(f"Created new game {game=}")
        else:
            current_game = current_game[0]
            app.logger.info(f"Found game {current_game=}")

            session.execute(
                update(Game),
                [{"id": current_game.id, "status": status, "number": number}],
            )
            session.commit()

            app.logger.info(f"Updated game {current_game=}")


def get_current_number(*, user: User) -> int | None:
    with Session(engine) as session:
        q = select(Game).where(Game.player == user).where(Game.status == "in_progress")
        game = session.execute(q).first()

        if not game:
            return None
        else:
            return game.number


@app.route("/start_game")
def start_game():
    user_name = request.headers.get("X-User-Name")
    app.logger.info(f"Starting game for user {user_name}")
    user = get_or_create_user(user_name=user_name, password="1234")

    current_number = random.randint(0, 100)
    app.logger.info(f"Generated number {current_number}")

    create_or_update_game(user=user, status="in_progress", number=current_number)

    return "Game started"


@app.route("/guess/<int:guess_number>")
def guess(guess_number):
    user_name = request.headers.get("X-User-Name")
    user = get_or_create_user(user_name=user_name, password="1234")

    current_number = get_current_number(user=user)

    if current_number is None:
        return "Game not started"

    app.logger.info(
        f"User {user.name} guessed {guess_number} for number {current_number}"
    )

    if guess_number == current_number:
        create_or_update_game(user=user, status="finished", number=current_number)
        return "You win!"
    elif guess_number < current_number:
        return "Your guess is too low"
    else:
        return "Your guess is too high"
