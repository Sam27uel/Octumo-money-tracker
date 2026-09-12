from PySide6.QtCore import QRegularExpression, Qt
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
    get_account,
    get_current_balance,
    list_accounts,
)
from app.ui.manage_account_dialog import ManageAccountDialog
from app.ui.modal import Modal


class AccountsView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.build_ui()
        self.refresh_accounts()

    # =================================================
    # UI
    # =================================================

    def build_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            44,
            36,
            44,
            44,
        )

        layout.setSpacing(0)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        header_layout = QHBoxLayout()

        header_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        header_layout.setSpacing(20)

        title_container = QVBoxLayout()

        title_container.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        title_container.setSpacing(6)

        title = QLabel("Accounts")
        title.setObjectName("page_title")

        subtitle = QLabel(
            "Manage the accounts where you keep your money."
        )
        subtitle.setObjectName("page_subtitle")

        title_container.addWidget(title)
        title_container.addWidget(subtitle)

        header_layout.addLayout(
            title_container
        )

        header_layout.addStretch()

        self.add_account_button = QPushButton(
            "+ Add account"
        )

        self.add_account_button.setObjectName(
            "primary_button"
        )

        self.add_account_button.setFixedHeight(
            42
        )

        self.add_account_button.setMinimumWidth(
            130
        )

        self.add_account_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.add_account_button.clicked.connect(
            self.open_add_account_modal
        )

        header_layout.addWidget(
            self.add_account_button
        )

        layout.addLayout(
            header_layout
        )

        # -------------------------------------------------
        # Accounts
        # -------------------------------------------------

        layout.addSpacing(34)

        self.accounts_container = QVBoxLayout()

        self.accounts_container.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.accounts_container.setSpacing(
            12
        )

        layout.addLayout(
            self.accounts_container
        )

        layout.addStretch()

        # -------------------------------------------------
        # Styling
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QLabel#page_title {
                color: #0F172A;
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#page_subtitle {
                color: #64748B;
                font-size: 15px;
            }

            QPushButton#primary_button {
                background-color: #0F172A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#primary_button:hover {
                background-color: #1E293B;
            }

            QWidget#account_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }

            QLabel#account_name {
                color: #0F172A;
                font-size: 16px;
                font-weight: 600;
            }

            QLabel#account_balance {
                color: #0F172A;
                font-size: 16px;
                font-weight: 700;
            }

            QPushButton#manage_button {
                background-color: transparent;
                color: #475569;
                border: none;
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 14px;
                font-weight: 500;
            }

            QPushButton#manage_button:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }

            QLabel#empty_state {
                color: #64748B;
                font-size: 15px;
            }
            """
        )

    # =================================================
    # Accounts
    # =================================================

    def refresh_accounts(self) -> None:
        self.clear_accounts()

        accounts = list_accounts()

        if not accounts:
            empty_label = QLabel(
                "No accounts yet. Add your first account to get started."
            )

            empty_label.setObjectName(
                "empty_state"
            )

            empty_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.accounts_container.addWidget(
                empty_label
            )

            return

        for account in accounts:
            self.add_account_card(
                account
            )

    def clear_accounts(self) -> None:
        while self.accounts_container.count():
            item = self.accounts_container.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def add_account_card(self, account) -> None:
        account_id = account["id"]
        account_name = account["name"]

        balance_cents = get_current_balance(
            account_id
        )

        balance = balance_cents / 100

        # -------------------------------------------------
        # Card
        # -------------------------------------------------

        card = QWidget()

        card.setObjectName(
            "account_card"
        )

        card_layout = QHBoxLayout(card)

        card_layout.setContentsMargins(
            26,
            18,
            18,
            18,
        )

        card_layout.setSpacing(
            16
        )

        # -------------------------------------------------
        # Name
        # -------------------------------------------------

        name_label = QLabel(
            account_name
        )

        name_label.setObjectName(
            "account_name"
        )

        # -------------------------------------------------
        # Balance
        # -------------------------------------------------

        balance_label = QLabel(
            self.format_balance(
                balance
            )
        )

        balance_label.setObjectName(
            "account_balance"
        )

        balance_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        # -------------------------------------------------
        # Manage
        # -------------------------------------------------

        manage_button = QPushButton(
            "Manage"
        )

        manage_button.setObjectName(
            "manage_button"
        )

        manage_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        manage_button.clicked.connect(
            lambda checked=False,
            account_id=account_id:
            self.open_manage_account(
                account_id
            )
        )

        # -------------------------------------------------
        # Layout
        # -------------------------------------------------

        card_layout.addWidget(
            name_label
        )

        card_layout.addStretch()

        card_layout.addWidget(
            balance_label
        )

        card_layout.addSpacing(
            10
        )

        card_layout.addWidget(
            manage_button
        )

        self.accounts_container.addWidget(
            card
        )

    # =================================================
    # Add account modal
    # =================================================

    def open_add_account_modal(self) -> None:
        modal = Modal(
            title="Add account",
            subtitle=(
                "Add a new account to track your money."
            ),
            primary_text="Add account",
            cancel_text="Cancel",
        )

        # -------------------------------------------------
        # Form container
        #
        # Modal.add_content() expects QWidget,
        # therefore the layout must be placed inside
        # a QWidget first.
        # -------------------------------------------------

        form_widget = QWidget()

        form_layout = QFormLayout(
            form_widget
        )

        form_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        form_layout.setHorizontalSpacing(
            18
        )

        form_layout.setVerticalSpacing(
            18
        )

        # -------------------------------------------------
        # Account name
        # -------------------------------------------------

        name_label = QLabel(
            "Account name"
        )

        name_label.setObjectName(
            "field_label"
        )

        name_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        name_input = QLineEdit()

        name_input.setPlaceholderText(
            "e.g. Revolut"
        )

        name_input.setMinimumHeight(
            44
        )

        # -------------------------------------------------
        # Starting balance
        # -------------------------------------------------

        balance_label = QLabel(
            "Starting balance"
        )

        balance_label.setObjectName(
            "field_label"
        )

        balance_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        balance_input = QLineEdit()

        balance_input.setPlaceholderText(
            "0.00 €"
        )

        balance_input.setMinimumHeight(
            44
        )

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

        # -------------------------------------------------
        # Form rows
        # -------------------------------------------------

        form_layout.addRow(
            name_label,
            name_input,
        )

        form_layout.addRow(
            balance_label,
            balance_input,
        )

        modal.add_content(
            form_widget
        )

        # -------------------------------------------------
        # Submit
        # -------------------------------------------------

        def submit() -> None:
            name = name_input.text().strip()

            balance_text = (
                balance_input.text()
                .strip()
                .replace(",", ".")
            )

            if not name:
                return

            if not balance_text:
                balance_text = "0"

            try:
                balance_cents = round(
                    float(balance_text) * 100
                )
            except ValueError:
                return

            try:
                create_account(
                    name=name,
                    starting_balance_cents=balance_cents,
                )
            except ValueError:
                return

            self.window().close_modal()

            self.refresh_accounts()

        modal.submitted.connect(
            submit
        )

        # -------------------------------------------------
        # Cancel
        # -------------------------------------------------

        modal.cancelled.connect(
            self.window().close_modal
        )

        # -------------------------------------------------
        # Show
        # -------------------------------------------------

        self.window().show_modal(
            modal
        )

        name_input.setFocus()

    # =================================================
    # Manage account
    # =================================================

    def open_manage_account(
        self,
        account_id: int,
    ) -> None:

        account = get_account(
            account_id
        )

        if account is None:
            return

        manage = ManageAccountDialog(
            account_id=account["id"],
            account_name=account["name"],
            is_active=bool(
                account["is_active"]
            ),
        )

        manage.finished.connect(
            self.on_manage_finished
        )

        self.window().show_modal(
            manage
        )

    def on_manage_finished(self) -> None:
        self.window().close_modal()

        self.refresh_accounts()

    # =================================================
    # Helpers
    # =================================================

    @staticmethod
    def format_balance(
        balance: float,
    ) -> str:
        return (
            f"{balance:,.2f} €"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", " ")
        )