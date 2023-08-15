CREATE TABLE IF NOT EXISTS USER (
    id integer PRIMARY KEY,
    name varchar(255) NOT NULL,
    password varchar(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS game(
    id integer PRIMARY KEY,
    player_id integer NOT NULL,
    number integer NOT NULL,
    status varchar(255) NOT NULL,
    FOREIGN KEY (player_id) REFERENCES users(id)
);

