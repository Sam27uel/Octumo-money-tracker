from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("BudgetFlow")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setSpacing(12)

        title = QLabel("BudgetFlow")
        title.setObjectName("title")

        subtitle = QLabel(
            "Your personal finance dashboard is being prepared."
        )
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        self.setCentralWidget(central_widget)

        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #F8FAFC;
            }

            QLabel#title {
                color: #0F172A;
                font-size: 32px;
                font-weight: 700;
            }

            QLabel#subtitle {
                color: #64748B;
                font-size: 16px;
            }
            """
        )