from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QRegularExpressionValidator, QShowEvent
from PySide6.QtWidgets import (
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services.account_service import (
    create_account,
    delete_account_permanently,
    get_account,
    get_current_balance,
    list_accounts,
    restore_account,
)
from app.ui.manage_account_dialog import ManageAccountDialog
from app.ui.modal import Modal


class AccountsView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.build_ui()
        self.refresh_accounts()

    # =================================================
    # Refresh when Accounts view becomes visible
    # =================================================

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
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
        # Accounts scroll area
        # -------------------------------------------------

        layout.addSpacing(34)

        self.accounts_scroll = QScrollArea()

        self.accounts_scroll.setObjectName(
            "accounts_scroll"
        )

        self.accounts_scroll.setWidgetResizable(
            True
        )

        self.accounts_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.accounts_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.accounts_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.accounts_scroll.setWidget(
            self.create_accounts_container()
        )

        layout.addWidget(
            self.accounts_scroll,
            1,
        )

        # -------------------------------------------------
        # Bottom section
        # -------------------------------------------------

        layout.addSpacing(20)

        self.bottom_area = QWidget()

        self.bottom_area.setObjectName(
            "accounts_bottom_area"
        )

        bottom_layout = QHBoxLayout(
            self.bottom_area
        )

        bottom_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        bottom_layout.setSpacing(16)

        # -------------------------------------------------
        # Total balance
        # -------------------------------------------------

        self.total_balance_card = QWidget()

        self.total_balance_card.setObjectName(
            "total_balance_card"
        )

        total_balance_layout = QVBoxLayout(
            self.total_balance_card
        )

        total_balance_layout.setContentsMargins(
            20,
            14,
            20,
            14,
        )

        total_balance_layout.setSpacing(2)

        total_balance_title = QLabel(
            "Total balance"
        )

        total_balance_title.setObjectName(
            "total_balance_title"
        )

        self.total_balance_value = QLabel(
            "0,00 €"
        )

        self.total_balance_value.setObjectName(
            "total_balance_value"
        )

        total_balance_layout.addWidget(
            total_balance_title
        )

        total_balance_layout.addWidget(
            self.total_balance_value
        )

        bottom_layout.addWidget(
            self.total_balance_card,
            1,
        )

        # -------------------------------------------------
        # Archived accounts
        # -------------------------------------------------

        self.archived_button = QPushButton(
            "Archived accounts"
        )

        self.archived_button.setObjectName(
            "archived_button"
        )

        self.archived_button.setFixedHeight(
            52
        )

        self.archived_button.setMinimumWidth(
            170
        )

        self.archived_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.archived_button.clicked.connect(
            self.open_archived_accounts
        )

        bottom_layout.addWidget(
            self.archived_button
        )

        layout.addWidget(
            self.bottom_area
        )

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

            QScrollArea#accounts_scroll {
                background-color: transparent;
                border: none;
            }

            QWidget#accounts_scroll_content {
                background-color: transparent;
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

            QWidget#total_balance_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }

            QLabel#total_balance_title {
                color: #64748B;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#total_balance_value {
                color: #0F172A;
                font-size: 20px;
                font-weight: 700;
            }

            QPushButton#archived_button {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
                font-weight: 500;
            }

            QPushButton#archived_button:hover {
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #94A3B8;
            }

            QScrollBar:vertical {
                width: 8px;
                background: transparent;
                margin: 2px 0 2px 0;
            }

            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 4px;
                min-height: 32px;
            }

            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

    def create_accounts_container(self) -> QWidget:
        container = QWidget()

        container.setObjectName(
            "accounts_scroll_content"
        )

        self.accounts_container = QVBoxLayout(
            container
        )

        self.accounts_container.setContentsMargins(
            0,
            0,
            8,
            0,
        )

        self.accounts_container.setSpacing(
            12
        )

        self.accounts_container.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        return container

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

        else:
            for account in accounts:
                self.add_account_card(
                    account
                )

        self.refresh_total_balance()

    def refresh_total_balance(self) -> None:
        accounts = list_accounts()

        total_balance_cents = 0

        for account in accounts:
            total_balance_cents += get_current_balance(
                account["id"]
            )

        self.total_balance_value.setText(
            self.format_balance(
                total_balance_cents / 100
            )
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
    # Archived accounts
    # =================================================

    def open_archived_accounts(self) -> None:
        archived_accounts = list_accounts(
            include_archived=True
        )

        archived_accounts = [
            account
            for account in archived_accounts
            if not bool(account["is_active"])
        ]

        modal = Modal(
            title="Archived accounts",
            subtitle=(
                "Accounts you have archived are hidden "
                "from your active accounts."
            ),
            primary_text="Close",
            cancel_text="",
        )

        # -------------------------------------------------
        # Archived modal styling
        # -------------------------------------------------

        modal.setStyleSheet(
            modal.styleSheet()
            + """
                QWidget#archived_row {
                    background-color: #F8FAFC;
                    border: 1px solid #E2E8F0;
                    border-radius: 10px;
                }

                QLabel#archived_name {
                    color: #0F172A;
                    font-size: 14px;
                    font-weight: 600;
                }

                QLabel#archived_description {
                    color: #64748B;
                    font-size: 12px;
                }

                QPushButton#restore_button {
                    background-color: #FFFFFF;
                    color: #475569;
                    border: 1px solid #CBD5E1;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                    padding: 0 12px;
                }

                QPushButton#restore_button:hover {
                    background-color: #F8FAFC;
                    color: #0F172A;
                    border: 1px solid #94A3B8;
                }

                QPushButton#archived_delete_button {
                    background-color: #FFFFFF;
                    color: #B91C1C;
                    border: 1px solid #FCA5A5;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                    padding: 0 12px;
                }

                QPushButton#archived_delete_button:hover {
                    background-color: #FEF2F2;
                }

                QLabel#archived_empty {
                    color: #64748B;
                    font-size: 14px;
                }
            """
        )

        modal.cancel_button.hide()

        # -------------------------------------------------
        # No archived accounts
        # -------------------------------------------------

        if not archived_accounts:
            empty_label = QLabel(
                "There are no archived accounts."
            )

            empty_label.setObjectName(
                "archived_empty"
            )

            empty_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            modal.add_content(
                empty_label
            )

            modal.primary_button.clicked.connect(
                self.close_nested_modal
            )

            self.window().show_modal(
                modal
            )

            return

        # -------------------------------------------------
        # Archived accounts list
        # -------------------------------------------------

        for account in archived_accounts:
            row = self.create_archived_row(
                account
            )

            modal.add_content(
                row
            )

        modal.primary_button.clicked.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    def create_archived_row(
        self,
        account,
    ) -> QWidget:
        account_id = account["id"]
        account_name = account["name"]

        row = QWidget()

        row.setObjectName(
            "archived_row"
        )

        row_layout = QHBoxLayout(row)

        row_layout.setContentsMargins(
            14,
            12,
            14,
            12,
        )

        row_layout.setSpacing(
            10
        )

        # -------------------------------------------------
        # Account information
        # -------------------------------------------------

        text_layout = QVBoxLayout()

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text_layout.setSpacing(
            2
        )

        name_label = QLabel(
            account_name
        )

        name_label.setObjectName(
            "archived_name"
        )

        description_label = QLabel(
            "Archived account"
        )

        description_label.setObjectName(
            "archived_description"
        )

        text_layout.addWidget(
            name_label
        )

        text_layout.addWidget(
            description_label
        )

        row_layout.addLayout(
            text_layout,
            1,
        )

        # -------------------------------------------------
        # Restore
        # -------------------------------------------------

        restore_button = QPushButton(
            "Restore"
        )

        restore_button.setObjectName(
            "restore_button"
        )

        restore_button.setFixedSize(
            88,
            36,
        )

        restore_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        restore_button.clicked.connect(
            lambda checked=False,
            account_id=account_id:
            self.restore_archived_account(
                account_id
            )
        )

        row_layout.addWidget(
            restore_button
        )

        # -------------------------------------------------
        # Delete
        # -------------------------------------------------

        delete_button = QPushButton(
            "Delete"
        )

        delete_button.setObjectName(
            "archived_delete_button"
        )

        delete_button.setFixedSize(
            78,
            36,
        )

        delete_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        delete_button.clicked.connect(
            lambda checked=False,
            account_id=account_id,
            account_name=account_name:
            self.confirm_archived_delete(
                account_id,
                account_name,
            )
        )

        row_layout.addWidget(
            delete_button
        )

        return row

    def restore_archived_account(
        self,
        account_id: int,
    ) -> None:
        restore_account(
            account_id
        )

        self.window().close_modal()

        self.refresh_accounts()

    def confirm_archived_delete(
        self,
        account_id: int,
        account_name: str,
    ) -> None:
        modal = Modal(
            title="Delete archived account?",
            subtitle=(
                f"Are you sure you want to permanently "
                f"delete {account_name}?"
            ),
            primary_text="Continue",
        )

        modal.submitted.connect(
            lambda:
            self.show_archived_delete_confirmation(
                account_id,
                account_name,
            )
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    def show_archived_delete_confirmation(
        self,
        account_id: int,
        account_name: str,
    ) -> None:
        modal = Modal(
            title="Permanently delete account?",
            subtitle=(
                "This action cannot be undone. "
                "All transactions and balance adjustments "
                f"for {account_name} will be permanently deleted."
            ),
            primary_text="Delete account",
        )

        modal.primary_button.setObjectName(
            "danger_button"
        )

        modal.primary_button.setStyleSheet(
            """
            QPushButton {
                background-color: #B91C1C;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 16px;
                text-align: left;
            }

            QPushButton:hover {
                background-color: #991B1B;
            }
            """
        )

        modal.primary_button.setFixedSize(
            135,
            42,
        )

        modal.submitted.connect(
            lambda:
            self.delete_archived_account(
                account_id
            )
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    def delete_archived_account(
        self,
        account_id: int,
    ) -> None:
        delete_account_permanently(
            account_id
        )

        self.window().close_modal()
        self.window().close_modal()
        self.window().close_modal()

        self.refresh_accounts()

    def close_nested_modal(self) -> None:
        self.window().close_modal()

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