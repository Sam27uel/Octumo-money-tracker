import sqlite3

from app.database.database import get_connection


def create_account(
    name: str,
    starting_balance_cents: int = 0,
) -> int:
    clean_name = name.strip()

    if not clean_name:
        raise ValueError(
            "Account name cannot be empty."
        )

    if starting_balance_cents < 0:
        raise ValueError(
            "Starting balance cannot be negative."
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO accounts (
                name,
                starting_balance_cents,
                is_active
            )
            VALUES (?, ?, 1)
            """,
            (
                clean_name,
                starting_balance_cents,
            ),
        )

        return cursor.lastrowid


def list_accounts(
    include_archived: bool = False,
) -> list[sqlite3.Row]:
    query = """
        SELECT
            id,
            name,
            starting_balance_cents,
            is_active,
            created_at
        FROM accounts
    """

    parameters: tuple = ()

    if not include_archived:
        query += " WHERE is_active = 1"

    query += " ORDER BY name COLLATE NOCASE"

    with get_connection() as connection:
        return connection.execute(
            query,
            parameters,
        ).fetchall()


def get_account(
    account_id: int,
) -> sqlite3.Row | None:
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                id,
                name,
                starting_balance_cents,
                is_active,
                created_at
            FROM accounts
            WHERE id = ?
            """,
            (
                account_id,
            ),
        ).fetchone()


def rename_account(
    account_id: int,
    new_name: str,
) -> None:
    clean_name = new_name.strip()

    if not clean_name:
        raise ValueError(
            "Account name cannot be empty."
        )

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE accounts
            SET name = ?
            WHERE id = ?
            """,
            (
                clean_name,
                account_id,
            ),
        )


def archive_account(
    account_id: int,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE accounts
            SET is_active = 0
            WHERE id = ?
            """,
            (
                account_id,
            ),
        )


def restore_account(
    account_id: int,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE accounts
            SET is_active = 1
            WHERE id = ?
            """,
            (
                account_id,
            ),
        )


def delete_account_permanently(
    account_id: int,
) -> None:
    """
    Permanently delete an account and all data
    belonging to that account.

    The deletion order is important because
    foreign-key constraints are enabled.
    """

    with get_connection() as connection:

        # -------------------------------------------------
        # Delete recurring transaction templates first.
        # -------------------------------------------------

        connection.execute(
            """
            DELETE FROM recurring_transactions
            WHERE account_id = ?
            """,
            (
                account_id,
            ),
        )

        # -------------------------------------------------
        # Delete normal transactions.
        # -------------------------------------------------

        connection.execute(
            """
            DELETE FROM transactions
            WHERE account_id = ?
            """,
            (
                account_id,
            ),
        )

        # -------------------------------------------------
        # Delete balance adjustments.
        # -------------------------------------------------

        connection.execute(
            """
            DELETE FROM balance_adjustments
            WHERE account_id = ?
            """,
            (
                account_id,
            ),
        )

        # -------------------------------------------------
        # Finally delete the account itself.
        # -------------------------------------------------

        connection.execute(
            """
            DELETE FROM accounts
            WHERE id = ?
            """,
            (
                account_id,
            ),
        )


def delete_account(
    account_id: int,
) -> None:
    delete_account_permanently(
        account_id
    )


def add_balance_adjustment(
    account_id: int,
    amount_cents: int,
    adjustment_date: str,
    note: str = "",
) -> int:
    if amount_cents == 0:
        raise ValueError(
            "Adjustment amount cannot be zero."
        )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO balance_adjustments (
                account_id,
                amount_cents,
                adjustment_date,
                note
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                account_id,
                amount_cents,
                adjustment_date,
                note.strip(),
            ),
        )

        return cursor.lastrowid


def get_current_balance(
    account_id: int,
) -> int:
    with get_connection() as connection:

        account = connection.execute(
            """
            SELECT starting_balance_cents
            FROM accounts
            WHERE id = ?
            """,
            (
                account_id,
            ),
        ).fetchone()

        if account is None:
            raise ValueError(
                "Account not found."
            )

        starting_balance = (
            account["starting_balance_cents"]
        )

        transaction_total = connection.execute(
            """
            SELECT COALESCE(
                SUM(amount_cents),
                0
            ) AS total
            FROM transactions
            WHERE account_id = ?
            """,
            (
                account_id,
            ),
        ).fetchone()["total"]

        adjustment_total = connection.execute(
            """
            SELECT COALESCE(
                SUM(amount_cents),
                0
            ) AS total
            FROM balance_adjustments
            WHERE account_id = ?
            """,
            (
                account_id,
            ),
        ).fetchone()["total"]

        return (
            starting_balance
            + transaction_total
            + adjustment_total
        )


def list_balance_adjustments(
    account_id: int,
) -> list[sqlite3.Row]:
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                id,
                account_id,
                amount_cents,
                adjustment_date,
                note,
                created_at
            FROM balance_adjustments
            WHERE account_id = ?
            ORDER BY
                adjustment_date DESC,
                id DESC
            """,
            (
                account_id,
            ),
        ).fetchall()