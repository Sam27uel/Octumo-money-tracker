from decimal import Decimal, InvalidOperation

from PySide6.QtCore import (
    QDate,
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    Qt,
    Signal,
)
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


class ModernComboBox(QComboBox):
    """
    Modern Octumo-style combo box.

    Uses a clean QListView popup without the default
    sharp macOS/Qt styling.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setObjectName(
            "modern_combo_box"
        )

        self.setFixedHeight(42)

        # ---------------------------------------------------------
        # CUSTOM POPUP VIEW
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # POPUP WINDOW
        # ---------------------------------------------------------

        view.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
        )

        # IMPORTANT:
        # Do NOT use WA_TranslucentBackground here.
        # On macOS this can cause the popup to render black.
        view.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            False,
        )

        view.setAutoFillBackground(
            True
        )

        # ---------------------------------------------------------
        # POPUP PALETTE
        # ---------------------------------------------------------

        palette = view.palette()

        palette.setColor(
            view.palette().ColorRole.Window,
            Qt.GlobalColor.white,
        )

        palette.setColor(
            view.palette().ColorRole.Base,
            Qt.GlobalColor.white,
        )

        palette.setColor(
            view.palette().ColorRole.Text,
            Qt.GlobalColor.black,
        )

        view.setPalette(
            palette
        )

        # ---------------------------------------------------------
        # ASSIGN VIEW
        # ---------------------------------------------------------

        self.setView(
            view
        )

        # ---------------------------------------------------------
        # COMBO + POPUP STYLE
        # ---------------------------------------------------------

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
                border: 1px solid #94A3B8;
            }

            QComboBox#modern_combo_box:focus {
                border: 1px solid #64748B;
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


class TransactionTypeSelector(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.selected_kind = "income"

        self._animation = None

        self.setObjectName(
            "transaction_type_selector"
        )

        self.setFixedHeight(44)

        # ---------------------------------------------------------
        # INDICATOR
        # ---------------------------------------------------------

        self.indicator = QFrame(
            self
        )

        self.indicator.setObjectName(
            "transaction_type_indicator"
        )

        # ---------------------------------------------------------
        # BUTTONS
        # ---------------------------------------------------------

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

        self.income_button.setChecked(
            True
        )

        # ---------------------------------------------------------
        # BUTTON GROUP
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # STYLE
        # ---------------------------------------------------------

        self.setStyleSheet(
            """
            QWidget#transaction_type_selector {
                background-color: #F1F5F9;

                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }

            QFrame#transaction_type_indicator {
                background-color: #0F172A;

                border-radius: 9px;
            }

            QPushButton#transaction_type_button {
                background-color: transparent;

                color: #64748B;

                border: none;
                border-radius: 9px;

                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#transaction_type_button:hover {
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

    def showEvent(
        self,
        event,
    ) -> None:

        super().showEvent(
            event
        )

        self.update_layout(
            animated=False
        )

    def resizeEvent(
        self,
        event,
    ) -> None:

        super().resizeEvent(
            event
        )

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

        target_rect = QRect(
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

        if not animated:

            self.indicator.setGeometry(
                target_rect
            )

            self.income_button.setGeometry(
                income_rect
            )

            self.expense_button.setGeometry(
                expense_rect
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
            target_rect
        )

        animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self._animation = animation

        animation.start()

    def set_transaction_type(
        self,
        kind: str,
    ) -> None:

        if kind == self.selected_kind:
            return

        self.selected_kind = kind

        self.update_layout(
            animated=True
        )


class AddTransactionDialog(QWidget):

    finished = Signal()

    def __init__(
        self,
        parent=None,
    ) -> None:

        super().__init__(
            parent
        )

        self.setObjectName(
            "add_transaction_dialog"
        )

        self.build_ui()

        self.load_accounts()

        self.load_categories()

    # =============================================================
    # UI
    # =============================================================

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

        layout.setSpacing(
            0
        )

        # ---------------------------------------------------------
        # HEADER
        # ---------------------------------------------------------

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
            5
        )

        layout.addWidget(
            subtitle
        )

        layout.addSpacing(
            24
        )

        # ---------------------------------------------------------
        # TRANSACTION
        # ---------------------------------------------------------

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
            14
        )

        # ---------------------------------------------------------
        # TYPE
        # ---------------------------------------------------------

        type_label = QLabel(
            "Type"
        )

        type_label.setObjectName(
            "field_label"
        )

        self.type_input = (
            TransactionTypeSelector()
        )

        type_container = QWidget()

        type_layout = QVBoxLayout(
            type_container
        )

        type_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        type_layout.setSpacing(
            7
        )

        type_layout.addWidget(
            type_label
        )

        type_layout.addWidget(
            self.type_input
        )

        layout.addWidget(
            type_container
        )

        layout.addSpacing(
            15
        )

        # ---------------------------------------------------------
        # GRID
        # ---------------------------------------------------------

        fields_grid = QGridLayout()

        fields_grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        fields_grid.setHorizontalSpacing(
            14
        )

        fields_grid.setVerticalSpacing(
            15
        )

        # ---------------------------------------------------------
        # AMOUNT
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # DATE
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # ACCOUNT
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # CATEGORY
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # GRID PLACEMENT
        # ---------------------------------------------------------

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
            1
        )

        fields_grid.setColumnStretch(
            1,
            1
        )

        layout.addLayout(
            fields_grid
        )

        layout.addSpacing(
            23
        )

        # ---------------------------------------------------------
        # SEPARATOR
        # ---------------------------------------------------------

        separator = QFrame()

        separator.setFrameShape(
            QFrame.Shape.HLine
        )

        separator.setObjectName(
            "dialog_separator"
        )

        layout.addWidget(
            separator
        )

        layout.addSpacing(
            21
        )

        # ---------------------------------------------------------
        # DETAILS
        # ---------------------------------------------------------

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
            13
        )

        # ---------------------------------------------------------
        # NOTE
        # ---------------------------------------------------------

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

        # ---------------------------------------------------------
        # ERROR
        # ---------------------------------------------------------

        self.error_label = QLabel()

        self.error_label.setObjectName(
            "dialog_error"
        )

        self.error_label.setWordWrap(
            True
        )

        self.error_label.hide()

        layout.addSpacing(
            10
        )

        layout.addWidget(
            self.error_label
        )

        # ---------------------------------------------------------
        # BUTTONS
        # ---------------------------------------------------------

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

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.cancel_button.setObjectName(
            "dialog_cancel_button"
        )

        self.cancel_button.setFixedHeight(
            42
        )

        self.cancel_button.clicked.connect(
            self.close_dialog
        )

        buttons_layout.addWidget(
            self.cancel_button
        )

        self.save_button = QPushButton(
            "Add transaction"
        )

        self.save_button.setObjectName(
            "dialog_primary_button"
        )

        self.save_button.setFixedHeight(
            42
        )

        self.save_button.setMinimumWidth(
            145
        )

        self.save_button.clicked.connect(
            self.save_transaction
        )

        buttons_layout.addWidget(
            self.save_button
        )

        layout.addLayout(
            buttons_layout
        )

        # ---------------------------------------------------------
        # SIGNALS
        # ---------------------------------------------------------

        self.type_input.income_button.clicked.connect(
            self.load_categories
        )

        self.type_input.expense_button.clicked.connect(
            self.load_categories
        )

        self.amount_input.returnPressed.connect(
            self.save_transaction
        )

        self.note_input.returnPressed.connect(
            self.save_transaction
        )

        # ---------------------------------------------------------
        # STYLE
        # ---------------------------------------------------------

        self.setStyleSheet(
            """
            QWidget#add_transaction_dialog {
                background-color: #FFFFFF;
            }

            QLabel#dialog_title {
                color: #0F172A;

                font-size: 25px;
                font-weight: 700;
            }

            QLabel#dialog_subtitle {
                color: #64748B;

                font-size: 14px;
            }

            QLabel#section_title {
                color: #0F172A;

                font-size: 16px;
                font-weight: 700;
            }

            QLabel#field_label {
                color: #334155;

                font-size: 13px;
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

                selection-background-color: #E2E8F0;
                selection-color: #0F172A;
            }

            QLineEdit:hover,
            QDateEdit:hover {
                border: 1px solid #94A3B8;
            }

            QLineEdit:focus,
            QDateEdit:focus {
                border: 1px solid #64748B;

                background-color: #FFFFFF;
            }

            QDateEdit {
                padding-right: 32px;
            }

            QDateEdit::drop-down {
                width: 30px;

                border: none;

                background: transparent;
            }

            QFrame#dialog_separator {
                background-color: #E2E8F0;
                color: #E2E8F0;

                border: none;

                min-height: 1px;
                max-height: 1px;
            }

            QPushButton#dialog_cancel_button {
                background-color: #FFFFFF;
                color: #334155;

                border: 1px solid #CBD5E1;
                border-radius: 9px;

                padding-left: 17px;
                padding-right: 17px;

                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#dialog_cancel_button:hover {
                background-color: #F8FAFC;

                border-color: #94A3B8;
            }

            QPushButton#dialog_cancel_button:pressed {
                background-color: #F1F5F9;
            }

            QPushButton#dialog_primary_button {
                background-color: #0F172A;
                color: #FFFFFF;

                border: none;
                border-radius: 9px;

                padding-left: 18px;
                padding-right: 18px;

                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#dialog_primary_button:hover {
                background-color: #1E293B;
            }

            QPushButton#dialog_primary_button:pressed {
                background-color: #334155;
            }

            QLabel#dialog_error {
                color: #DC2626;

                font-size: 13px;
                font-weight: 500;
            }
            """
        )

    # =============================================================
    # FIELD CONTAINER
    # =============================================================

    def create_field_container(
        self,
        label_text: str,
    ) -> QWidget:

        container = QWidget()

        container_layout = QVBoxLayout(
            container
        )

        container_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        container_layout.setSpacing(
            7
        )

        label = QLabel(
            label_text
        )

        label.setObjectName(
            "field_label"
        )

        container_layout.addWidget(
            label
        )

        return container

    # =============================================================
    # ACCOUNTS
    # =============================================================

    def load_accounts(self) -> None:

        self.account_input.clear()

        accounts = list_accounts()

        for account in accounts:

            self.account_input.addItem(
                account["name"],
                account["id"],
            )

        if not accounts:

            self.account_input.addItem(
                "No accounts available",
                None,
            )

    # =============================================================
    # CATEGORIES
    # =============================================================

    def load_categories(self) -> None:

        self.category_input.clear()

        kind = (
            self.type_input.selected_kind
        )

        categories = list_categories(
            kind=kind
        )

        for category in categories:

            self.category_input.addItem(
                category["name"],
                category["id"],
            )

        if not categories:

            self.category_input.addItem(
                "No categories available",
                None,
            )

    # =============================================================
    # SAVE
    # =============================================================

    def save_transaction(self) -> None:

        self.error_label.hide()

        # ---------------------------------------------------------
        # ACCOUNT
        # ---------------------------------------------------------

        account_id = (
            self.account_input.currentData()
        )

        if account_id is None:

            self.show_error(
                "Please select an account."
            )

            self.account_input.setFocus()

            return

        # ---------------------------------------------------------
        # CATEGORY
        # ---------------------------------------------------------

        category_id = (
            self.category_input.currentData()
        )

        if category_id is None:

            self.show_error(
                "Please select a category."
            )

            self.category_input.setFocus()

            return

        # ---------------------------------------------------------
        # AMOUNT
        # ---------------------------------------------------------

        amount_text = (
            self.amount_input
            .text()
            .strip()
            .replace(",", ".")
        )

        if not amount_text:

            self.show_error(
                "Please enter an amount."
            )

            self.amount_input.setFocus()

            return

        try:

            amount = Decimal(
                amount_text
            )

        except InvalidOperation:

            self.show_error(
                "Please enter a valid amount."
            )

            self.amount_input.setFocus()

            return

        if amount <= 0:

            self.show_error(
                "Amount must be greater than zero."
            )

            self.amount_input.setFocus()

            return

        amount_cents = int(
            amount
            * Decimal("100")
        )

        if amount_cents <= 0:

            self.show_error(
                "Amount must be greater than zero."
            )

            self.amount_input.setFocus()

            return

        # ---------------------------------------------------------
        # DATE
        # ---------------------------------------------------------

        transaction_date = (
            self.date_input
            .date()
            .toString(
                "yyyy-MM-dd"
            )
        )

        # ---------------------------------------------------------
        # NOTE
        # ---------------------------------------------------------

        note = (
            self.note_input
            .text()
            .strip()
        )

        # ---------------------------------------------------------
        # TYPE
        # ---------------------------------------------------------

        kind = (
            self.type_input.selected_kind
        )

        # ---------------------------------------------------------
        # CREATE
        # ---------------------------------------------------------

        try:

            create_transaction(
                account_id=account_id,
                category_id=category_id,
                amount_cents=amount_cents,
                transaction_date=transaction_date,
                note=note,
                kind=kind,
            )

        except ValueError as error:

            self.show_error(
                str(error)
            )

            return

        except Exception:

            self.show_error(
                "An unexpected error occurred while saving the transaction."
            )

            return

        # ---------------------------------------------------------
        # SUCCESS
        # ---------------------------------------------------------

        self.finished.emit()

    # =============================================================
    # ERROR
    # =============================================================

    def show_error(
        self,
        message: str,
    ) -> None:

        self.error_label.setText(
            message
        )

        self.error_label.show()

    # =============================================================
    # CLOSE
    # =============================================================

    def close_dialog(self) -> None:

        self.finished.emit()