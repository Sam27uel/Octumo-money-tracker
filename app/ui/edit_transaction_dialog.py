from decimal import Decimal, InvalidOperation

from PySide6.QtCore import (
    QEasingCurve,
    QDate,
    QPropertyAnimation,
    QRect,
    Signal,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.account_service import list_accounts
from app.services.category_service import list_categories
from app.services.transaction_service import (
    get_transaction,
    update_transaction,
)


class TransactionTypeSelector(QWidget):
    """
    Animated Income / Expense selector.

    The dark indicator moves between the two buttons.
    """

    type_changed = Signal(str)

    def __init__(
        self,
        selected_kind: str = "income",
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.selected_kind = (
            selected_kind
            if selected_kind in {"income", "expense"}
            else "income"
        )

        self._animation = None

        self.setObjectName(
            "transaction_type_selector"
        )

        self.setFixedHeight(42)

        # -------------------------------------------------
        # Indicator
        # -------------------------------------------------

        self.indicator = QFrame(self)

        self.indicator.setObjectName(
            "transaction_type_indicator"
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        self.income_button = QPushButton(
            "Income",
            self,
        )

        self.expense_button = QPushButton(
            "Expense",
            self,
        )

        self.income_button.setObjectName(
            "transaction_type_button"
        )

        self.expense_button.setObjectName(
            "transaction_type_button"
        )

        self.income_button.setCheckable(True)
        self.expense_button.setCheckable(True)

        # -------------------------------------------------
        # Button group
        # -------------------------------------------------

        self.type_group = QButtonGroup(
            self
        )

        self.type_group.setExclusive(
            True
        )

        self.type_group.addButton(
            self.income_button
        )

        self.type_group.addButton(
            self.expense_button
        )

        # -------------------------------------------------
        # Connections
        # -------------------------------------------------

        self.income_button.clicked.connect(
            lambda: self.set_transaction_type(
                "income"
            )
        )

        self.expense_button.clicked.connect(
            lambda: self.set_transaction_type(
                "expense"
            )
        )

        # -------------------------------------------------
        # Initial state
        # -------------------------------------------------

        self.income_button.setChecked(
            self.selected_kind == "income"
        )

        self.expense_button.setChecked(
            self.selected_kind == "expense"
        )

        # -------------------------------------------------
        # Styling
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QWidget#transaction_type_selector {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
            }

            QFrame#transaction_type_indicator {
                background-color: #0F172A;
                border-radius: 7px;
            }

            QPushButton#transaction_type_button {
                background-color: transparent;
                color: #64748B;
                border: none;
                border-radius: 7px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#transaction_type_button:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }

            QPushButton#transaction_type_button:checked {
                background-color: transparent;
                color: #FFFFFF;
            }

            QPushButton#transaction_type_button:checked:hover {
                background-color: transparent;
                color: #FFFFFF;
            }
            """
        )

        self.indicator.lower()

    # =====================================================
    # Layout
    # =====================================================

    def showEvent(self, event) -> None:
        super().showEvent(event)

        self.update_layout(
            animated=False
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

        self.update_layout(
            animated=False
        )

    def update_layout(
        self,
        animated: bool = True,
    ) -> None:
        margin = 1

        available_width = (
            self.width() - 2 * margin
        )

        half_width = available_width / 2

        indicator_width = int(
            half_width
        )

        if self.selected_kind == "income":
            target_x = margin
        else:
            target_x = (
                margin
                + indicator_width
            )

        target_rect = QRect(
            int(target_x),
            margin,
            indicator_width,
            self.height() - 2 * margin,
        )

        button_height = (
            self.height()
            - 2 * margin
        )

        income_rect = QRect(
            margin,
            margin,
            indicator_width,
            button_height,
        )

        expense_rect = QRect(
            margin + indicator_width,
            margin,
            indicator_width,
            button_height,
        )

        self.income_button.setGeometry(
            income_rect
        )

        self.expense_button.setGeometry(
            expense_rect
        )

        if not animated:
            self.indicator.setGeometry(
                target_rect
            )
            return

        animation = QPropertyAnimation(
            self.indicator,
            b"geometry",
            self,
        )

        animation.setDuration(180)

        animation.setStartValue(
            self.indicator.geometry()
        )

        animation.setEndValue(
            target_rect
        )

        animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self._animation = animation

        animation.start()

    # =====================================================
    # Change type
    # =====================================================

    def set_transaction_type(
        self,
        kind: str,
    ) -> None:
        if kind not in {
            "income",
            "expense",
        }:
            return

        if kind == self.selected_kind:
            return

        self.selected_kind = kind

        self.income_button.setChecked(
            kind == "income"
        )

        self.expense_button.setChecked(
            kind == "expense"
        )

        self.update_layout(
            animated=True
        )

        self.type_changed.emit(
            kind
        )


class EditTransactionDialog(QWidget):
    finished = Signal()

    def __init__(
        self,
        transaction_id: int,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.transaction_id = (
            transaction_id
        )

        self.transaction = None

        self.accounts = []
        self.categories = []

        self.setObjectName(
            "edit_transaction_dialog"
        )

        self.build_ui()
        self.load_transaction()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(0)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        title = QLabel(
            "Edit transaction"
        )

        title.setObjectName(
            "dialog_title"
        )

        subtitle = QLabel(
            "Update the details of this transaction."
        )

        subtitle.setObjectName(
            "dialog_subtitle"
        )

        layout.addWidget(title)

        layout.addSpacing(5)

        layout.addWidget(subtitle)

        # -------------------------------------------------
        # Transaction
        # -------------------------------------------------

        layout.addSpacing(26)

        transaction_title = QLabel(
            "Transaction"
        )

        transaction_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            transaction_title
        )

        layout.addSpacing(16)

        # Type

        type_label = QLabel(
            "Type"
        )

        type_label.setObjectName(
            "field_label"
        )

        layout.addWidget(
            type_label
        )

        layout.addSpacing(7)

        self.type_input = (
            TransactionTypeSelector()
        )

        layout.addWidget(
            self.type_input
        )

        self.type_input.type_changed.connect(
            self.on_type_changed
        )

        # -------------------------------------------------
        # Amount + Date
        # -------------------------------------------------

        layout.addSpacing(18)

        amount_date = QHBoxLayout()

        amount_date.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        amount_date.setSpacing(20)

        # Amount

        amount_box = QWidget()

        amount_layout = QVBoxLayout(
            amount_box
        )

        amount_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        amount_layout.setSpacing(7)

        amount_label = QLabel(
            "Amount"
        )

        amount_label.setObjectName(
            "field_label"
        )

        self.amount_input = QLineEdit()

        self.amount_input.setFixedHeight(
            42
        )

        self.amount_input.setPlaceholderText(
            "0.00"
        )

        amount_layout.addWidget(
            amount_label
        )

        amount_layout.addWidget(
            self.amount_input
        )

        # Date

        date_box = QWidget()

        date_layout = QVBoxLayout(
            date_box
        )

        date_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        date_layout.setSpacing(7)

        date_label = QLabel(
            "Date"
        )

        date_label.setObjectName(
            "field_label"
        )

        self.date_input = QDateEdit()

        self.date_input.setFixedHeight(
            42
        )

        self.date_input.setCalendarPopup(
            True
        )

        self.date_input.setDisplayFormat(
            "dd.MM.yyyy"
        )

        date_layout.addWidget(
            date_label
        )

        date_layout.addWidget(
            self.date_input
        )

        amount_date.addWidget(
            amount_box,
            1,
        )

        amount_date.addWidget(
            date_box,
            1,
        )

        layout.addLayout(
            amount_date
        )

        # -------------------------------------------------
        # Account + Category
        # -------------------------------------------------

        layout.addSpacing(16)

        account_category = QHBoxLayout()

        account_category.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        account_category.setSpacing(20)

        # Account

        account_box = QWidget()

        account_layout = QVBoxLayout(
            account_box
        )

        account_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        account_layout.setSpacing(7)

        account_label = QLabel(
            "Account"
        )

        account_label.setObjectName(
            "field_label"
        )

        self.account_input = QComboBox()

        self.account_input.setObjectName(
            "form_combo"
        )

        self.account_input.setFixedHeight(
            42
        )

        account_layout.addWidget(
            account_label
        )

        account_layout.addWidget(
            self.account_input
        )

        # Category

        category_box = QWidget()

        category_layout = QVBoxLayout(
            category_box
        )

        category_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        category_layout.setSpacing(7)

        category_label = QLabel(
            "Category"
        )

        category_label.setObjectName(
            "field_label"
        )

        self.category_input = QComboBox()

        self.category_input.setObjectName(
            "form_combo"
        )

        self.category_input.setFixedHeight(
            42
        )

        category_layout.addWidget(
            category_label
        )

        category_layout.addWidget(
            self.category_input
        )

        account_category.addWidget(
            account_box,
            1,
        )

        account_category.addWidget(
            category_box,
            1,
        )

        layout.addLayout(
            account_category
        )

        # -------------------------------------------------
        # Separator
        # -------------------------------------------------

        layout.addSpacing(24)

        separator = QFrame()

        separator.setObjectName(
            "section_separator"
        )

        separator.setFixedHeight(
            1
        )

        layout.addWidget(
            separator
        )

        # -------------------------------------------------
        # Details
        # -------------------------------------------------

        layout.addSpacing(22)

        details_title = QLabel(
            "Details"
        )

        details_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            details_title
        )

        layout.addSpacing(16)

        note_label = QLabel(
            "Note"
        )

        note_label.setObjectName(
            "field_label"
        )

        self.note_input = QLineEdit()

        self.note_input.setFixedHeight(
            42
        )

        self.note_input.setPlaceholderText(
            "Optional note"
        )

        layout.addWidget(
            note_label
        )

        layout.addSpacing(7)

        layout.addWidget(
            self.note_input
        )

        # -------------------------------------------------
        # Error
        # -------------------------------------------------

        self.error_label = QLabel()

        self.error_label.setObjectName(
            "error_label"
        )

        self.error_label.setWordWrap(
            True
        )

        self.error_label.hide()

        layout.addSpacing(8)

        layout.addWidget(
            self.error_label
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        layout.addSpacing(20)

        buttons = QHBoxLayout()

        buttons.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        buttons.setSpacing(10)

        buttons.addStretch()

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.cancel_button.setObjectName(
            "cancel_button"
        )

        self.cancel_button.setFixedHeight(
            42
        )

        self.save_button = QPushButton(
            "Save changes"
        )

        self.save_button.setObjectName(
            "save_button"
        )

        self.save_button.setFixedHeight(
            42
        )

        buttons.addWidget(
            self.cancel_button
        )

        buttons.addWidget(
            self.save_button
        )

        layout.addLayout(
            buttons
        )

        # -------------------------------------------------
        # Connections
        # -------------------------------------------------

        self.cancel_button.clicked.connect(
            self.close_dialog
        )

        self.save_button.clicked.connect(
            self.save_transaction
        )

        self.amount_input.returnPressed.connect(
            self.save_transaction
        )

        self.note_input.returnPressed.connect(
            self.save_transaction
        )

        # -------------------------------------------------
        # Style
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QWidget#edit_transaction_dialog {
                background-color: #FFFFFF;
            }

            QLabel#dialog_title {
                color: #0F172A;
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#dialog_subtitle {
                color: #64748B;
                font-size: 15px;
            }

            QLabel#section_title {
                color: #0F172A;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#field_label {
                color: #334155;
                font-size: 15px;
                font-weight: 600;
            }

            QLineEdit,
            QDateEdit,
            QComboBox {
                background-color: #FFFFFF;
                color: #0F172A;

                border: 1px solid #CBD5E1;
                border-radius: 8px;

                padding-left: 12px;
                padding-right: 12px;

                font-size: 14px;
            }

            QLineEdit:focus,
            QDateEdit:focus,
            QComboBox:focus {
                border: 1px solid #94A3B8;
            }

            QLineEdit::placeholder {
                color: #94A3B8;
            }

            QComboBox#form_combo {
                padding-right: 8px;
            }

            QComboBox#form_combo::drop-down {
                width: 28px;
                border: none;
                background: transparent;
            }

            QComboBox#form_combo QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;

                border: none;

                outline: none;

                padding: 6px;

                selection-background-color: #E2E8F0;
                selection-color: #0F172A;
            }

            QDateEdit::drop-down {
                width: 28px;
                border: none;
                background: transparent;
            }

            QFrame#section_separator {
                background-color: #E2E8F0;
                border: none;
            }

            QLabel#error_label {
                color: #B91C1C;
                font-size: 13px;
            }

            QPushButton#cancel_button {
                background-color: #FFFFFF;
                color: #334155;

                border: 1px solid #CBD5E1;
                border-radius: 8px;

                padding: 0 16px;

                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#cancel_button:hover {
                background-color: #F8FAFC;
                border-color: #94A3B8;
            }

            QPushButton#save_button {
                background-color: #0F172A;
                color: #FFFFFF;

                border: none;
                border-radius: 8px;

                padding: 0 18px;

                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#save_button:hover {
                background-color: #1E293B;
            }

            QPushButton#save_button:pressed {
                background-color: #334155;
            }
            """
        )

    # =====================================================
    # Load
    # =====================================================

    def load_transaction(self) -> None:
        transaction = get_transaction(
            self.transaction_id
        )

        if transaction is None:
            self.show_error(
                "Transaction not found."
            )
            return

        self.transaction = transaction

        kind = (
            "income"
            if transaction["amount_cents"] > 0
            else "expense"
        )

        self.type_input.selected_kind = kind

        self.type_input.income_button.setChecked(
            kind == "income"
        )

        self.type_input.expense_button.setChecked(
            kind == "expense"
        )

        self.type_input.update_layout(
            animated=False
        )

        # Amount

        amount = (
            abs(
                transaction[
                    "amount_cents"
                ]
            )
            / 100
        )

        self.amount_input.setText(
            f"{amount:.2f}"
        )

        # Date

        date = QDate.fromString(
            transaction[
                "transaction_date"
            ],
            "yyyy-MM-dd",
        )

        if date.isValid():
            self.date_input.setDate(
                date
            )
        else:
            self.date_input.setDate(
                QDate.currentDate()
            )

        # Account

        self.load_accounts(
            transaction[
                "account_id"
            ]
        )

        # Category

        self.load_categories(
            transaction[
                "category_id"
            ]
        )

        # Note

        self.note_input.setText(
            transaction["note"] or ""
        )

    # =====================================================
    # Accounts
    # =====================================================

    def load_accounts(
        self,
        selected_id=None,
    ) -> None:
        self.accounts = list_accounts()

        self.account_input.clear()

        selected_index = -1

        for index, account in enumerate(
            self.accounts
        ):
            self.account_input.addItem(
                account["name"],
                account["id"],
            )

            if account["id"] == selected_id:
                selected_index = index

        if selected_index >= 0:
            self.account_input.setCurrentIndex(
                selected_index
            )

    # =====================================================
    # Categories
    # =====================================================

    def load_categories(
        self,
        selected_id=None,
    ) -> None:
        kind = (
            self.type_input.selected_kind
        )

        self.categories = list_categories(
            kind=kind,
            include_archived=True,
        )

        self.category_input.clear()

        selected_index = -1

        for index, category in enumerate(
            self.categories
        ):
            self.category_input.addItem(
                category["name"],
                category["id"],
            )

            if category["id"] == selected_id:
                selected_index = index

        if selected_index >= 0:
            self.category_input.setCurrentIndex(
                selected_index
            )

    # =====================================================
    # Type
    # =====================================================

    def on_type_changed(
        self,
        kind: str,
    ) -> None:
        self.load_categories()

    # =====================================================
    # Amount
    # =====================================================

    def parse_amount(self):
        value = (
            self.amount_input
            .text()
            .strip()
        )

        if not value:
            return None

        value = (
            value
            .replace("€", "")
            .replace(" ", "")
            .replace(",", ".")
        )

        try:
            amount = Decimal(
                value
            )
        except InvalidOperation:
            return None

        if amount <= 0:
            return None

        cents = int(
            amount * 100
        )

        return cents if cents > 0 else None

    # =====================================================
    # Save
    # =====================================================

    def save_transaction(self) -> None:
        self.clear_error()

        if self.transaction is None:
            self.show_error(
                "Transaction could not be loaded."
            )
            return

        account_id = (
            self.account_input.currentData()
        )

        category_id = (
            self.category_input.currentData()
        )

        if account_id is None:
            self.show_error(
                "Please select an account."
            )
            return

        if category_id is None:
            self.show_error(
                "Please select a category."
            )
            return

        amount_cents = (
            self.parse_amount()
        )

        if amount_cents is None:
            self.show_error(
                "Enter a valid amount greater than 0."
            )
            self.amount_input.setFocus()
            return

        transaction_date = (
            self.date_input
            .date()
            .toString(
                "yyyy-MM-dd"
            )
        )

        note = (
            self.note_input
            .text()
            .strip()
        )

        try:
            update_transaction(
                transaction_id=(
                    self.transaction_id
                ),
                account_id=account_id,
                category_id=category_id,
                amount_cents=amount_cents,
                transaction_date=(
                    transaction_date
                ),
                note=note,
                kind=(
                    self.type_input
                    .selected_kind
                ),
            )

        except ValueError as error:
            self.show_error(
                str(error)
            )
            return

        except Exception as error:
            self.show_error(
                f"Could not save transaction: {error}"
            )
            return

        self.finished.emit()

    # =====================================================
    # Error
    # =====================================================

    def show_error(
        self,
        message: str,
    ) -> None:
        self.error_label.setText(
            message
        )

        self.error_label.show()

    def clear_error(self) -> None:
        self.error_label.clear()
        self.error_label.hide()

    # =====================================================
    # Close
    # =====================================================

    def close_dialog(self) -> None:
        self.finished.emit()