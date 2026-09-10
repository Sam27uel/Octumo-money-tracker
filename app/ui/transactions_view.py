from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt


class TransactionsView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)

        title = QLabel("Transactions")
        title.setObjectName("page_title")

        subtitle = QLabel("View and manage your transactions.")
        subtitle.setObjectName("page_subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()