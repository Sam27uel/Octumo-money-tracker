import sys

from PySide6.QtWidgets import QApplication

from app.database.database import initialize_database
from app.ui.main_window import MainWindow


def main() -> None:
    initialize_database()

    app = QApplication(sys.argv)
    app.setApplicationName("Octumo")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()