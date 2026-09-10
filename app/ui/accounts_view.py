from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.account_service import create_account, list_accounts
from app.ui.add_account_dialog import AddAccountDialog


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
        add_button.clicked.connect(self.open_add_account_dialog)

        header_layout.addWidget(add_button)
        layout.addLayout(header_layout)

        self.accounts_layout = QVBoxLayout()
        self.accounts_layout.setSpacing(12)

        layout.addLayout(self.accounts_layout)
        layout.addStretch()

        self.refresh_accounts()

    def open_add_account_dialog(self) -> None:
        dialog = AddAccountDialog(self)

        if dialog.exec() == AddAccountDialog.DialogCode.Accepted:
            name, balance_cents = dialog.get_data()

            if not name:
                return

            try:
                create_account(name, balance_cents)

            except Exception as error:
                QMessageBox.warning(
                    self,
                    "Could not create account",
                    f"Could not create account:\n\n{error}",
                )
                return

            self.refresh_accounts()

    def refresh_accounts(self) -> None:
        # Remove existing account cards
        while self.accounts_layout.count():
            item = self.accounts_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        accounts = list_accounts()

        if not accounts:
            empty_label = QLabel("No accounts yet.")
            empty_label.setObjectName("empty_state")
            self.accounts_layout.addWidget(empty_label)
            return

        for account in accounts:
            card = QWidget()
            card.setObjectName("account_card")

            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(20, 16, 20, 16)

            name_label = QLabel(account["name"])
            name_label.setObjectName("account_name")

            balance_label = QLabel(
                f"{account['starting_balance_cents'] / 100:.2f} €"
            )
            balance_label.setObjectName("account_balance")

            card_layout.addWidget(name_label)
            card_layout.addStretch()
            card_layout.addWidget(balance_label)

            self.accounts_layout.addWidget(card)