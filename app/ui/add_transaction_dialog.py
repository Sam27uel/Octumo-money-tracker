from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QDate, Qt, Signal
from PySide6.QtWidgets import (
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
from app.services.transaction_service import create_transaction


class AddTransactionDialog(QWidget):
    finished = Signal()

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.accounts = []
        self.categories = []

        self.build_ui()
        self.load_accounts()

    # =================================================
    # UI
    # =================================================

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
            "Add transaction"
        )

        title.setObjectName(
            "manage_title"
        )

        layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Record a new income or expense."
        )

        subtitle.setObjectName(
            "manage_subtitle"
        )

        subtitle.setWordWrap(
            True
        )

        layout.addSpacing(6)

        layout.addWidget(
            subtitle
        )

        # -------------------------------------------------
        # Transaction section
        # -------------------------------------------------

        layout.addSpacing(28)

        transaction_section = QLabel(
            "Transaction"
        )

        transaction_section.setObjectName(
            "section_title"
        )

        layout.addWidget(
            transaction_section
        )

        layout.addSpacing(12)

        # Type
        type_row = self.create_form_row(
            "Type",
            self.create_type_selector(),
        )

        layout.addWidget(
            type_row
        )

        layout.addSpacing(12)

        # Account
        self.account_input = QComboBox()

        self.account_input.setFixedHeight(
            42
        )

        account_row = self.create_form_row(
            "Account",
            self.account_input,
        )

        layout.addWidget(
            account_row
        )

        layout.addSpacing(12)

        # Category
        self.category_input = QComboBox()

        self.category_input.setFixedHeight(
            42
        )

        category_row = self.create_form_row(
            "Category",
            self.category_input,
        )

        layout.addWidget(
            category_row
        )

        # -------------------------------------------------
        # Separator
        # -------------------------------------------------

        layout.addSpacing(20)

        separator = self.create_separator()

        layout.addWidget(
            separator
        )

        # -------------------------------------------------
        # Details section
        # -------------------------------------------------

        layout.addSpacing(20)

        details_section = QLabel(
            "Details"
        )

        details_section.setObjectName(
            "section_title"
        )

        layout.addWidget(
            details_section
        )

        layout.addSpacing(12)

        # Amount
        self.amount_input = QLineEdit()

        self.amount_input.setPlaceholderText(
            "0,00 €"
        )

        self.amount_input.setFixedHeight(
            42
        )

        amount_row = self.create_form_row(
            "Amount",
            self.amount_input,
        )

        layout.addWidget(
            amount_row
        )

        layout.addSpacing(12)

        # Date
        self.date_input = QDateEdit()

        self.date_input.setFixedHeight(
            42
        )

        self.date_input.setCalendarPopup(
            True
        )

        self.date_input.setDate(
            QDate.currentDate()
        )

        self.date_input.setDisplayFormat(
            "dd.MM.yyyy"
        )

        date_row = self.create_form_row(
            "Date",
            self.date_input,
        )

        layout.addWidget(
            date_row
        )

        layout.addSpacing(12)

        # Note
        self.note_input = QLineEdit()

        self.note_input.setPlaceholderText(
            "Optional note"
        )

        self.note_input.setFixedHeight(
            42
        )

        note_row = self.create_form_row(
            "Note",
            self.note_input,
        )

        layout.addWidget(
            note_row
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

        layout.addSpacing(12)

        layout.addWidget(
            self.error_label
        )

        # -------------------------------------------------
        # Bottom
        # -------------------------------------------------

        layout.addSpacing(24)

        bottom_layout = QHBoxLayout()

        bottom_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        bottom_layout.setSpacing(
            10
        )

        bottom_layout.addStretch()

        cancel_button = QPushButton(
            "Cancel"
        )

        cancel_button.setObjectName(
            "secondary_button"
        )

        cancel_button.setFixedSize(
            100,
            42,
        )

        cancel_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        cancel_button.clicked.connect(
            self.close_dialog
        )

        bottom_layout.addWidget(
            cancel_button
        )

        add_button = QPushButton(
            "Add transaction"
        )

        add_button.setObjectName(
            "primary_button"
        )

        add_button.setFixedSize(
            145,
            42,
        )

        add_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        add_button.clicked.connect(
            self.save_transaction
        )

        bottom_layout.addWidget(
            add_button
        )

        layout.addLayout(
            bottom_layout
        )

        # -------------------------------------------------
        # Styling
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QLabel#manage_title {
                color: #0F172A;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#manage_subtitle {
                color: #64748B;
                font-size: 14px;
            }

            QLabel#section_title {
                color: #334155;
                font-size: 16px;
                font-weight: 700;
            }

            QLabel#form_label {
                color: #334155;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#error_label {
                color: #B91C1C;
                background-color: #FEF2F2;
                border: 1px solid #FECACA;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 13px;
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

            QComboBox {
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
            }

            QComboBox:focus {
                background-color: #FFFFFF;
                border: 1px solid #64748B;
            }

            QComboBox::drop-down {
                border: none;
                width: 32px;
            }

            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                selection-background-color: #F1F5F9;
                selection-color: #0F172A;
                padding: 4px;
            }

            QDateEdit {
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
            }

            QDateEdit:focus {
                background-color: #FFFFFF;
                border: 1px solid #64748B;
            }

            QDateEdit::drop-down {
                border: none;
                width: 32px;
            }

            QPushButton#secondary_button {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 16px;
            }

            QPushButton#secondary_button:hover {
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #94A3B8;
            }

            QPushButton#secondary_button:pressed {
                background-color: #F1F5F9;
            }

            QPushButton#primary_button {
                background-color: #0F172A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 16px;
            }

            QPushButton#primary_button:hover {
                background-color: #1E293B;
            }

            QPushButton#primary_button:pressed {
                background-color: #334155;
            }

            QFrame#separator {
                background-color: #E2E8F0;
            }
            """
        )

    # =================================================
    # Type selector
    # =================================================

    def create_type_selector(self) -> QWidget:
        container = QWidget()

        layout = QHBoxLayout(
            container
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            8
        )

        self.expense_button = QPushButton(
            "Expense"
        )

        self.expense_button.setCheckable(
            True
        )

        self.expense_button.setChecked(
            True
        )

        self.expense_button.setFixedHeight(
            42
        )

        self.expense_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.income_button = QPushButton(
            "Income"
        )

        self.income_button.setCheckable(
            True
        )

        self.income_button.setFixedHeight(
            42
        )

        self.income_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.expense_button.clicked.connect(
            self.select_expense
        )

        self.income_button.clicked.connect(
            self.select_income
        )

        layout.addWidget(
            self.expense_button
        )

        layout.addWidget(
            self.income_button
        )

        layout.addStretch()

        container.setStyleSheet(
            """
            QPushButton {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: 600;
                min-width: 95px;
            }

            QPushButton:hover {
                background-color: #F8FAFC;
                border-color: #94A3B8;
                color: #0F172A;
            }

            QPushButton:checked {
                background-color: #0F172A;
                color: #FFFFFF;
                border: 1px solid #0F172A;
            }

            QPushButton:checked:hover {
                background-color: #1E293B;
                border-color: #1E293B;
            }
            """
        )

        return container

    def select_expense(self) -> None:
        self.expense_button.setChecked(
            True
        )

        self.income_button.setChecked(
            False
        )

        self.refresh_categories()

    def select_income(self) -> None:
        self.income_button.setChecked(
            True
        )

        self.expense_button.setChecked(
            False
        )

        self.refresh_categories()

    # =================================================
    # Form helpers
    # =================================================

    def create_form_row(
        self,
        label_text: str,
        input_widget: QWidget,
    ) -> QWidget:
        row = QWidget()

        layout = QHBoxLayout(
            row
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            18
        )

        label = QLabel(
            label_text
        )

        label.setObjectName(
            "form_label"
        )

        label.setFixedWidth(
            90
        )

        label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(
            label
        )

        layout.addWidget(
            input_widget,
            1,
        )

        return row

    def create_separator(self) -> QFrame:
        separator = QFrame()

        separator.setObjectName(
            "separator"
        )

        separator.setFrameShape(
            QFrame.Shape.HLine
        )

        separator.setFixedHeight(
            1
        )

        return separator

    # =================================================
    # Data
    # =================================================

    def load_accounts(self) -> None:
        self.accounts = list_accounts()

        self.account_input.clear()

        for account in self.accounts:
            self.account_input.addItem(
                account["name"],
                account["id"],
            )

        if not self.accounts:
            self.show_error(
                "Create an account before adding a transaction."
            )

            return

        self.refresh_categories()

    def refresh_categories(self) -> None:
        kind = self.get_transaction_kind()

        self.categories = list_categories(
            kind=kind,
            include_archived=False,
        )

        self.category_input.clear()

        for category in self.categories:
            self.category_input.addItem(
                category["name"],
                category["id"],
            )

        if not self.categories:
            self.show_error(
                "Create a category for this transaction type first."
            )
        else:
            self.clear_error()

    def get_transaction_kind(self) -> str:
        if self.income_button.isChecked():
            return "income"

        return "expense"

    # =================================================
    # Save
    # =================================================

    def save_transaction(self) -> None:
        self.clear_error()

        if not self.accounts:
            self.show_error(
                "Create an account before adding a transaction."
            )

            return

        if not self.categories:
            self.show_error(
                "Create a category for this transaction type first."
            )

            return

        account_id = self.account_input.currentData()
        category_id = self.category_input.currentData()

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

        amount_cents = self.parse_amount()

        if amount_cents is None:
            self.show_error(
                "Enter a valid amount greater than 0."
            )

            self.amount_input.setFocus()

            return

        transaction_date = (
            self.date_input
            .date()
            .toString("yyyy-MM-dd")
        )

        try:
            create_transaction(
                account_id=account_id,
                category_id=category_id,
                amount_cents=amount_cents,
                transaction_date=transaction_date,
                note=self.note_input.text(),
                kind=self.get_transaction_kind(),
            )

        except ValueError as error:
            self.show_error(
                str(error)
            )

            return

        self.finished.emit()

    # =================================================
    # Amount
    # =================================================

    def parse_amount(self) -> int | None:
        raw_value = (
            self.amount_input
            .text()
            .strip()
        )

        if not raw_value:
            return None

        normalized = (
            raw_value
            .replace(" ", "")
            .replace(",", ".")
        )

        try:
            amount = Decimal(
                normalized
            )
        except InvalidOperation:
            return None

        if amount <= 0:
            return None

        if amount.as_tuple().exponent < -2:
            return None

        amount_cents = int(
            amount * Decimal("100")
        )

        if amount_cents <= 0:
            return None

        return amount_cents

    # =================================================
    # Error
    # =================================================

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

    # =================================================
    # Close
    # =================================================

    def close_dialog(self) -> None:
        self.finished.emit()