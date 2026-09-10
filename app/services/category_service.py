import sqlite3

from app.database.database import get_connection


VALID_CATEGORY_KINDS = {"income", "expense"}


def create_category(
    name: str,
    kind: str,
    color: str | None = None,
) -> int:
    clean_name = name.strip()

    if not clean_name:
        raise ValueError("Category name cannot be empty.")

    if kind not in VALID_CATEGORY_KINDS:
        raise ValueError("Category kind must be 'income' or 'expense'.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO categories (name, kind, color)
            VALUES (?, ?, ?)
            """,
            (clean_name, kind, color),
        )
        return cursor.lastrowid


def list_categories(kind: str | None = None) -> list[sqlite3.Row]:
    query = "SELECT id, name, kind, color FROM categories"
    parameters: tuple[str, ...] = ()

    if kind is not None:
        if kind not in VALID_CATEGORY_KINDS:
            raise ValueError("Category kind must be 'income' or 'expense'.")

        query += " WHERE kind = ?"
        parameters = (kind,)

    query += " ORDER BY name COLLATE NOCASE"

    with get_connection() as connection:
        return connection.execute(query, parameters).fetchall()


def delete_category(category_id: int) -> None:
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM categories WHERE id = ?",
            (category_id,),
        )