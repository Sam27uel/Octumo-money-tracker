from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class AccountsView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Accounts")
        title.setObjectName("page_title")

        subtitle = QLabel(
            "Manage the accounts where you keep your money."
        )
        subtitle.setObjectName("page_subtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        header_layout = QHBoxLayout()

        header_layout.addStretch()

        add_button = QPushButton("+ Add account")
        add_button.setObjectName("primary_button")

        header_layout.addWidget(add_button)

        layout.addLayout(header_layout)

        accounts_label = QLabel("No accounts yet.")
        accounts_label.setObjectName("empty_state")

        layout.addWidget(accounts_label)
        layout.addStretch()