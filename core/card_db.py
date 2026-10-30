"""Read card data from EDOPro cards.cdb (SQLite)."""

import sqlite3
import os


class CardDB:
    def __init__(self, db_path):
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Card database not found: {db_path}")
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row

    def close(self):
        self._conn.close()

    def get_card(self, card_id):
        row = self._conn.execute(
            "SELECT d.*, t.name, t.desc FROM datas d "
            "JOIN texts t ON d.id = t.id WHERE d.id = ?",
            (card_id,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)

    def get_cards(self, card_ids):
        if not card_ids:
            return {}
        placeholders = ",".join("?" * len(card_ids))
        rows = self._conn.execute(
            f"SELECT d.*, t.name, t.desc FROM datas d "
            f"JOIN texts t ON d.id = t.id WHERE d.id IN ({placeholders})",
            list(card_ids),
        ).fetchall()
        return {row["id"]: dict(row) for row in rows}

    def search(self, query, limit=50):
        rows = self._conn.execute(
            "SELECT d.*, t.name, t.desc FROM datas d "
            "JOIN texts t ON d.id = t.id "
            "WHERE t.name LIKE ? OR t.desc LIKE ? "
            "ORDER BY t.name LIMIT ?",
            (f"%{query}%", f"%{query}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def search_by_type(self, type_mask, limit=100):
        rows = self._conn.execute(
            "SELECT d.*, t.name, t.desc FROM datas d "
            "JOIN texts t ON d.id = t.id "
            "WHERE (d.type & ?) != 0 "
            "ORDER BY t.name LIMIT ?",
            (type_mask, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def search_by_attribute(self, attribute, limit=100):
        rows = self._conn.execute(
            "SELECT d.*, t.name, t.desc FROM datas d "
            "JOIN texts t ON d.id = t.id "
            "WHERE d.attribute = ? "
            "ORDER BY t.name LIMIT ?",
            (attribute, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def search_by_race(self, race, limit=100):
        rows = self._conn.execute(
            "SELECT d.*, t.name, t.desc FROM datas d "
            "JOIN texts t ON d.id = t.id "
            "WHERE d.race = ? "
            "ORDER BY t.name LIMIT ?",
            (race, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def all_names(self):
        rows = self._conn.execute(
            "SELECT id, name FROM texts ORDER BY name"
        ).fetchall()
        return {row["id"]: row["name"] for row in rows}

    def count(self):
        row = self._conn.execute("SELECT count(*) as c FROM datas").fetchone()
        return row["c"]

    def get_name(self, card_id):
        row = self._conn.execute(
            "SELECT name FROM texts WHERE id = ?", (card_id,)
        ).fetchone()
        return row["name"] if row else str(card_id)
