from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.account_service import (
    create_account,
    get_current_balance,
    list_accounts,
)
from app.ui.add_account_dialog import AddAccountDialog
from app.ui.manage_account_dialog import ManageAccountDialog


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
        add_button.clicked.connect(
            self.open_add_account_modal
        )

        header_layout.addWidget(add_button)
        layout.addLayout(header_layout)

        self.accounts_layout = QVBoxLayout()
        self.accounts_layout.setSpacing(12)

        layout.addLayout(self.accounts_layout)
        layout.addStretch()

        self.refresh_accounts()

    def open_add_account_modal(self) -> None:
        modal_content = AddAccountDialog()

        modal_content.submitted.connect(
            lambda: self.create_account_from_modal(
                modal_content
            )
        )

        modal_content.cancelled.connect(
            self.close_modal
        )

        self.window().show_modal(modal_content)

    def create_account_from_modal(
        self,
        modal_content: AddAccountDialog,
    ) -> None:
        name, balance_cents = modal_content.get_data()

        if not name:
            QMessageBox.warning(
                self,
                "Invalid account",
                "Account name cannot be empty.",
            )
            return

        try:
            create_account(
                name,
                balance_cents,
            )

        except Exception as error:
            QMessageBox.warning(
                self,
                "Could not create account",
                f"Could not create account:\n\n{error}",
            )
            return

        self.close_modal()
        self.refresh_accounts()

    def close_modal(self) -> None:
        self.window().close_modal()

    def open_manage_account_dialog(
        self,
        account_id: int,
        account_name: str,
        is_active: bool,
    ) -> None:
        dialog = ManageAccountDialog(
            account_id=account_id,
            account_name=account_name,
            is_active=bool(is_active),
            parent=self,
        )

        dialog.exec()

        self.refresh_accounts()

    def refresh_accounts(self) -> None:
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
            card_layout.setContentsMargins(
                20,
                16,
                20,
                16,
            )
            card_layout.setSpacing(12)

            name_label = QLabel(account["name"])
            name_label.setObjectName("account_name")

            balance_cents = get_current_balance(
                account["id"]
            )

            balance_label = QLabel(
                f"{balance_cents / 100:.2f} €"
            )
            balance_label.setObjectName(
                "account_balance"
            )

            manage_button = QPushButton("Manage")
            manage_button.setObjectName(
                "secondary_button"
            )

            manage_button.clicked.connect(
                lambda checked=False,
                account_id=account["id"],
                account_name=account["name"],
                is_active=account["is_active"]:
                self.open_manage_account_dialog(
                    account_id,
                    account_name,
                    is_active,
                )
            )

            card_layout.addWidget(name_label)
            card_layout.addStretch()
            card_layout.addWidget(balance_label)
            card_layout.addWidget(manage_button)

            self.accounts_layout.addWidget(card)