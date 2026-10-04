from datetime import date, timedelta
from typing import Optional

from app.database.database import get_connection
from app.services.transaction_service import create_transaction


VALID_KINDS = {
    "income",
    "expense",
}

VALID_FREQUENCIES = {
    "daily",
    "weekly",
    "monthly",
    "yearly",
}


# =========================================================
# Validation
# =========================================================


def _validate_kind(kind: str) -> None:
    if kind not in VALID_KINDS:
        raise ValueError(
            f"Unsupported transaction kind: {kind}"
        )


def _validate_frequency(frequency: str) -> None:
    if frequency not in VALID_FREQUENCIES:
        raise ValueError(
            f"Unsupported recurring frequency: {frequency}"
        )


def _validate_amount(amount_cents: int) -> None:
    if not isinstance(amount_cents, int):
        raise ValueError(
            "Amount must be an integer number of cents."
        )

    if amount_cents <= 0:
        raise ValueError(
            "Amount must be greater than zero."
        )


def _validate_date(date_value: str) -> None:
    try:
        date.fromisoformat(date_value)
    except (ValueError, TypeError):
        raise ValueError(
            f"Invalid date: {date_value}"
        )


def _validate_account(account_id: int) -> None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id
            FROM accounts
            WHERE id = ?
            """,
            (account_id,),
        ).fetchone()

    if row is None:
        raise ValueError(
            f"Account with id {account_id} does not exist."
        )


def _validate_category(category_id: int) -> None:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id
            FROM categories
            WHERE id = ?
            """,
            (category_id,),
        ).fetchone()

    if row is None:
        raise ValueError(
            f"Category with id {category_id} does not exist."
        )


# =========================================================
# Date helpers
# =========================================================


def _add_month(current_date: date) -> date:
    """
    Add one month while keeping the day where possible.

    Examples:
        2026-01-31 -> 2026-02-28
        2026-03-31 -> 2026-04-30
        2026-05-15 -> 2026-06-15
    """

    if current_date.month == 12:
        target_year = current_date.year + 1
        target_month = 1
    else:
        target_year = current_date.year
        target_month = current_date.month + 1

    # First day of the following month.
    if target_month == 12:
        next_month = date(
            target_year + 1,
            1,
            1,
        )
    else:
        next_month = date(
            target_year,
            target_month + 1,
            1,
        )

    # Last day of target month.
    last_day = (
        next_month - timedelta(days=1)
    ).day

    target_day = min(
        current_date.day,
        last_day,
    )

    return date(
        target_year,
        target_month,
        target_day,
    )


def _add_year(current_date: date) -> date:
    """
    Add one year.

    February 29 is changed to February 28
    if the next year is not a leap year.
    """

    target_year = current_date.year + 1

    if (
        current_date.month == 2
        and current_date.day == 29
    ):
        return date(
            target_year,
            2,
            28,
        )

    return date(
        target_year,
        current_date.month,
        current_date.day,
    )


def _next_date(
    current_date: date,
    frequency: str,
) -> date:
    """
    Return the next occurrence after current_date.
    """

    _validate_frequency(frequency)

    if frequency == "daily":
        return current_date + timedelta(
            days=1
        )

    if frequency == "weekly":
        return current_date + timedelta(
            days=7
        )

    if frequency == "monthly":
        return _add_month(
            current_date
        )

    if frequency == "yearly":
        return _add_year(
            current_date
        )

    raise ValueError(
        f"Unsupported frequency: {frequency}"
    )


# =========================================================
# Create recurring transaction
# =========================================================


def create_recurring_transaction(
    name: str,
    account_id: int,
    category_id: int,
    amount_cents: int,
    kind: str,
    start_date: str,
    frequency: str,
    note: Optional[str] = None,
) -> int:
    """
    Create a recurring transaction.

    The first automatic occurrence is AFTER start_date.

    Examples:

        2026-10-03 + daily
            -> 2026-10-04

        2026-10-03 + weekly
            -> 2026-10-10

        2026-10-03 + monthly
            -> 2026-11-03

        2026-10-03 + yearly
            -> 2027-10-03
    """

    _validate_kind(kind)
    _validate_frequency(frequency)
    _validate_amount(amount_cents)
    _validate_date(start_date)
    _validate_account(account_id)
    _validate_category(category_id)

    start_date_obj = date.fromisoformat(
        start_date
    )

    # The current transaction is already created.
    # Therefore the recurring transaction must point
    # to the NEXT occurrence, not start_date itself.
    first_run_date = _next_date(
        start_date_obj,
        frequency,
    ).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO recurring_transactions (
                name,
                account_id,
                category_id,
                amount_cents,
                kind,
                start_date,
                frequency,
                note,
                next_run_date,
                is_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
            """,
            (
                name,
                account_id,
                category_id,
                amount_cents,
                kind,
                start_date,
                frequency,
                note,
                first_run_date,
            ),
        )

        return cursor.lastrowid


# =========================================================
# Update recurring transaction
# =========================================================


def update_recurring_transaction(
    recurring_transaction_id: int,
    name: str,
    account_id: int,
    category_id: int,
    amount_cents: int,
    kind: str,
    start_date: str,
    frequency: str,
    note: Optional[str] = None,
    is_active: bool = True,
) -> None:
    """
    Update an existing recurring transaction.

    IMPORTANT:
    recurring_transaction_id is intentionally used as the
    parameter name because EditTransactionDialog calls this
    function using that keyword.

    next_run_date is recalculated from:

        start_date + frequency

    Examples:

        start_date = 2026-10-04

        daily
            -> 2026-10-05

        weekly
            -> 2026-10-11

        monthly
            -> 2026-11-04

        yearly
            -> 2027-10-04
    """

    _validate_kind(kind)
    _validate_frequency(frequency)
    _validate_amount(amount_cents)
    _validate_date(start_date)
    _validate_account(account_id)
    _validate_category(category_id)

    start_date_obj = date.fromisoformat(
        start_date
    )

    # The edited transaction itself represents start_date.
    # Therefore the next automatic occurrence is one
    # frequency interval after it.
    next_run_date = _next_date(
        start_date_obj,
        frequency,
    ).isoformat()

    with get_connection() as connection:

        existing = connection.execute(
            """
            SELECT id
            FROM recurring_transactions
            WHERE id = ?
            """,
            (
                recurring_transaction_id,
            ),
        ).fetchone()

        if existing is None:
            raise ValueError(
                "Recurring transaction does not exist."
            )

        connection.execute(
            """
            UPDATE recurring_transactions
            SET
                name = ?,
                account_id = ?,
                category_id = ?,
                amount_cents = ?,
                kind = ?,
                start_date = ?,
                frequency = ?,
                note = ?,
                next_run_date = ?,
                is_active = ?
            WHERE id = ?
            """,
            (
                name,
                account_id,
                category_id,
                amount_cents,
                kind,
                start_date,
                frequency,
                note,
                next_run_date,
                1 if is_active else 0,
                recurring_transaction_id,
            ),
        )


# =========================================================
# Delete recurring transaction
# =========================================================


def delete_recurring_transaction(
    recurring_transaction_id: int,
) -> None:
    """
    Delete a recurring transaction template.
    """

    with get_connection() as connection:
        connection.execute(
            """
            DELETE FROM recurring_transactions
            WHERE id = ?
            """,
            (
                recurring_transaction_id,
            ),
        )


# =========================================================
# Get recurring transaction
# =========================================================


def get_recurring_transaction(
    recurring_transaction_id: int,
):
    """
    Return one recurring transaction by ID.
    """

    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                id,
                name,
                account_id,
                category_id,
                amount_cents,
                kind,
                start_date,
                frequency,
                note,
                next_run_date,
                is_active
            FROM recurring_transactions
            WHERE id = ?
            """,
            (
                recurring_transaction_id,
            ),
        ).fetchone()


# =========================================================
# List recurring transactions
# =========================================================


def list_recurring_transactions(
    include_inactive: bool = False,
):
    """
    Return recurring transactions.

    By default only active recurring transactions
    are returned.
    """

    with get_connection() as connection:

        if include_inactive:
            return connection.execute(
                """
                SELECT
                    id,
                    name,
                    account_id,
                    category_id,
                    amount_cents,
                    kind,
                    start_date,
                    frequency,
                    note,
                    next_run_date,
                    is_active
                FROM recurring_transactions
                ORDER BY
                    next_run_date ASC,
                    id ASC
                """
            ).fetchall()

        return connection.execute(
            """
            SELECT
                id,
                name,
                account_id,
                category_id,
                amount_cents,
                kind,
                start_date,
                frequency,
                note,
                next_run_date,
                is_active
            FROM recurring_transactions
            WHERE is_active = 1
            ORDER BY
                next_run_date ASC,
                id ASC
            """
        ).fetchall()


# =========================================================
# List due recurring transactions
# =========================================================


def list_due_recurring_transactions(
    run_date: Optional[str] = None,
):
    """
    Return active recurring transactions where:

        next_run_date <= run_date

    If run_date is omitted, today's date is used.
    """

    if run_date is None:
        run_date = date.today().isoformat()

    _validate_date(run_date)

    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                id,
                name,
                account_id,
                category_id,
                amount_cents,
                kind,
                start_date,
                frequency,
                note,
                next_run_date,
                is_active
            FROM recurring_transactions
            WHERE
                is_active = 1
                AND next_run_date <= ?
            ORDER BY
                next_run_date ASC,
                id ASC
            """,
            (
                run_date,
            ),
        ).fetchall()


# =========================================================
# Generate due transactions
# =========================================================


def generate_due_transactions(
    run_date: Optional[str] = None,
) -> int:
    """
    Generate all recurring transactions that are due.

    Also handles missed occurrences.

    Example:

        next_run_date = 2026-10-04
        frequency = daily

    App opened on:

        2026-10-06

    Generated transactions:

        2026-10-04
        2026-10-05
        2026-10-06

    New next_run_date:

        2026-10-07
    """

    if run_date is None:
        run_date = date.today().isoformat()

    _validate_date(run_date)

    generated_count = 0

    # Continue until no recurring transaction is overdue.
    while True:

        due_transactions = (
            list_due_recurring_transactions(
                run_date
            )
        )

        if not due_transactions:
            break

        for recurring in due_transactions:

            transaction_date = (
                recurring["next_run_date"]
            )

            # -------------------------------------------------
            # Create actual transaction.
            # -------------------------------------------------

            create_transaction(
                account_id=recurring["account_id"],
                category_id=recurring["category_id"],
                amount_cents=recurring["amount_cents"],
                transaction_date=transaction_date,
                note=recurring["note"] or "",
                kind=recurring["kind"],
            )

            # -------------------------------------------------
            # Calculate next occurrence.
            # -------------------------------------------------

            current_date = date.fromisoformat(
                recurring["next_run_date"]
            )

            next_date = _next_date(
                current_date,
                recurring["frequency"],
            )

            # -------------------------------------------------
            # Update recurring template.
            # -------------------------------------------------

            with get_connection() as connection:
                connection.execute(
                    """
                    UPDATE recurring_transactions
                    SET next_run_date = ?
                    WHERE id = ?
                    """,
                    (
                        next_date.isoformat(),
                        recurring["id"],
                    ),
                )

            generated_count += 1

    return generated_count