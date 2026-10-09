from app.database.database import get_connection


DEFAULT_USER_NAME = "UserOctupus1"
DEFAULT_DATE_FORMAT = "DD.MM.YYYY"
DEFAULT_FIRST_DAY_OF_WEEK = "Monday"


def get_user_settings() -> dict:

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT
                name,
                date_format,
                first_day_of_week
            FROM user_settings
            WHERE id = 1
            """
        ).fetchone()

    if row is None:

        return {
            "name": DEFAULT_USER_NAME,
            "date_format": DEFAULT_DATE_FORMAT,
            "first_day_of_week": DEFAULT_FIRST_DAY_OF_WEEK,
        }

    return {
        "name": (
            row["name"]
            or DEFAULT_USER_NAME
        ),
        "date_format": (
            row["date_format"]
            or DEFAULT_DATE_FORMAT
        ),
        "first_day_of_week": (
            row["first_day_of_week"]
            or DEFAULT_FIRST_DAY_OF_WEEK
        ),
    }


def get_user_name() -> str:

    return get_user_settings()["name"]


def get_date_format() -> str:

    return get_user_settings()["date_format"]


def get_first_day_of_week() -> str:

    return get_user_settings()[
        "first_day_of_week"
    ]


def update_user_name(
    name: str,
) -> None:

    name = name.strip()

    if not name:

        raise ValueError(
            "Name cannot be empty."
        )

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO user_settings (
                id,
                name
            )
            VALUES (
                1,
                ?
            )
            ON CONFLICT(id)
            DO UPDATE SET
                name = excluded.name,
                updated_at = CURRENT_TIMESTAMP
            """,
            (name,),
        )


def update_date_format(
    date_format: str,
) -> None:

    allowed_formats = {
        "DD.MM.YYYY",
        "DD/MM/YYYY",
        "YYYY-MM-DD",
    }

    if date_format not in allowed_formats:

        raise ValueError(
            "Invalid date format."
        )

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO user_settings (
                id,
                date_format
            )
            VALUES (
                1,
                ?
            )
            ON CONFLICT(id)
            DO UPDATE SET
                date_format = excluded.date_format,
                updated_at = CURRENT_TIMESTAMP
            """,
            (date_format,),
        )


def update_first_day_of_week(
    first_day: str,
) -> None:

    allowed_days = {
        "Monday",
        "Sunday",
    }

    if first_day not in allowed_days:

        raise ValueError(
            "Invalid first day of week."
        )

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO user_settings (
                id,
                first_day_of_week
            )
            VALUES (
                1,
                ?
            )
            ON CONFLICT(id)
            DO UPDATE SET
                first_day_of_week = excluded.first_day_of_week,
                updated_at = CURRENT_TIMESTAMP
            """,
            (first_day,),
        )