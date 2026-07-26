"""QualityHub application factory."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from flask import Flask, g


SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    status TEXT NOT NULL CHECK (status IN ('active', 'discontinued'))
);
"""


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    default_database = Path(app.instance_path) / "qualityhub.db"
    app.config.from_mapping(
        DATABASE=os.getenv("QUALITYHUB_DATABASE", str(default_database)),
        SECRET_KEY=os.getenv("QUALITYHUB_SECRET_KEY", "dev-only-change-me"),
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    @app.teardown_appcontext
    def close_database(_error: BaseException | None = None) -> None:
        database = g.pop("database", None)
        if database is not None:
            database.close()

    from app.routes import bp

    app.register_blueprint(bp)

    with app.app_context():
        get_database().executescript(SCHEMA)
        get_database().commit()

    return app


def get_database() -> sqlite3.Connection:
    if "database" not in g:
        g.database = sqlite3.connect(
            current_database_path(),
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.database.row_factory = sqlite3.Row
    return g.database


def current_database_path() -> str:
    from flask import current_app

    return current_app.config["DATABASE"]

