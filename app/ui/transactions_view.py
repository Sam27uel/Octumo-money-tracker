from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services.transaction_service import (
    delete_transaction,
    list_transactions,
)

from app.ui.add_transaction_dialog import (
    AddTransactionDialog,
)

from app.ui.edit_transaction_dialog import (
    EditTransactionDialog,
)

from app.ui.modal import Modal


class TransactionsView(QWidget):
    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.build_ui()
        self.refresh_transactions()

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

        title = QLabel(
            "Transactions"
        )

        title.setObjectName(
            "page_title"
        )

        subtitle = QLabel(
            "View and manage your transactions."
        )

        subtitle.setObjectName(
            "page_subtitle"
        )

        title_container.addWidget(
            title
        )

        title_container.addWidget(
            subtitle
        )

        header_layout.addLayout(
            title_container
        )

        header_layout.addStretch()

        self.add_transaction_button = QPushButton(
            "+ Add transaction"
        )

        self.add_transaction_button.setObjectName(
            "primary_button"
        )

        self.add_transaction_button.setFixedHeight(
            42
        )

        self.add_transaction_button.setMinimumWidth(
            150
        )

        self.add_transaction_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.add_transaction_button.clicked.connect(
            self.open_add_transaction_dialog
        )

        header_layout.addWidget(
            self.add_transaction_button
        )

        layout.addLayout(
            header_layout
        )

        # -------------------------------------------------
        # Transactions
        # -------------------------------------------------

        layout.addSpacing(
            34
        )

        self.transactions_scroll = QScrollArea()

        self.transactions_scroll.setObjectName(
            "transactions_scroll"
        )

        self.transactions_scroll.setWidgetResizable(
            True
        )

        self.transactions_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.transactions_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.transactions_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.transactions_scroll.setWidget(
            self.create_transactions_container()
        )

        layout.addWidget(
            self.transactions_scroll,
            1,
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

            QPushButton#primary_button:pressed {
                background-color: #334155;
            }

            QScrollArea#transactions_scroll {
                background-color: transparent;
                border: none;
            }

            QWidget#transactions_scroll_content {
                background-color: transparent;
            }

            QWidget#transaction_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }

            QLabel#transaction_category {
                color: #0F172A;
                font-size: 15px;
                font-weight: 600;
            }

            QLabel#transaction_note {
                color: #64748B;
                font-size: 13px;
            }

            QLabel#transaction_account {
                color: #64748B;
                font-size: 12px;
            }

            QLabel#transaction_date {
                color: #64748B;
                font-size: 13px;
            }

            QLabel#transaction_amount_income {
                color: #15803D;
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#transaction_amount_expense {
                color: #B91C1C;
                font-size: 15px;
                font-weight: 700;
            }

            QPushButton#transaction_edit_button {
                background-color: #FFFFFF;
                color: #475569;

                border: 1px solid #CBD5E1;
                border-radius: 8px;

                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#transaction_edit_button:hover {
                background-color: #F8FAFC;
                color: #0F172A;
                border-color: #94A3B8;
            }

            QPushButton#transaction_delete_button {
                background-color: #FFFFFF;
                color: #B91C1C;

                border: 1px solid #FCA5A5;
                border-radius: 8px;

                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#transaction_delete_button:hover {
                background-color: #FEF2F2;
                border-color: #F87171;
            }

            QLabel#empty_state {
                color: #64748B;
                font-size: 15px;
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

    # =================================================
    # Transactions container
    # =================================================

    def create_transactions_container(self) -> QWidget:
        container = QWidget()

        container.setObjectName(
            "transactions_scroll_content"
        )

        self.transactions_container = QVBoxLayout(
            container
        )

        self.transactions_container.setContentsMargins(
            0,
            0,
            8,
            0,
        )

        self.transactions_container.setSpacing(
            12
        )

        self.transactions_container.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        return container

    # =================================================
    # Refresh
    # =================================================

    def refresh_transactions(self) -> None:
        self.clear_transactions()

        transactions = list_transactions()

        if not transactions:
            empty_label = QLabel(
                "No transactions yet. "
                "Add your first transaction to get started."
            )

            empty_label.setObjectName(
                "empty_state"
            )

            empty_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.transactions_container.addWidget(
                empty_label
            )

            return

        for transaction in transactions:
            self.add_transaction_card(
                transaction
            )

    def clear_transactions(self) -> None:
        while self.transactions_container.count():
            item = self.transactions_container.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    # =================================================
    # Transaction card
    # =================================================

    def add_transaction_card(
        self,
        transaction,
    ) -> None:
        transaction_id = transaction[
            "id"
        ]

        amount_cents = transaction[
            "amount_cents"
        ]

        amount = abs(
            amount_cents
        ) / 100

        is_income = amount_cents > 0

        card = QWidget()

        card.setObjectName(
            "transaction_card"
        )

        card_layout = QHBoxLayout(
            card
        )

        card_layout.setContentsMargins(
            22,
            16,
            18,
            16,
        )

        card_layout.setSpacing(
            18
        )

        # -------------------------------------------------
        # Information
        # -------------------------------------------------

        information_layout = QVBoxLayout()

        information_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        information_layout.setSpacing(
            3
        )

        category_name = (
            transaction["category_name"]
            or "Uncategorized"
        )

        category_label = QLabel(
            category_name
        )

        category_label.setObjectName(
            "transaction_category"
        )

        information_layout.addWidget(
            category_label
        )

        note = transaction[
            "note"
        ]

        if note:
            note_label = QLabel(
                note
            )

            note_label.setObjectName(
                "transaction_note"
            )

            information_layout.addWidget(
                note_label
            )

        account_label = QLabel(
            transaction["account_name"]
        )

        account_label.setObjectName(
            "transaction_account"
        )

        information_layout.addWidget(
            account_label
        )

        card_layout.addLayout(
            information_layout,
            1,
        )

        # -------------------------------------------------
        # Date
        # -------------------------------------------------

        date_label = QLabel(
            self.format_date(
                transaction[
                    "transaction_date"
                ]
            )
        )

        date_label.setObjectName(
            "transaction_date"
        )

        date_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        card_layout.addWidget(
            date_label
        )

        # -------------------------------------------------
        # Amount
        # -------------------------------------------------

        sign = (
            "+"
            if is_income
            else "-"
        )

        amount_label = QLabel(
            f"{sign}{self.format_amount(amount)}"
        )

        amount_label.setObjectName(
            "transaction_amount_income"
            if is_income
            else "transaction_amount_expense"
        )

        amount_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        card_layout.addWidget(
            amount_label
        )

        # -------------------------------------------------
        # Actions
        # -------------------------------------------------

        actions_layout = QHBoxLayout()

        actions_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        actions_layout.setSpacing(
            8
        )

        edit_button = QPushButton(
            "Edit"
        )

        edit_button.setObjectName(
            "transaction_edit_button"
        )

        edit_button.setFixedSize(
            62,
            36,
        )

        edit_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        edit_button.clicked.connect(
            lambda checked=False,
            transaction_id=transaction_id:
            self.open_edit_transaction(
                transaction_id
            )
        )

        delete_button = QPushButton(
            "Delete"
        )

        delete_button.setObjectName(
            "transaction_delete_button"
        )

        delete_button.setFixedSize(
            68,
            36,
        )

        delete_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        delete_button.clicked.connect(
            lambda checked=False,
            transaction_id=transaction_id,
            category_name=category_name,
            amount_label=amount_label:
            self.confirm_delete_transaction(
                transaction_id,
                category_name,
                amount_label.text(),
            )
        )

        actions_layout.addWidget(
            edit_button
        )

        actions_layout.addWidget(
            delete_button
        )

        card_layout.addLayout(
            actions_layout
        )

        self.transactions_container.addWidget(
            card
        )

    # =================================================
    # Add transaction
    # =================================================

    def open_add_transaction_dialog(self) -> None:
        dialog = AddTransactionDialog(
            parent=self.window()
        )

        dialog.finished.connect(
            self.on_transaction_dialog_finished
        )

        self.window().show_modal(
            dialog
        )

    # =================================================
    # Edit transaction
    # =================================================

    def open_edit_transaction(
        self,
        transaction_id: int,
    ) -> None:

        try:
            dialog = EditTransactionDialog(
                transaction_id=transaction_id,
                parent=self.window(),
            )

        except ValueError:
            return

        dialog.finished.connect(
            self.on_transaction_dialog_finished
        )

        self.window().show_modal(
            dialog
        )

    # =================================================
    # Delete confirmation
    # =================================================

    def confirm_delete_transaction(
        self,
        transaction_id: int,
        category_name: str,
        amount_text: str,
    ) -> None:

        modal = Modal(
            title="Delete transaction?",
            subtitle=(
                f"{category_name} · {amount_text}\n\n"
                "This transaction will be permanently deleted. "
                "This action cannot be undone."
            ),
            primary_text="Delete transaction",
            cancel_text="Cancel",
        )

        modal.primary_button.setObjectName(
            "danger_button"
        )

        modal.primary_button.setStyleSheet(
            """
            QPushButton#danger_button {
                background-color: #B91C1C;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#danger_button:hover {
                background-color: #991B1B;
            }

            QPushButton#danger_button:pressed {
                background-color: #7F1D1D;
            }
            """
        )

        modal.primary_button.setFixedHeight(
            42
        )

        modal.submitted.connect(
            lambda:
            self.delete_transaction(
                transaction_id
            )
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    # =================================================
    # Delete
    # =================================================

    def delete_transaction(
        self,
        transaction_id: int,
    ) -> None:

        try:
            delete_transaction(
                transaction_id
            )

        except Exception:
            self.close_nested_modal()
            return

        # Close confirmation modal.
        self.window().close_modal()

        self.refresh_transactions()

    # =================================================
    # Modal helpers
    # =================================================

    def on_transaction_dialog_finished(
        self,
    ) -> None:
        self.window().close_modal()
        self.refresh_transactions()

    def close_nested_modal(self) -> None:
        self.window().close_modal()

    # =================================================
    # Formatting
    # =================================================

    @staticmethod
    def format_amount(
        amount: float,
    ) -> str:
        return (
            f"{amount:,.2f} €"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", " ")
        )

    @staticmethod
    def format_date(
        date_value: str,
    ) -> str:
        try:
            year, month, day = (
                date_value.split("-")
            )

            return (
                f"{day}.{month}.{year}"
            )

        except ValueError:
            return date_value