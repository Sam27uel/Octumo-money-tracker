import sqlite3

from app.database.database import get_connection


def create_account(
    name: str,
    starting_balance_cents: int = 0,
) -> int:
    clean_name = name.strip()

    if not clean_name:
        raise ValueError("Account name cannot be empty.")

    if starting_balance_cents < 0:
        raise ValueError("Starting balance cannot be negative.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO accounts (name, starting_balance_cents)
            VALUES (?, ?)
            """,
            (clean_name, starting_balance_cents),
        )
        return cursor.lastrowid


def list_accounts() -> list[sqlite3.Row]:
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT id, name, starting_balance_cents, created_at
            FROM accounts
            ORDER BY name COLLATE NOCASE
            """
        ).fetchall()


def delete_account(account_id: int) -> None:
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM accounts WHERE id = ?",
            (account_id,),
        )