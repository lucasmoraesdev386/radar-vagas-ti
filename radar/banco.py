"""Conexão com o SQLite e criação do esquema."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

CAMINHO_PADRAO = "data/radar.db"


def agora():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def conectar(caminho=CAMINHO_PADRAO):
    if str(caminho) != ":memory:":
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(caminho))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript((Path(__file__).parent / "schema.sql").read_text(encoding="utf-8"))
    return con
