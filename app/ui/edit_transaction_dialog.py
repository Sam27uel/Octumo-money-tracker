from decimal import Decimal, InvalidOperation


from PySide6.QtCore import (
    QEasingCurve,
    QDate,
    QPropertyAnimation,
    QRect,
    Qt,
    Signal,
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

from app.services.transaction_service import (
    get_transaction,
    update_transaction,
)

from app.services.recurring_transaction_service import (
    create_recurring_transaction,
    delete_recurring_transaction,
    list_recurring_transactions,
    update_recurring_transaction,
)

from app.ui.date_picker import OctumoDateEdit


# =========================================================
# Modern Combo Box
# Same visual style as Add Transaction
# =========================================================


class ModernComboBox(QComboBox):

    def __init__(
        self,
        parent=None,
    ) -> None:

        super().__init__(
            parent
        )

        self.setObjectName(
            "modern_combo_box"
        )

        self.setFixedHeight(
            42
        )

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

        view.setSpacing(
            2
        )

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

    def resizeEvent(
        self,
        event,
    ) -> None:

        super().resizeEvent(
            event
        )

        self._position_dropdown_button()

    def _position_dropdown_button(
        self,
    ) -> None:

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

    def showPopup(
        self,
    ) -> None:

        super().showPopup()

        self.dropdown_button.raise_()


# =========================================================
# Transaction Type Selector
# Same visual style as Add Transaction
# =========================================================


class TransactionTypeSelector(QWidget):

    type_changed = Signal(str)

    def __init__(
        self,
        selected_kind: str = "income",
        parent=None,
    ) -> None:

        super().__init__(
            parent
        )

        self.selected_kind = (
            selected_kind
            if selected_kind in {
                "income",
                "expense",
            }
            else "income"
        )

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

        self.income_button.setChecked(
            self.selected_kind == "income"
        )

        self.expense_button.setChecked(
            self.selected_kind == "expense"
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

    # =====================================================
    # Show
    # =====================================================

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

    # =====================================================
    # Resize
    # =====================================================

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

    # =====================================================
    # Layout
    # =====================================================

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

    # =====================================================
    # Set type
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


# =========================================================
# Edit Transaction Dialog
# =========================================================


class EditTransactionDialog(QWidget):

    finished = Signal()

    def __init__(
        self,
        transaction_id: int,
        parent=None,
    ) -> None:

        super().__init__(
            parent
        )

        self.transaction_id = transaction_id

        self.transaction = None

        self.accounts = []
        self.categories = []

        self.recurring_transaction = None

        self.setObjectName(
            "edit_transaction_dialog"
        )

        self.build_ui()

        self.load_transaction()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(
        self,
    ) -> None:

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

        # =================================================
        # Scroll area
        # Same as Add Transaction
        # =================================================

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

        # =================================================
        # Header
        # =================================================

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

        # =================================================
        # Transaction
        # =================================================

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

        # =================================================
        # Type
        # =================================================

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

        # =================================================
        # Fields grid
        # Same as Add Transaction
        # =================================================

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

        # =================================================
        # Amount
        # =================================================

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

        # =================================================
        # Date
        # =================================================

        date_container = (
            self.create_field_container(
                "Date"
            )
        )

        self.date_input = OctumoDateEdit()

        date_container.layout().addWidget(
            self.date_input
        )

        # =================================================
        # Account
        # =================================================

        account_container = (
            self.create_field_container(
                "Account"
            )
        )

        self.account_input = ModernComboBox()

        account_container.layout().addWidget(
            self.account_input
        )

        # =================================================
        # Category
        # =================================================

        category_container = (
            self.create_field_container(
                "Category"
            )
        )

        self.category_input = ModernComboBox()

        category_container.layout().addWidget(
            self.category_input
        )

        # =================================================
        # Grid placement
        # =================================================

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

        # =================================================
        # Separator
        # =================================================

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

        # =================================================
        # Recurring
        # Exact Add Transaction structure
        # =================================================

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

        # -------------------------------------------------
        # Checkbox
        # -------------------------------------------------

        self.recurring_checkbox = QCheckBox(
            "Recurring / Subscription"
        )

        self.recurring_checkbox.setObjectName(
            "recurring_checkbox"
        )

        self.recurring_checkbox.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        recurring_layout.addWidget(
            self.recurring_checkbox
        )

        # -------------------------------------------------
        # Frequency
        # Same horizontal layout as Add
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

        # -------------------------------------------------
        # Recurring description
        # -------------------------------------------------

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

        # =================================================
        # Note
        # =================================================

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

        content_layout.addWidget(
            note_container
        )

        # =================================================
        # Signals
        # =================================================

        self.recurring_checkbox.toggled.connect(
            self.frequency_container.setVisible
        )

        self.recurring_checkbox.toggled.connect(
            self.update_recurring_status
        )

        self.frequency_input.currentIndexChanged.connect(
            self.update_recurring_status
        )

        self.type_input.type_changed.connect(
            self.on_type_changed
        )

        self.amount_input.returnPressed.connect(
            self.save_transaction
        )

        self.note_input.returnPressed.connect(
            self.save_transaction
        )

        # =================================================
        # Error
        # =================================================

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

        # =================================================
        # Bottom spacer
        # =================================================

        content_layout.addStretch(
            1
        )

        # =================================================
        # Buttons
        # Same as Add Transaction
        # =================================================

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

        self.cancel_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        buttons_layout.addWidget(
            self.cancel_button
        )

        self.save_button = QPushButton(
            "Save changes"
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

        self.save_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        buttons_layout.addWidget(
            self.save_button
        )

        layout.addLayout(
            buttons_layout
        )

        # =================================================
        # Connections
        # =================================================

        self.cancel_button.clicked.connect(
            self.close_dialog
        )

        self.save_button.clicked.connect(
            self.save_transaction
        )

        # =================================================
        # Style
        # Same as Add Transaction
        # =================================================

        self.setStyleSheet(
            """
            QWidget#edit_transaction_dialog {
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

            /* =================================================
               Header
               ================================================= */

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

            /* =================================================
               Text fields
               ================================================= */

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

            /* =================================================
               Separator
               ================================================= */

            QFrame#dialog_separator {
                background-color: #E2E8F0;

                color: #E2E8F0;

                border: none;

                min-height: 1px;

                max-height: 1px;
            }

            /* =================================================
               Recurring
               ================================================= */

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

            /* =================================================
               Error
               ================================================= */

            QLabel#dialog_error {
                color: #DC2626;

                font-size: 13px;

                font-weight: 500;
            }

            /* =================================================
               Buttons
               ================================================= */

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
            """
        )

        self.update_recurring_status()

    # =====================================================
    # Field container
    # Same as Add Transaction
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
    # Load transaction
    # =====================================================

    def load_transaction(
        self,
    ) -> None:

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

        # =================================================
        # Amount
        # =================================================

        amount = (
            abs(
                transaction["amount_cents"]
            )
            / 100
        )

        self.amount_input.setText(
            f"{amount:.2f}"
        )

        # =================================================
        # Date
        # =================================================

        transaction_date = QDate.fromString(
            transaction["transaction_date"],
            "yyyy-MM-dd",
        )

        if transaction_date.isValid():

            self.date_input.setDate(
                transaction_date
            )

        else:

            self.date_input.setDate(
                QDate.currentDate()
            )

        # =================================================
        # Account
        # =================================================

        self.load_accounts(
            transaction["account_id"]
        )

        # =================================================
        # Category
        # =================================================

        self.load_categories(
            transaction["category_id"]
        )

        # =================================================
        # Note
        # =================================================

        self.note_input.setText(
            transaction["note"] or ""
        )

        # =================================================
        # Recurring
        # =================================================

        self.load_recurring_transaction()

    # =====================================================
    # Recurring lookup
    # =====================================================

    def load_recurring_transaction(
        self,
    ) -> None:

        self.recurring_transaction = None

        try:

            recurring_transactions = (
                list_recurring_transactions(
                    include_inactive=True
                )
            )

        except Exception:

            recurring_transactions = []

        if self.transaction is None:

            self.recurring_checkbox.setChecked(
                False
            )

            self.update_recurring_status()

            return

        transaction_amount = abs(
            self.transaction["amount_cents"]
        )

        transaction_kind = (
            "income"
            if self.transaction["amount_cents"] > 0
            else "expense"
        )

        transaction_date = (
            self.transaction["transaction_date"]
        )

        transaction_note = (
            self.transaction["note"] or ""
        )

        # -------------------------------------------------
        # Exact match including start date
        # -------------------------------------------------

        exact_matches = []

        for recurring in recurring_transactions:

            if (
                recurring["account_id"]
                != self.transaction["account_id"]
            ):
                continue

            if (
                recurring["category_id"]
                != self.transaction["category_id"]
            ):
                continue

            if (
                abs(
                    recurring["amount_cents"]
                )
                != transaction_amount
            ):
                continue

            if (
                recurring["kind"]
                != transaction_kind
            ):
                continue

            if (
                recurring["start_date"]
                != transaction_date
            ):
                continue

            exact_matches.append(
                recurring
            )

        # -------------------------------------------------
        # Broader match
        # -------------------------------------------------

        if exact_matches:

            self.recurring_transaction = (
                exact_matches[0]
            )

        else:

            broad_matches = []

            for recurring in recurring_transactions:

                if (
                    recurring["account_id"]
                    != self.transaction["account_id"]
                ):
                    continue

                if (
                    recurring["category_id"]
                    != self.transaction["category_id"]
                ):
                    continue

                if (
                    abs(
                        recurring["amount_cents"]
                    )
                    != transaction_amount
                ):
                    continue

                if (
                    recurring["kind"]
                    != transaction_kind
                ):
                    continue

                recurring_note = (
                    recurring["note"] or ""
                )

                if recurring_note != transaction_note:
                    continue

                broad_matches.append(
                    recurring
                )

            if broad_matches:

                active_matches = [
                    recurring
                    for recurring in broad_matches
                    if recurring["is_active"]
                ]

                if active_matches:

                    self.recurring_transaction = (
                        active_matches[0]
                    )

                else:

                    self.recurring_transaction = (
                        broad_matches[0]
                    )

        # -------------------------------------------------
        # Update UI
        # -------------------------------------------------

        if self.recurring_transaction is None:

            self.recurring_checkbox.setChecked(
                False
            )

        else:

            self.recurring_checkbox.setChecked(
                True
            )

            frequency = (
                self.recurring_transaction[
                    "frequency"
                ]
            )

            frequency_index = (
                self.frequency_input.findData(
                    frequency
                )
            )

            if frequency_index >= 0:

                self.frequency_input.setCurrentIndex(
                    frequency_index
                )

        self.update_recurring_status()

    # =====================================================
    # Accounts
    # =====================================================

    def load_accounts(
        self,
        selected_id=None,
    ) -> None:

        self.account_input.clear()

        self.accounts = list_accounts()

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

        if not self.accounts:

            self.account_input.addItem(
                "No accounts available",
                None,
            )

        elif selected_index >= 0:

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

        self.category_input.clear()

        kind = (
            self.type_input.selected_kind
        )

        self.categories = list_categories(
            kind=kind,
            include_archived=True,
        )

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

        if not self.categories:

            self.category_input.addItem(
                "No categories available",
                None,
            )

        elif selected_index >= 0:

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
    # Recurring status
    # Same visual structure as Add
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
    # Amount
    # =====================================================

    def parse_amount(
        self,
    ):

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

        return (
            cents
            if cents > 0
            else None
        )

    # =====================================================
    # Save
    # =====================================================

    def save_transaction(
        self,
    ) -> None:

        self.error_label.hide()

        if self.transaction is None:

            self.show_error(
                "Transaction could not be loaded."
            )

            return

        account_id = (
            self.account_input.currentData()
        )

        if account_id is None:

            self.show_error(
                "Please select an account."
            )

            self.account_input.setFocus()

            return

        category_id = (
            self.category_input.currentData()
        )

        if category_id is None:

            self.show_error(
                "Please select a category."
            )

            self.category_input.setFocus()

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

        kind = (
            self.type_input.selected_kind
        )

        recurring_enabled = (
            self.recurring_checkbox.isChecked()
        )

        frequency = (
            self.frequency_input.currentData()
        )

        # -------------------------------------------------
        # Keep old recurring transaction
        # -------------------------------------------------

        old_recurring = (
            self.recurring_transaction
        )

        try:

            # =================================================
            # 1. Update normal transaction
            # =================================================

            update_transaction(
                transaction_id=self.transaction_id,
                account_id=account_id,
                category_id=category_id,
                amount_cents=amount_cents,
                transaction_date=transaction_date,
                note=note,
                kind=kind,
            )

            # =================================================
            # 2. Recurring enabled
            # =================================================

            if recurring_enabled:

                recurring_name = (
                    self.transaction["name"]
                    if "name"
                    in self.transaction.keys()
                    and self.transaction["name"]
                    else None
                )

                if not recurring_name:

                    recurring_name = (
                        self.transaction[
                            "category_name"
                        ]
                        if "category_name"
                        in self.transaction.keys()
                        and self.transaction[
                            "category_name"
                        ]
                        else "Recurring transaction"
                    )

                # -------------------------------------------------
                # Existing recurring -> update
                # -------------------------------------------------

                if old_recurring is not None:

                    update_recurring_transaction(
                        recurring_transaction_id=(
                            old_recurring["id"]
                        ),
                        name=recurring_name,
                        account_id=account_id,
                        category_id=category_id,
                        amount_cents=amount_cents,
                        kind=kind,
                        note=note,
                        frequency=frequency,
                        start_date=transaction_date,
                    )

                # -------------------------------------------------
                # No recurring -> create
                # -------------------------------------------------

                else:

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

            # =================================================
            # 3. Recurring switched OFF
            # =================================================

            else:

                if old_recurring is not None:

                    delete_recurring_transaction(
                        old_recurring["id"]
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

        self.scroll_area.ensureWidgetVisible(
            self.error_label
        )

    def clear_error(
        self,
    ) -> None:

        self.error_label.clear()

        self.error_label.hide()

    # =====================================================
    # Close
    # =====================================================

    def close_dialog(
        self,
    ) -> None:

        self.finished.emit()