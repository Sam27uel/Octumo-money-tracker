from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIRECTORY = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIRECTORY / "octumo.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                starting_balance_cents INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                kind TEXT NOT NULL CHECK (kind IN ('income', 'expense')),
                color TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, kind)
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL,
                category_id INTEGER,
                amount_cents INTEGER NOT NULL CHECK (amount_cents != 0),
                transaction_date TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );

            CREATE TABLE IF NOT EXISTS balance_adjustments (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL,
                amount_cents INTEGER NOT NULL CHECK (amount_cents != 0),
                adjustment_date TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                account_id INTEGER NOT NULL,
                category_id INTEGER,
                amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
                kind TEXT NOT NULL CHECK (kind IN ('income', 'expense')),
                note TEXT NOT NULL DEFAULT '',
                frequency TEXT NOT NULL CHECK (
                    frequency IN ('daily', 'weekly', 'monthly', 'yearly')
                ),
                start_date TEXT NOT NULL,
                next_run_date TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(id),
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );
            """
        )

        # Migration for existing databases:
        # Add is_active to accounts if the column does not exist yet.
        account_columns = connection.execute(
            "PRAGMA table_info(accounts)"
        ).fetchall()

        account_column_names = {
            column["name"]
            for column in account_columns
        }

        if "is_active" not in account_column_names:
            connection.execute(
                """
                ALTER TABLE accounts
                ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
                """
            )

        # Migration for existing databases:
        # Add is_active to categories if the column does not exist yet.
        category_columns = connection.execute(
            "PRAGMA table_info(categories)"
        ).fetchall()

        category_column_names = {
            column["name"]
            for column in category_columns
        }

        if "is_active" not in category_column_names:
            connection.execute(
                """
                ALTER TABLE categories
                ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
                """
            )