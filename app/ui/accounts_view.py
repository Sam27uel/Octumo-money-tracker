from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class AccountsView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Accounts")
        title.setObjectName("page_title")

        subtitle = QLabel("Manage your bank accounts.")
        subtitle.setObjectName("page_subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()