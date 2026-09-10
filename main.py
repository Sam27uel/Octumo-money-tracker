from app.database.database import DATABASE_PATH, initialize_database


def main() -> None:
    initialize_database()
    print(f"BudgetFlow database is ready: {DATABASE_PATH}")


if __name__ == "__main__":
    main()