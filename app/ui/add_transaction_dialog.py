from decimal import Decimal, InvalidOperation

from PySide6.QtCore import (
    QEasingCurve,
    QRect,
    Qt,
    Signal,
    QPropertyAnimation,
)
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListView,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.services.account_service import list_accounts
from app.services.category_service import list_categories
from app.services.transaction_service import create_transaction
from app.services.recurring_transaction_service import (
    create_recurring_transaction,
    generate_due_transactions,
)
from app.ui.date_picker import OctumoDateEdit


# =========================================================
# Modern Combo Box
# =========================================================


class ModernComboBox(QComboBox):
    """
    Modern Octumo-style combo box.

    Uses a custom QToolButton for the dropdown arrow,
    matching the arrow used by OctumoDateEdit.
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

        view.setUniformItemSizes(
            True
        )

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

        view.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
        )

        view.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            False,
        )

        view.setAutoFillBackground(
            True
        )

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

        self.setView(
            view
        )

        # -------------------------------------------------
        # Dropdown arrow button
        # -------------------------------------------------

        self.dropdown_button = QToolButton(
            self
        )

        self.dropdown_button.setObjectName(
            "modern_combo_dropdown_button"
        )

        self.dropdown_button.setText(
            "▼"
        )

        self.dropdown_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.dropdown_button.setFixedSize(
            34,
            34,
        )

        self.dropdown_button.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        self.dropdown_button.clicked.connect(
            self.showPopup
        )

        # -------------------------------------------------
        # Style
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QComboBox#modern_combo_box {
                background-color: #FFFFFF;
                color: #0F172A;

                border: 1px solid #CBD5E1;
                border-radius: 9px;

                padding-left: 12px;
                padding-right: 38px;

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
                width: 0px;
                border: none;
                background: transparent;
            }

            QComboBox#modern_combo_box::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
            }

            QToolButton#modern_combo_dropdown_button {
                background-color: transparent;

                border: none;

                color: #17243A;

                font-size: 13px;
                font-weight: 700;

                padding: 0px;
            }

            QToolButton#modern_combo_dropdown_button:hover {
                background-color: #F1F5F9;

                border-radius: 9px;

                color: #0F172A;
            }

            QToolButton#modern_combo_dropdown_button:pressed {
                background-color: #E2E8F0;

                border-radius: 9px;
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

        self._position_dropdown_button()

    # =====================================================
    # Position dropdown button
    # =====================================================

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

        self._position_dropdown_button()

    def _position_dropdown_button(self) -> None:

        if not hasattr(
            self,
            "dropdown_button",
        ):
            return

        button_x = (
            self.width()
            - self.dropdown_button.width()
            - 4
        )

        button_y = (
            self.height()
            - self.dropdown_button.height()
        ) // 2

        self.dropdown_button.move(
            button_x,
            button_y,
        )

        self.dropdown_button.raise_()

    # =====================================================
    # Popup
    # =====================================================

    def showPopup(self) -> None:
        super().showPopup()

        self.dropdown_button.raise_()


# =========================================================
# Transaction Type Selector
# =========================================================


class TransactionTypeSelector(QWidget):
    type_changed = Signal(str)

    def __init__(
        self,
        parent=None,
    ) -> None:

        super().__init__(
            parent
        )

        self.selected_kind = "income"

        self._animation = None

        self.setObjectName(
            "transaction_type_selector"
        )

        self.setFixedHeight(
            44
        )

        self.indicator = QFrame(
            self
        )

        self.indicator.setObjectName(
            "transaction_type_indicator"
        )

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

        available_width = max(
            0,
            self.width() - 2 * margin,
        )

        button_width = (
            available_width // 2
        )

        button_height = max(
            0,
            self.height() - 2 * margin,
        )

        target_x = (
            margin
            if self.selected_kind == "income"
            else margin + button_width
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


# =========================================================
# Add Transaction Dialog
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

        try:
            generate_due_transactions()
        except Exception:
            pass

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

        layout.setSpacing(
            0
        )

        # -------------------------------------------------
        # Scroll area
        # -------------------------------------------------

        self.scroll_area = QScrollArea()

        self.scroll_area.setObjectName(
            "dialog_scroll_area"
        )

        self.scroll_area.setWidgetResizable(
            True
        )

        self.scroll_area.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        scroll_content = QWidget()

        scroll_content.setObjectName(
            "dialog_scroll_content"
        )

        content_layout = QVBoxLayout(
            scroll_content
        )

        content_layout.setContentsMargins(
            0,
            0,
            8,
            10,
        )

        content_layout.setSpacing(
            0
        )

        self.scroll_area.setWidget(
            scroll_content
        )

        layout.addWidget(
            self.scroll_area,
            1,
        )

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

        content_layout.addWidget(
            title
        )

        content_layout.addSpacing(
            5
        )

        content_layout.addWidget(
            subtitle
        )

        content_layout.addSpacing(
            24
        )

        # -------------------------------------------------
        # Transaction
        # -------------------------------------------------

        transaction_title = QLabel(
            "Transaction"
        )

        transaction_title.setObjectName(
            "section_title"
        )

        content_layout.addWidget(
            transaction_title
        )

        content_layout.addSpacing(
            14
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

        self.type_input = TransactionTypeSelector()

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

        content_layout.addWidget(
            type_container
        )

        content_layout.addSpacing(
            15
        )

        # -------------------------------------------------
        # Fields grid
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Amount
        # -------------------------------------------------

        amount_container = self.create_field_container(
            "Amount"
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

        # -------------------------------------------------
        # Date
        # -------------------------------------------------

        date_container = self.create_field_container(
            "Date"
        )

        self.date_input = OctumoDateEdit()

        date_container.layout().addWidget(
            self.date_input
        )

        # -------------------------------------------------
        # Account
        # -------------------------------------------------

        account_container = self.create_field_container(
            "Account"
        )

        self.account_input = ModernComboBox()

        account_container.layout().addWidget(
            self.account_input
        )

        # -------------------------------------------------
        # Category
        # -------------------------------------------------

        category_container = self.create_field_container(
            "Category"
        )

        self.category_input = ModernComboBox()

        category_container.layout().addWidget(
            self.category_input
        )

        # -------------------------------------------------
        # Grid placement
        # -------------------------------------------------

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

        content_layout.addLayout(
            fields_grid
        )

        content_layout.addSpacing(
            23
        )

        # -------------------------------------------------
        # Separator
        # -------------------------------------------------

        separator = QFrame()

        separator.setFrameShape(
            QFrame.Shape.HLine
        )

        separator.setObjectName(
            "dialog_separator"
        )

        content_layout.addWidget(
            separator
        )

        content_layout.addSpacing(
            18
        )

        # -------------------------------------------------
        # Recurring
        # -------------------------------------------------

        recurring_container = QWidget()

        recurring_layout = QVBoxLayout(
            recurring_container
        )

        recurring_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        recurring_layout.setSpacing(
            8
        )

        self.recurring_checkbox = QCheckBox(
            "Recurring / Subscription"
        )

        self.recurring_checkbox.setObjectName(
            "recurring_checkbox"
        )

        recurring_layout.addWidget(
            self.recurring_checkbox
        )

        # -------------------------------------------------
        # Frequency
        # -------------------------------------------------

        self.frequency_container = QWidget()

        frequency_layout = QHBoxLayout(
            self.frequency_container
        )

        frequency_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        frequency_layout.setSpacing(
            10
        )

        frequency_label = QLabel(
            "Frequency"
        )

        frequency_label.setObjectName(
            "field_label"
        )

        self.frequency_input = ModernComboBox()

        self.frequency_input.setMinimumWidth(
            150
        )

        self.frequency_input.addItem(
            "Daily",
            "daily",
        )

        self.frequency_input.addItem(
            "Weekly",
            "weekly",
        )

        self.frequency_input.addItem(
            "Monthly",
            "monthly",
        )

        self.frequency_input.addItem(
            "Yearly",
            "yearly",
        )

        frequency_layout.addWidget(
            frequency_label
        )

        frequency_layout.addWidget(
            self.frequency_input,
            1,
        )

        recurring_layout.addWidget(
            self.frequency_container
        )

        self.frequency_container.hide()

        # -------------------------------------------------
        # Recurring status
        # -------------------------------------------------

        self.recurring_status_label = QLabel(
            "Recurring: No"
        )

        self.recurring_status_label.setObjectName(
            "recurring_status_label"
        )

        recurring_layout.addWidget(
            self.recurring_status_label
        )

        self.recurring_description_label = QLabel(
            "This transaction will be added once."
        )

        self.recurring_description_label.setObjectName(
            "recurring_description_label"
        )

        self.recurring_description_label.setWordWrap(
            True
        )

        recurring_layout.addWidget(
            self.recurring_description_label
        )

        content_layout.addWidget(
            recurring_container
        )

        content_layout.addSpacing(
            17
        )

        # -------------------------------------------------
        # Note
        # -------------------------------------------------

        note_container = self.create_field_container(
            "Note"
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

        content_layout.addWidget(
            note_container
        )

        # -------------------------------------------------
        # Recurring signals
        # -------------------------------------------------

        self.recurring_checkbox.toggled.connect(
            self.frequency_container.setVisible
        )

        self.recurring_checkbox.toggled.connect(
            self.update_recurring_status
        )

        self.frequency_input.currentIndexChanged.connect(
            self.update_recurring_status
        )

        # -------------------------------------------------
        # Error
        # -------------------------------------------------

        self.error_label = QLabel()

        self.error_label.setObjectName(
            "dialog_error"
        )

        self.error_label.setWordWrap(
            True
        )

        self.error_label.hide()

        content_layout.addSpacing(
            10
        )

        content_layout.addWidget(
            self.error_label
        )

        content_layout.addSpacing(
            10
        )

        # -------------------------------------------------
        # Bottom spacer
        # -------------------------------------------------

        content_layout.addStretch(
            1
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        buttons_layout = QHBoxLayout()

        buttons_layout.setContentsMargins(
            0,
            14,
            0,
            14,
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

        # -------------------------------------------------
        # Signals
        # -------------------------------------------------

        self.type_input.type_changed.connect(
            self.load_categories
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
            QWidget#add_transaction_dialog {
                background-color: #FFFFFF;
            }

            QScrollArea#dialog_scroll_area {
                background-color: #FFFFFF;

                border: none;
            }

            QScrollArea#dialog_scroll_area > QWidget > QWidget {
                background-color: #FFFFFF;
            }

            QWidget#dialog_scroll_content {
                background-color: #FFFFFF;
            }

            QScrollArea#dialog_scroll_area QScrollBar:vertical {
                background: transparent;

                width: 7px;

                margin-top: 2px;
                margin-bottom: 2px;

                border: none;
            }

            QScrollArea#dialog_scroll_area QScrollBar::handle:vertical {
                background: #CBD5E1;

                border-radius: 3px;

                min-height: 40px;
            }

            QScrollArea#dialog_scroll_area QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }

            QScrollArea#dialog_scroll_area QScrollBar::add-line:vertical,
            QScrollArea#dialog_scroll_area QScrollBar::sub-line:vertical {
                height: 0px;

                border: none;

                background: transparent;
            }

            QScrollArea#dialog_scroll_area QScrollBar::add-page:vertical,
            QScrollArea#dialog_scroll_area QScrollBar::sub-page:vertical {
                background: transparent;
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

            QLineEdit {
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

            QLineEdit:hover {
                border-color: #94A3B8;
            }

            QLineEdit:focus {
                border-color: #64748B;

                background-color: #FFFFFF;
            }

            QLineEdit::placeholder {
                color: #94A3B8;
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

            QCheckBox#recurring_checkbox {
                color: #0F172A;

                font-size: 14px;

                font-weight: 600;

                spacing: 8px;
            }

            QCheckBox#recurring_checkbox::indicator {
                width: 18px;

                height: 18px;

                border: 1px solid #CBD5E1;

                border-radius: 5px;

                background-color: #FFFFFF;
            }

            QCheckBox#recurring_checkbox::indicator:hover {
                border-color: #94A3B8;
            }

            QCheckBox#recurring_checkbox::indicator:checked {
                background-color: #0F172A;

                border-color: #0F172A;
            }

            QLabel#recurring_status_label {
                color: #334155;

                font-size: 13px;

                font-weight: 600;
            }

            QLabel#recurring_description_label {
                color: #64748B;

                font-size: 12px;
            }

            QLabel#dialog_error {
                color: #DC2626;

                font-size: 13px;

                font-weight: 500;
            }
            """
        )

    # =====================================================
    # Recurring status
    # =====================================================

    def update_recurring_status(
        self,
    ) -> None:

        if not self.recurring_checkbox.isChecked():

            self.recurring_status_label.setText(
                "Recurring: No"
            )

            self.recurring_description_label.setText(
                "This transaction will be added once."
            )

            return

        frequency_text = (
            self.frequency_input.currentText()
        )

        self.recurring_status_label.setText(
            f"Recurring: Yes · {frequency_text}"
        )

        self.recurring_description_label.setText(
            "This transaction will be added now and future "
            "transactions will be generated automatically "
            "according to this frequency."
        )

    # =====================================================
    # Field container
    # =====================================================

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

    # =====================================================
    # Accounts
    # =====================================================

    def load_accounts(
        self,
    ) -> None:

        self.account_input.clear()

        accounts = list_accounts()

        self.accounts = accounts

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

    # =====================================================
    # Categories
    # =====================================================

    def load_categories(
        self,
    ) -> None:

        self.category_input.clear()

        kind = (
            self.type_input.selected_kind
        )

        categories = list_categories(
            kind=kind
        )

        self.categories = categories

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

    # =====================================================
    # Save
    # =====================================================

    def save_transaction(
        self,
    ) -> None:

        self.error_label.hide()

        # -------------------------------------------------
        # Account
        # -------------------------------------------------

        account_id = (
            self.account_input.currentData()
        )

        if account_id is None:

            self.show_error(
                "Please select an account."
            )

            self.account_input.setFocus()

            return

        # -------------------------------------------------
        # Category
        # -------------------------------------------------

        category_id = (
            self.category_input.currentData()
        )

        if category_id is None:

            self.show_error(
                "Please select a category."
            )

            self.category_input.setFocus()

            return

        # -------------------------------------------------
        # Amount
        # -------------------------------------------------

        amount_text = (
            self.amount_input
            .text()
            .strip()
            .replace(
                ",",
                ".",
            )
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

        # -------------------------------------------------
        # Amount in cents
        # -------------------------------------------------

        amount_cents = int(
            amount * Decimal("100")
        )

        if amount_cents <= 0:

            self.show_error(
                "Amount must be greater than zero."
            )

            self.amount_input.setFocus()

            return

        # -------------------------------------------------
        # Date
        # -------------------------------------------------

        transaction_date = (
            self.date_input
            .date()
            .toString(
                "yyyy-MM-dd"
            )
        )

        # -------------------------------------------------
        # Note
        # -------------------------------------------------

        note = (
            self.note_input
            .text()
            .strip()
        )

        # -------------------------------------------------
        # Type
        # -------------------------------------------------

        kind = (
            self.type_input.selected_kind
        )

        # -------------------------------------------------
        # Create normal transaction
        # -------------------------------------------------

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
                "An unexpected error occurred while saving "
                "the transaction."
            )

            return

        # -------------------------------------------------
        # Create recurring template
        # -------------------------------------------------

        if self.recurring_checkbox.isChecked():

            recurring_name = (
                note
                or self.category_input.currentText()
                or "Recurring transaction"
            )

            frequency = (
                self.frequency_input.currentData()
            )

            try:

                create_recurring_transaction(
                    name=recurring_name,
                    account_id=account_id,
                    category_id=category_id,
                    amount_cents=amount_cents,
                    kind=kind,
                    note=note,
                    frequency=frequency,
                    start_date=transaction_date,
                )

            except ValueError as error:

                self.show_error(
                    "Transaction was added, but recurring "
                    "setup failed: "
                    f"{error}"
                )

                return

            except Exception:

                self.show_error(
                    "Transaction was added, but recurring "
                    "setup failed."
                )

                return

        # -------------------------------------------------
        # Finished
        # -------------------------------------------------

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

        self.scroll_area.ensureWidgetVisible(
            self.error_label
        )

    # =====================================================
    # Close
    # =====================================================

    def close_dialog(
        self,
    ) -> None:

        self.finished.emit()