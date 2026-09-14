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
        raise ValueError(
            "Category kind must be 'income' or 'expense'."
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO categories (
                name,
                kind,
                color,
                is_active
            )
            VALUES (?, ?, ?, 1)
            """,
            (clean_name, kind, color),
        )

        return cursor.lastrowid


def list_categories(
    kind: str | None = None,
    include_archived: bool = False,
) -> list[sqlite3.Row]:
    query = """
        SELECT
            id,
            name,
            kind,
            color,
            is_active
        FROM categories
    """

    conditions = []
    parameters = []

    if kind is not None:
        if kind not in VALID_CATEGORY_KINDS:
            raise ValueError(
                "Category kind must be 'income' or 'expense'."
            )

        conditions.append("kind = ?")
        parameters.append(kind)

    if not include_archived:
        conditions.append("is_active = 1")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += """
        ORDER BY
            name COLLATE NOCASE
    """

    with get_connection() as connection:
        return connection.execute(
            query,
            tuple(parameters),
        ).fetchall()


def get_category(
    category_id: int,
) -> sqlite3.Row | None:
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                id,
                name,
                kind,
                color,
                is_active
            FROM categories
            WHERE id = ?
            """,
            (category_id,),
        ).fetchone()


def update_category(
    category_id: int,
    name: str,
) -> None:
    clean_name = name.strip()

    if not clean_name:
        raise ValueError(
            "Category name cannot be empty."
        )

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE categories
            SET name = ?
            WHERE id = ?
            """,
            (clean_name, category_id),
        )


def get_category_usage_count(
    category_id: int,
) -> int:
    with get_connection() as connection:
        result = connection.execute(
            """
            SELECT COUNT(*) AS usage_count
            FROM transactions
            WHERE category_id = ?
            """,
            (category_id,),
        ).fetchone()

        return result["usage_count"]


def archive_category(
    category_id: int,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE categories
            SET is_active = 0
            WHERE id = ?
            """,
            (category_id,),
        )


def restore_category(
    category_id: int,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE categories
            SET is_active = 1
            WHERE id = ?
            """,
            (category_id,),
        )


def delete_category(
    category_id: int,
) -> None:
    usage_count = get_category_usage_count(category_id)

    if usage_count > 0:
        raise ValueError(
            "Category cannot be deleted because it is used "
            "by existing transactions."
        )

    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM categories
            WHERE id = ?
            """,
            (category_id,),
        )