from pathlib import Path
import shutil
import sqlite3
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_data_directory() -> Path:
    """
    Return the appropriate data directory.

    Development:
        <project>/data

    Packaged macOS application:
        ~/Library/Application Support/Octumo
    """

    if getattr(sys, "frozen", False):
        if sys.platform == "darwin":
            return (
                Path.home()
                / "Library"
                / "Application Support"
                / "Octumo"
            )

        return Path.home() / ".octumo"

    return PROJECT_ROOT / "data"


DATA_DIRECTORY = get_data_directory()

DATABASE_PATH = DATA_DIRECTORY / "octumo.db"


def migrate_existing_database() -> None:
    """
    Copy the existing development database into the application
    data directory on the first launch of the packaged application.

    Never overwrite an existing destination database.
    """

    if not getattr(sys, "frozen", False):
        return

    if DATABASE_PATH.exists():
        return

    legacy_database = PROJECT_ROOT / "data" / "octumo.db"

    if not legacy_database.exists():
        return

    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        legacy_database,
        DATABASE_PATH,
    )


def get_connection() -> sqlite3.Connection:
    DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    migrate_existing_database()

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection

def initialize_database() -> None:

    with get_connection() as connection:

        # =================================================
        # Main database structure
        # =================================================

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
                kind TEXT NOT NULL CHECK (
                    kind IN ('income', 'expense')
                ),
                color TEXT,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, kind)
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL,
                category_id INTEGER,
                amount_cents INTEGER NOT NULL CHECK (
                    amount_cents != 0
                ),
                transaction_date TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (
                    account_id
                )
                REFERENCES accounts(id),

                FOREIGN KEY (
                    category_id
                )
                REFERENCES categories(id)
            );

            CREATE TABLE IF NOT EXISTS balance_adjustments (
                id INTEGER PRIMARY KEY,
                account_id INTEGER NOT NULL,
                amount_cents INTEGER NOT NULL CHECK (
                    amount_cents != 0
                ),
                adjustment_date TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (
                    account_id
                )
                REFERENCES accounts(id)
                ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS recurring_transactions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                account_id INTEGER NOT NULL,
                category_id INTEGER,
                amount_cents INTEGER NOT NULL CHECK (
                    amount_cents > 0
                ),
                kind TEXT NOT NULL CHECK (
                    kind IN ('income', 'expense')
                ),
                note TEXT NOT NULL DEFAULT '',
                frequency TEXT NOT NULL CHECK (
                    frequency IN (
                        'daily',
                        'weekly',
                        'monthly',
                        'yearly'
                    )
                ),
                start_date TEXT NOT NULL,
                next_run_date TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (
                    account_id
                )
                REFERENCES accounts(id),

                FOREIGN KEY (
                    category_id
                )
                REFERENCES categories(id)
            );

            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL DEFAULT 'UserOctupus1',
                date_format TEXT NOT NULL DEFAULT 'DD.MM.YYYY',
                first_day_of_week TEXT NOT NULL DEFAULT 'Monday',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # =================================================
        # Accounts migration
        # =================================================

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
                ADD COLUMN is_active
                INTEGER NOT NULL DEFAULT 1
                """
            )

        # =================================================
        # Categories migration
        # =================================================

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
                ADD COLUMN is_active
                INTEGER NOT NULL DEFAULT 1
                """
            )

        # =================================================
        # User settings migration
        # =================================================

        user_settings_columns = connection.execute(
            "PRAGMA table_info(user_settings)"
        ).fetchall()

        user_settings_column_names = {
            column["name"]
            for column in user_settings_columns
        }

        # -------------------------------------------------
        # Add date_format to existing databases
        # -------------------------------------------------

        if "date_format" not in user_settings_column_names:

            connection.execute(
                """
                ALTER TABLE user_settings
                ADD COLUMN date_format
                TEXT NOT NULL DEFAULT 'DD.MM.YYYY'
                """
            )

        # -------------------------------------------------
        # Add first_day_of_week to existing databases
        # -------------------------------------------------

        if "first_day_of_week" not in user_settings_column_names:

            connection.execute(
                """
                ALTER TABLE user_settings
                ADD COLUMN first_day_of_week
                TEXT NOT NULL DEFAULT 'Monday'
                """
            )

        # =================================================
        # Ensure default user settings exist
        # =================================================

        connection.execute(
            """
            INSERT INTO user_settings (
                id,
                name,
                date_format,
                first_day_of_week
            )
            VALUES (
                1,
                'UserOctupus1',
                'DD.MM.YYYY',
                'Monday'
            )
            ON CONFLICT(id)
            DO NOTHING
            """
        )