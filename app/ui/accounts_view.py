from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.account_service import (
    create_account,
    get_current_balance,
    list_accounts,
)
from app.ui.manage_account_dialog import ManageAccountDialog
from app.ui.modal import Modal


class AccountsView(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            32,
            32,
            32,
            32,
        )
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

        add_button = QPushButton(
            "+ Add account"
        )
        add_button.setObjectName(
            "primary_button"
        )
        add_button.clicked.connect(
            self.open_add_account_modal
        )

        header_layout.addWidget(add_button)
        layout.addLayout(header_layout)

        self.accounts_layout = QVBoxLayout()
        self.accounts_layout.setSpacing(12)

        layout.addLayout(
            self.accounts_layout
        )
        layout.addStretch()

        self.refresh_accounts()

    def open_add_account_modal(self) -> None:
        modal = Modal(
            title="Add account",
            subtitle=(
                "Add a new account to track your money."
            ),
            primary_text="Add account",
        )

        form_layout = QFormLayout()
        form_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(18)

        # Account name
        name_label = QLabel(
            "Account name"
        )
        name_label.setObjectName(
            "field_label"
        )

        name_input = QLineEdit()
        name_input.setPlaceholderText(
            "e.g. Revolut"
        )
        name_input.setMinimumHeight(44)

        form_layout.addRow(
            name_label,
            name_input,
        )

        # Starting balance
        balance_label = QLabel(
            "Starting balance"
        )
        balance_label.setObjectName(
            "field_label"
        )

        balance_input = QLineEdit()
        balance_input.setPlaceholderText(
            "0.00 €"
        )
        balance_input.setMinimumHeight(44)

        balance_validator = (
            QRegularExpressionValidator(
                QRegularExpression(
                    r"^\d{0,10}([.,]\d{0,2})?$"
                )
            )
        )

        balance_input.setValidator(
            balance_validator
        )

        form_layout.addRow(
            balance_label,
            balance_input,
        )

        # Input styling
        modal.setStyleSheet(
            modal.styleSheet()
            + """
            QLabel#field_label {
                color: #334155;
                font-size: 13px;
                font-weight: 600;
            }

            QLineEdit {
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
            }

            QLineEdit:focus {
                background-color: #FFFFFF;
                border: 1px solid #64748B;
            }

            QLineEdit::placeholder {
                color: #94A3B8;
            }
            """
        )

        form_widget = QWidget()
        form_widget.setLayout(
            form_layout
        )

        modal.add_content(
            form_widget
        )

        def create_account_from_modal() -> None:
            name = (
                name_input.text()
                .strip()
            )

            balance_text = (
                balance_input.text()
                .strip()
                .replace(",", ".")
            )

            if not balance_text:
                balance_text = "0"

            try:
                balance_cents = round(
                    float(balance_text) * 100
                )
            except ValueError:
                balance_cents = 0

            if not name:
                name_input.setFocus()
                return

            try:
                create_account(
                    name,
                    balance_cents,
                )
            except Exception:
                return

            self.close_modal()
            self.refresh_accounts()

        modal.submitted.connect(
            create_account_from_modal
        )

        modal.cancelled.connect(
            self.close_modal
        )

        name_input.setFocus()

        self.window().show_modal(
            modal
        )

    def close_modal(self) -> None:
        self.window().close_modal()

    def open_manage_account_dialog(
        self,
        account_id: int,
        account_name: str,
        is_active: bool,
    ) -> None:
        modal_content = ManageAccountDialog(
            account_id=account_id,
            account_name=account_name,
            is_active=bool(is_active),
        )

        modal_content.finished.connect(
            self.refresh_accounts
        )

        self.window().show_modal(
            modal_content
        )

    def refresh_accounts(self) -> None:
        while self.accounts_layout.count():
            item = self.accounts_layout.takeAt(0)

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        accounts = list_accounts()

        if not accounts:
            empty_label = QLabel(
                "No accounts yet."
            )
            empty_label.setObjectName(
                "empty_state"
            )

            self.accounts_layout.addWidget(
                empty_label
            )
            return

        for account in accounts:
            card = QWidget()
            card.setObjectName(
                "account_card"
            )

            card_layout = QHBoxLayout(card)
            card_layout.setContentsMargins(
                20,
                16,
                20,
                16,
            )
            card_layout.setSpacing(12)

            name_label = QLabel(
                account["name"]
            )
            name_label.setObjectName(
                "account_name"
            )

            balance_cents = (
                get_current_balance(
                    account["id"]
                )
            )

            balance_label = QLabel(
                f"{balance_cents / 100:.2f} €"
            )
            balance_label.setObjectName(
                "account_balance"
            )

            manage_button = QPushButton(
                "Manage"
            )
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

            card_layout.addWidget(
                name_label
            )
            card_layout.addStretch()
            card_layout.addWidget(
                balance_label
            )
            card_layout.addWidget(
                manage_button
            )

            self.accounts_layout.addWidget(
                card
            )