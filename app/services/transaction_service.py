import sqlite3

from app.database.database import get_connection


VALID_TRANSACTION_KINDS = {"income", "expense"}


def create_transaction(
    account_id: int,
    category_id: int | None,
    amount_cents: int,
    transaction_date: str,
    note: str = "",
    kind: str = "expense",
) -> int:
    if kind not in VALID_TRANSACTION_KINDS:
        raise ValueError(
            "Transaction kind must be 'income' or 'expense'."
        )

    if amount_cents <= 0:
        raise ValueError(
            "Transaction amount must be greater than zero."
        )

    clean_note = note.strip()

    with get_connection() as connection:
        account = connection.execute(
            """
            SELECT id
            FROM accounts
            WHERE id = ?
              AND is_active = 1
            """,
            (account_id,),
        ).fetchone()

        if account is None:
            raise ValueError(
                "Account not found or is archived."
            )

        if category_id is not None:
            category = connection.execute(
                """
                SELECT id, kind
                FROM categories
                WHERE id = ?
                  AND is_active = 1
                """,
                (category_id,),
            ).fetchone()

            if category is None:
                raise ValueError(
                    "Category not found or is archived."
                )

            if category["kind"] != kind:
                raise ValueError(
                    "Category type does not match transaction type."
                )

        signed_amount_cents = (
            amount_cents
            if kind == "income"
            else -amount_cents
        )

        cursor = connection.execute(
            """
            INSERT INTO transactions (
                account_id,
                category_id,
                amount_cents,
                transaction_date,
                note
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                account_id,
                category_id,
                signed_amount_cents,
                transaction_date,
                clean_note,
            ),
        )

        return cursor.lastrowid


def list_transactions(
    account_id: int | None = None,
    category_id: int | None = None,
    kind: str | None = None,
) -> list[sqlite3.Row]:
    if kind is not None and kind not in VALID_TRANSACTION_KINDS:
        raise ValueError(
            "Transaction kind must be 'income' or 'expense'."
        )

    query = """
        SELECT
            transactions.id,
            transactions.account_id,
            accounts.name AS account_name,
            transactions.category_id,
            categories.name AS category_name,
            categories.kind AS category_kind,
            categories.color AS category_color,
            transactions.amount_cents,
            transactions.transaction_date,
            transactions.note,
            transactions.created_at
        FROM transactions

        INNER JOIN accounts
            ON accounts.id = transactions.account_id

        LEFT JOIN categories
            ON categories.id = transactions.category_id
    """

    conditions = []
    parameters = []

    if account_id is not None:
        conditions.append(
            "transactions.account_id = ?"
        )
        parameters.append(account_id)

    if category_id is not None:
        conditions.append(
            "transactions.category_id = ?"
        )
        parameters.append(category_id)

    if kind is not None:
        if kind == "income":
            conditions.append(
                "transactions.amount_cents > 0"
            )
        else:
            conditions.append(
                "transactions.amount_cents < 0"
            )

    if conditions:
        query += " WHERE " + " AND ".join(
            conditions
        )

    query += """
        ORDER BY
            transactions.transaction_date DESC,
            transactions.id DESC
    """

    with get_connection() as connection:
        return connection.execute(
            query,
            tuple(parameters),
        ).fetchall()


def get_transaction(
    transaction_id: int,
) -> sqlite3.Row | None:
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                transactions.id,
                transactions.account_id,
                accounts.name AS account_name,
                transactions.category_id,
                categories.name AS category_name,
                categories.kind AS category_kind,
                categories.color AS category_color,
                transactions.amount_cents,
                transactions.transaction_date,
                transactions.note,
                transactions.created_at
            FROM transactions

            INNER JOIN accounts
                ON accounts.id = transactions.account_id

            LEFT JOIN categories
                ON categories.id = transactions.category_id

            WHERE transactions.id = ?
            """,
            (transaction_id,),
        ).fetchone()


def update_transaction(
    transaction_id: int,
    account_id: int,
    category_id: int | None,
    amount_cents: int,
    transaction_date: str,
    note: str = "",
    kind: str = "expense",
) -> None:
    if kind not in VALID_TRANSACTION_KINDS:
        raise ValueError(
            "Transaction kind must be 'income' or 'expense'."
        )

    if amount_cents <= 0:
        raise ValueError(
            "Transaction amount must be greater than zero."
        )

    clean_note = note.strip()

    with get_connection() as connection:
        account = connection.execute(
            """
            SELECT id
            FROM accounts
            WHERE id = ?
              AND is_active = 1
            """,
            (account_id,),
        ).fetchone()

        if account is None:
            raise ValueError(
                "Account not found or is archived."
            )

        if category_id is not None:
            category = connection.execute(
                """
                SELECT id, kind
                FROM categories
                WHERE id = ?
                """,
                (category_id,),
            ).fetchone()

            if category is None:
                raise ValueError(
                    "Category not found."
                )

            if category["kind"] != kind:
                raise ValueError(
                    "Category type does not match transaction type."
                )

        signed_amount_cents = (
            amount_cents
            if kind == "income"
            else -amount_cents
        )

        connection.execute(
            """
            UPDATE transactions
            SET
                account_id = ?,
                category_id = ?,
                amount_cents = ?,
                transaction_date = ?,
                note = ?
            WHERE id = ?
            """,
            (
                account_id,
                category_id,
                signed_amount_cents,
                transaction_date,
                clean_note,
                transaction_id,
            ),
        )


def delete_transaction(
    transaction_id: int,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        )