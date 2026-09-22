from decimal import Decimal, InvalidOperation

from PySide6.QtCore import (
    QDate,
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    Qt,
    Signal,
)
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListView,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.account_service import list_accounts
from app.services.category_service import list_categories
from app.services.transaction_service import create_transaction


# =========================================================
# Modern combo box
# =========================================================


class ModernComboBox(QComboBox):
    """
    Octumo-style combo box with a clean popup.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setObjectName(
            "modern_combo_box"
        )

        self.setFixedHeight(42)

        # -------------------------------------------------
        # Popup view
        # -------------------------------------------------

        view = QListView()

        view.setObjectName(
            "modern_combo_popup"
        )

        view.setFrameShape(
            QFrame.Shape.NoFrame
        )

        view.setFrameShadow(
            QFrame.Shadow.Plain
        )

        view.setSpacing(2)
        view.setUniformItemSizes(True)

        view.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        view.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        view.setSelectionMode(
            QListView.SelectionMode.SingleSelection
        )

        view.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        # -------------------------------------------------
        # Popup window
        # -------------------------------------------------

        view.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
        )

        # Important on macOS:
        # translucent popup can render black.
        view.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            False,
        )

        view.setAutoFillBackground(
            True
        )

        # -------------------------------------------------
        # Popup palette
        # -------------------------------------------------

        palette = view.palette()

        palette.setColor(
            QPalette.ColorRole.Window,
            Qt.GlobalColor.white,
        )

        palette.setColor(
            QPalette.ColorRole.Base,
            Qt.GlobalColor.white,
        )

        palette.setColor(
            QPalette.ColorRole.Text,
            Qt.GlobalColor.black,
        )

        view.setPalette(
            palette
        )

        self.setView(view)

        # -------------------------------------------------
        # Styling
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QComboBox#modern_combo_box {
                background-color: #FFFFFF;
                color: #0F172A;

                border: 1px solid #CBD5E1;
                border-radius: 9px;

                padding-left: 12px;
                padding-right: 34px;

                font-size: 14px;
            }

            QComboBox#modern_combo_box:hover {
                border-color: #94A3B8;
            }

            QComboBox#modern_combo_box:focus {
                border-color: #64748B;
                background-color: #FFFFFF;
            }

            QComboBox#modern_combo_box::drop-down {
                width: 32px;
                border: none;
                background: transparent;
            }

            QListView#modern_combo_popup {
                background-color: #FFFFFF;
                color: #0F172A;

                border: 1px solid #E2E8F0;
                border-radius: 12px;

                padding: 6px;
                outline: none;
            }

            QListView#modern_combo_popup::item {
                background-color: transparent;
                color: #0F172A;

                min-height: 36px;

                padding-left: 10px;
                padding-right: 10px;

                border-radius: 8px;
            }

            QListView#modern_combo_popup::item:hover {
                background-color: #F8FAFC;
                color: #0F172A;
            }

            QListView#modern_combo_popup::item:selected {
                background-color: #F1F5F9;
                color: #0F172A;
            }

            QListView#modern_combo_popup::item:selected:hover {
                background-color: #E2E8F0;
                color: #0F172A;
            }

            QListView#modern_combo_popup QScrollBar:vertical {
                background: transparent;

                width: 6px;

                margin-top: 7px;
                margin-bottom: 7px;
                margin-right: 3px;

                border: none;
            }

            QListView#modern_combo_popup QScrollBar::handle:vertical {
                background: #CBD5E1;

                border-radius: 3px;

                min-height: 28px;
            }

            QListView#modern_combo_popup QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }

            QListView#modern_combo_popup QScrollBar::add-line:vertical,
            QListView#modern_combo_popup QScrollBar::sub-line:vertical {
                height: 0px;
                border: none;
                background: transparent;
            }

            QListView#modern_combo_popup QScrollBar::add-page:vertical,
            QListView#modern_combo_popup QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )


# =========================================================
# Transaction type selector
# =========================================================


class TransactionTypeSelector(QWidget):
    """
    Animated Income / Expense selector.

    Income  -> left
    Expense -> right
    """

    type_changed = Signal(str)

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.selected_kind = "income"
        self._animation = None

        self.setObjectName(
            "transaction_type_selector"
        )

        self.setFixedHeight(44)

        # -------------------------------------------------
        # Indicator
        # -------------------------------------------------

        self.indicator = QFrame(
            self
        )

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

        self.income_button.setCheckable(
            True
        )

        self.expense_button.setCheckable(
            True
        )

        # -------------------------------------------------
        # Group
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

        self.income_button.setChecked(
            True
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
        # Styling
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QWidget#transaction_type_selector {
                background-color: #F8FAFC;

                border: 1px solid #CBD5E1;
                border-radius: 9px;
            }

            QFrame#transaction_type_indicator {
                background-color: #0F172A;
                border-radius: 8px;
            }

            QPushButton#transaction_type_button {
                background-color: transparent;
                color: #64748B;

                border: none;
                border-radius: 8px;

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

        self.income_button.raise_()
        self.expense_button.raise_()

    # -----------------------------------------------------
    # Layout
    # -----------------------------------------------------

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
            self.width()
            - (2 * margin)
        )

        button_width = (
            available_width // 2
        )

        button_height = (
            self.height()
            - (2 * margin)
        )

        if self.selected_kind == "income":
            target_x = margin
        else:
            target_x = (
                margin
                + button_width
            )

        indicator_rect = QRect(
            target_x,
            margin,
            button_width,
            button_height,
        )

        income_rect = QRect(
            margin,
            margin,
            button_width,
            button_height,
        )

        expense_rect = QRect(
            margin + button_width,
            margin,
            available_width - button_width,
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
                indicator_rect
            )
            return

        animation = QPropertyAnimation(
            self.indicator,
            b"geometry",
            self,
        )

        animation.setDuration(
            180
        )

        animation.setStartValue(
            self.indicator.geometry()
        )

        animation.setEndValue(
            indicator_rect
        )

        animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self._animation = animation

        animation.start()

    # -----------------------------------------------------
    # Change type
    # -----------------------------------------------------

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
            self.income_button.setChecked(
                kind == "income"
            )

            self.expense_button.setChecked(
                kind == "expense"
            )

            self.update_layout(
                animated=False
            )

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


# =========================================================
# Add transaction dialog
# =========================================================


class AddTransactionDialog(QWidget):
    finished = Signal()

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(
            parent
        )

        self.accounts = []
        self.categories = []

        self.setObjectName(
            "add_transaction_dialog"
        )

        self.build_ui()
        self.load_accounts()
        self.load_categories()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self) -> None:
        layout = QVBoxLayout(
            self
        )

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
            "dialog_title"
        )

        subtitle = QLabel(
            "Record an income or expense and assign it to an account."
        )

        subtitle.setObjectName(
            "dialog_subtitle"
        )

        subtitle.setWordWrap(
            True
        )

        layout.addWidget(
            title
        )

        layout.addSpacing(
            6
        )

        layout.addWidget(
            subtitle
        )

        # -------------------------------------------------
        # Transaction section
        # -------------------------------------------------

        layout.addSpacing(
            30
        )

        transaction_title = QLabel(
            "Transaction"
        )

        transaction_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            transaction_title
        )

        layout.addSpacing(
            18
        )

        # -------------------------------------------------
        # Type
        # -------------------------------------------------

        type_label = QLabel(
            "Type"
        )

        type_label.setObjectName(
            "field_label"
        )

        layout.addWidget(
            type_label
        )

        layout.addSpacing(
            7
        )

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
        # Amount / Date / Account / Category
        # -------------------------------------------------

        layout.addSpacing(
            18
        )

        fields_grid = QGridLayout()

        fields_grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        fields_grid.setHorizontalSpacing(
            18
        )

        fields_grid.setVerticalSpacing(
            15
        )

        # Amount

        amount_container = (
            self.create_field_container(
                "Amount"
            )
        )

        self.amount_input = QLineEdit()

        self.amount_input.setPlaceholderText(
            "0.00"
        )

        self.amount_input.setFixedHeight(
            42
        )

        amount_container.layout().addWidget(
            self.amount_input
        )

        # Date

        date_container = (
            self.create_field_container(
                "Date"
            )
        )

        self.date_input = QDateEdit()

        self.date_input.setCalendarPopup(
            True
        )

        self.date_input.setDisplayFormat(
            "dd.MM.yyyy"
        )

        self.date_input.setDate(
            QDate.currentDate()
        )

        self.date_input.setFixedHeight(
            42
        )

        date_container.layout().addWidget(
            self.date_input
        )

        # Account

        account_container = (
            self.create_field_container(
                "Account"
            )
        )

        self.account_input = (
            ModernComboBox()
        )

        account_container.layout().addWidget(
            self.account_input
        )

        # Category

        category_container = (
            self.create_field_container(
                "Category"
            )
        )

        self.category_input = (
            ModernComboBox()
        )

        category_container.layout().addWidget(
            self.category_input
        )

        # Grid

        fields_grid.addWidget(
            amount_container,
            0,
            0,
        )

        fields_grid.addWidget(
            date_container,
            0,
            1,
        )

        fields_grid.addWidget(
            account_container,
            1,
            0,
        )

        fields_grid.addWidget(
            category_container,
            1,
            1,
        )

        fields_grid.setColumnStretch(
            0,
            1,
        )

        fields_grid.setColumnStretch(
            1,
            1,
        )

        layout.addLayout(
            fields_grid
        )

        # -------------------------------------------------
        # Separator
        # -------------------------------------------------

        layout.addSpacing(
            22
        )

        separator = QFrame()

        separator.setObjectName(
            "dialog_separator"
        )

        separator.setFrameShape(
            QFrame.Shape.HLine
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

        layout.addSpacing(
            22
        )

        details_title = QLabel(
            "Details"
        )

        details_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            details_title
        )

        layout.addSpacing(
            15
        )

        note_container = (
            self.create_field_container(
                "Note"
            )
        )

        self.note_input = QLineEdit()

        self.note_input.setPlaceholderText(
            "Optional note"
        )

        self.note_input.setFixedHeight(
            42
        )

        note_container.layout().addWidget(
            self.note_input
        )

        layout.addWidget(
            note_container
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

        layout.addSpacing(
            8
        )

        layout.addWidget(
            self.error_label
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        layout.addSpacing(
            20
        )

        buttons_layout = QHBoxLayout()

        buttons_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        buttons_layout.setSpacing(
            10
        )

        buttons_layout.addStretch()

        cancel_button = QPushButton(
            "Cancel"
        )

        cancel_button.setObjectName(
            "dialog_cancel_button"
        )

        cancel_button.setFixedHeight(
            42
        )

        cancel_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        save_button = QPushButton(
            "Add transaction"
        )

        save_button.setObjectName(
            "dialog_primary_button"
        )

        save_button.setFixedHeight(
            42
        )

        save_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        buttons_layout.addWidget(
            cancel_button
        )

        buttons_layout.addWidget(
            save_button
        )

        layout.addLayout(
            buttons_layout
        )

        # -------------------------------------------------
        # Connections
        # -------------------------------------------------

        cancel_button.clicked.connect(
            self.close_dialog
        )

        save_button.clicked.connect(
            self.save_transaction
        )

        self.amount_input.returnPressed.connect(
            self.save_transaction
        )

        self.note_input.returnPressed.connect(
            self.save_transaction
        )

        # -------------------------------------------------
        # Main styling
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QWidget#add_transaction_dialog {
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
            QDateEdit {
                background-color: #FFFFFF;
                color: #0F172A;

                border: 1px solid #CBD5E1;
                border-radius: 9px;

                padding-left: 12px;
                padding-right: 12px;

                font-size: 14px;
            }

            QLineEdit:hover,
            QDateEdit:hover {
                border-color: #94A3B8;
            }

            QLineEdit:focus,
            QDateEdit:focus {
                border-color: #64748B;
            }

            QLineEdit::placeholder {
                color: #94A3B8;
            }

            QDateEdit::drop-down {
                width: 30px;
                border: none;
                background: transparent;
            }

            QFrame#dialog_separator {
                background-color: #E2E8F0;
                border: none;
            }

            QLabel#error_label {
                color: #B91C1C;
                font-size: 13px;
            }

            QPushButton#dialog_cancel_button {
                background-color: #FFFFFF;
                color: #334155;

                border: 1px solid #CBD5E1;
                border-radius: 9px;

                padding: 0 18px;

                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#dialog_cancel_button:hover {
                background-color: #F8FAFC;
                border-color: #94A3B8;
            }

            QPushButton#dialog_primary_button {
                background-color: #0F172A;
                color: #FFFFFF;

                border: none;
                border-radius: 9px;

                padding: 0 18px;

                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#dialog_primary_button:hover {
                background-color: #1E293B;
            }

            QPushButton#dialog_primary_button:pressed {
                background-color: #334155;
            }
            """
        )

    # =====================================================
    # Field helper
    # =====================================================

    def create_field_container(
        self,
        label_text: str,
    ) -> QWidget:
        container = QWidget()

        layout = QVBoxLayout(
            container
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            7
        )

        label = QLabel(
            label_text
        )

        label.setObjectName(
            "field_label"
        )

        layout.addWidget(
            label
        )

        return container

    # =====================================================
    # Data
    # =====================================================

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

    def load_categories(self) -> None:
        self.refresh_categories()

    def refresh_categories(self) -> None:
        kind = (
            self.type_input.selected_kind
        )

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

    # =====================================================
    # Type
    # =====================================================

    def on_type_changed(
        self,
        kind: str,
    ) -> None:
        self.refresh_categories()

    # =====================================================
    # Amount
    # =====================================================

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
            .replace("€", "")
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

        cents = int(
            amount * 100
        )

        if cents <= 0:
            return None

        return cents

    # =====================================================
    # Save
    # =====================================================

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

        try:
            create_transaction(
                account_id=account_id,
                category_id=category_id,
                amount_cents=amount_cents,
                transaction_date=transaction_date,
                note=self.note_input.text(),
                kind=(
                    self.type_input.selected_kind
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