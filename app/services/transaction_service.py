from datetime import date
from typing import Optional

from app.database.database import get_connection


VALID_TRANSACTION_KINDS = {
    "income",
    "expense",
}


def _validate_kind(kind: str) -> None:
    if kind not in VALID_TRANSACTION_KINDS:
        raise ValueError(
            "Transaction kind must be either 'income' or 'expense'."
        )


def _validate_amount(amount_cents: int) -> None:
    if amount_cents <= 0:
        raise ValueError(
            "Amount must be greater than zero."
        )


def _validate_date(transaction_date: str) -> None:
    try:
        date.fromisoformat(transaction_date)
    except ValueError:
        raise ValueError(
            "Transaction date must be in YYYY-MM-DD format."
        )


def _validate_account(
    connection,
    account_id: int,
) -> None:
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
            "Selected account does not exist or is inactive."
        )


def _validate_category(
    connection,
    category_id: Optional[int],
    kind: str,
) -> None:
    if category_id is None:
        return

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
            "Selected category does not exist or is inactive."
        )

    if category["kind"] != kind:
        raise ValueError(
            "Selected category does not match the transaction type."
        )


def _signed_amount(
    amount_cents: int,
    kind: str,
) -> int:
    if kind == "income":
        return abs(amount_cents)

    return -abs(amount_cents)


def create_transaction(
    account_id: int,
    category_id: Optional[int],
    amount_cents: int,
    transaction_date: str,
    note: str = "",
    kind: str = "expense",
) -> int:
    """
    Create a normal one-time transaction.

    Positive amount is used for income.
    Negative amount is used for expense.
    """

    note = note.strip()

    _validate_kind(kind)
    _validate_amount(amount_cents)
    _validate_date(transaction_date)

    with get_connection() as connection:
        _validate_account(
            connection,
            account_id,
        )

        _validate_category(
            connection,
            category_id,
            kind,
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
                _signed_amount(
                    amount_cents,
                    kind,
                ),
                transaction_date,
                note,
            ),
        )

        return cursor.lastrowid


def list_transactions(
    account_id: Optional[int] = None,
    category_id: Optional[int] = None,
    kind: Optional[str] = None,
):
    if kind is not None:
        _validate_kind(kind)

    query = """
        SELECT
            transactions.id,
            transactions.account_id,
            transactions.category_id,
            transactions.amount_cents,
            transactions.transaction_date,
            transactions.note,
            transactions.created_at,
            accounts.name AS account_name,
            categories.name AS category_name,
            CASE
                WHEN transactions.amount_cents > 0
                    THEN 'income'
                ELSE 'expense'
            END AS kind
        FROM transactions
        INNER JOIN accounts
            ON accounts.id = transactions.account_id
        LEFT JOIN categories
            ON categories.id = transactions.category_id
        WHERE 1 = 1
    """

    parameters = []

    if account_id is not None:
        query += """
            AND transactions.account_id = ?
        """
        parameters.append(account_id)

    if category_id is not None:
        query += """
            AND transactions.category_id = ?
        """
        parameters.append(category_id)

    if kind == "income":
        query += """
            AND transactions.amount_cents > 0
        """

    elif kind == "expense":
        query += """
            AND transactions.amount_cents < 0
        """

    query += """
        ORDER BY
            transactions.transaction_date DESC,
            transactions.id DESC
    """

    with get_connection() as connection:
        rows = connection.execute(
            query,
            parameters,
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def get_transaction(
    transaction_id: int,
):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                transactions.id,
                transactions.account_id,
                transactions.category_id,
                transactions.amount_cents,
                transactions.transaction_date,
                transactions.note,
                transactions.created_at,
                accounts.name AS account_name,
                categories.name AS category_name,
                CASE
                    WHEN transactions.amount_cents > 0
                        THEN 'income'
                    ELSE 'expense'
                END AS kind
            FROM transactions
            INNER JOIN accounts
                ON accounts.id = transactions.account_id
            LEFT JOIN categories
                ON categories.id = transactions.category_id
            WHERE transactions.id = ?
            """,
            (transaction_id,),
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def update_transaction(
    transaction_id: int,
    account_id: int,
    category_id: Optional[int],
    amount_cents: int,
    transaction_date: str,
    note: str = "",
    kind: str = "expense",
) -> None:
    """
    Update an existing transaction.
    """

    note = note.strip()

    _validate_kind(kind)
    _validate_amount(amount_cents)
    _validate_date(transaction_date)

    with get_connection() as connection:
        existing = connection.execute(
            """
            SELECT id
            FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        ).fetchone()

        if existing is None:
            raise ValueError(
                "Transaction does not exist."
            )

        _validate_account(
            connection,
            account_id,
        )

        _validate_category(
            connection,
            category_id,
            kind,
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
                _signed_amount(
                    amount_cents,
                    kind,
                ),
                transaction_date,
                note,
                transaction_id,
            ),
        )


def delete_transaction(
    transaction_id: int,
) -> None:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM transactions
            WHERE id = ?
            """,
            (transaction_id,),
        )

        if cursor.rowcount == 0:
            raise ValueError(
                "Transaction does not exist."
            )