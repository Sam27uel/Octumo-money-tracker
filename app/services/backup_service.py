import json

from datetime import datetime
from pathlib import Path
from typing import Any

from app.database.database import get_connection


BACKUP_FORMAT = "octumo-backup"
BACKUP_VERSION = 1


BACKUP_TABLES = [
    "accounts",
    "categories",
    "transactions",
    "balance_adjustments",
    "recurring_transactions",
    "user_settings",
]


def _serialize_value(value: Any) -> Any:
    """
    Convert SQLite values into JSON-compatible values.
    """

    if isinstance(value, bytes):
        return value.decode(
            "utf-8",
            errors="replace",
        )

    return value


def export_database(
    file_path: str | Path,
) -> None:

    file_path = Path(file_path)

    tables: dict[str, list[dict[str, Any]]] = {}

    with get_connection() as connection:

        for table_name in BACKUP_TABLES:

            rows = connection.execute(
                f"""
                SELECT *
                FROM {table_name}
                ORDER BY id ASC
                """
            ).fetchall()

            tables[table_name] = [
                {
                    key: _serialize_value(value)
                    for key, value in dict(row).items()
                }
                for row in rows
            ]

    backup = {
        "format": BACKUP_FORMAT,
        "version": BACKUP_VERSION,
        "created_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "tables": tables,
    }

    file_path.write_text(
        json.dumps(
            backup,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def validate_backup(
    backup: dict[str, Any],
) -> None:

    if not isinstance(
        backup,
        dict,
    ):
        raise ValueError(
            "Invalid Octumo backup."
        )

    if backup.get("format") != BACKUP_FORMAT:

        raise ValueError(
            "This file is not a valid Octumo backup."
        )

    if backup.get("version") != BACKUP_VERSION:

        raise ValueError(
            "Unsupported Octumo backup version."
        )

    tables = backup.get(
        "tables"
    )

    if not isinstance(
        tables,
        dict,
    ):
        raise ValueError(
            "Backup does not contain valid table data."
        )

    for table_name in BACKUP_TABLES:

        if table_name not in tables:

            raise ValueError(
                f"Backup is missing table: {table_name}"
            )

        if not isinstance(
            tables[table_name],
            list,
        ):
            raise ValueError(
                f"Invalid data for table: {table_name}"
            )


def load_backup(
    file_path: str | Path,
) -> dict[str, Any]:

    file_path = Path(file_path)

    if not file_path.exists():

        raise FileNotFoundError(
            "Backup file does not exist."
        )

    try:

        backup = json.loads(
            file_path.read_text(
                encoding="utf-8"
            )
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "The selected file is not valid JSON."
        ) from error

    validate_backup(
        backup
    )

    return backup


def restore_database(
    file_path: str | Path,
) -> None:

    backup = load_backup(
        file_path
    )

    tables = backup["tables"]

    with get_connection() as connection:

        try:

            connection.execute(
                "PRAGMA foreign_keys = OFF"
            )

            connection.execute(
                "BEGIN"
            )

            # ---------------------------------------------
            # Clear current data.
            # ---------------------------------------------

            for table_name in reversed(
                BACKUP_TABLES
            ):

                connection.execute(
                    f"DELETE FROM {table_name}"
                )

            # ---------------------------------------------
            # Restore in dependency order.
            # ---------------------------------------------

            for table_name in BACKUP_TABLES:

                rows = tables[table_name]

                if not rows:
                    continue

                columns = list(
                    rows[0].keys()
                )

                column_sql = ", ".join(
                    f'"{column}"'
                    for column in columns
                )

                placeholders = ", ".join(
                    "?"
                    for _ in columns
                )

                sql = f"""
                    INSERT INTO "{table_name}" (
                        {column_sql}
                    )
                    VALUES (
                        {placeholders}
                    )
                """

                for row in rows:

                    values = [
                        row.get(column)
                        for column in columns
                    ]

                    connection.execute(
                        sql,
                        values,
                    )

            connection.execute(
                "COMMIT"
            )

        except Exception:

            connection.execute(
                "ROLLBACK"
            )

            raise

        finally:

            connection.execute(
                "PRAGMA foreign_keys = ON"
            )