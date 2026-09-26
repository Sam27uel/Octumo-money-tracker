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
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListView,
    QLineEdit,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QListWidgetItem,
    
)

from app.services.account_service import list_accounts
from app.services.category_service import list_categories
from app.services.transaction_service import create_transaction
from app.ui.date_picker import OctumoDateEdit


# =========================================================
# Modern Combo Box
# =========================================================

class RoundedComboPopup(QWidget):
    def __init__(self, combo_box):
        super().__init__(None)

        self.combo_box = combo_box

        # ---------------------------------------------------------
        # POPUP WINDOW
        # ---------------------------------------------------------

        self.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_NoSystemBackground
        )

        self.setObjectName(
            "rounded_combo_popup_window"
        )

        # ---------------------------------------------------------
        # OUTER LAYOUT
        # ---------------------------------------------------------

        outer_layout = QVBoxLayout(self)

        outer_layout.setContentsMargins(
            1,
            1,
            1,
            1,
        )

        outer_layout.setSpacing(0)

        # ---------------------------------------------------------
        # ACTUAL ROUNDED SURFACE
        # ---------------------------------------------------------

        self.surface = QFrame()

        self.surface.setObjectName(
            "rounded_combo_surface"
        )

        self.surface.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.surface.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground
        )

        self.surface.setStyleSheet(
            """
            QFrame#rounded_combo_surface {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 16px;
            }
            """
        )

        outer_layout.addWidget(
            self.surface
        )

        # ---------------------------------------------------------
        # SURFACE LAYOUT
        # ---------------------------------------------------------

        layout = QVBoxLayout(
            self.surface
        )

        layout.setContentsMargins(
            7,
            7,
            7,
            7,
        )

        layout.setSpacing(3)

        # ---------------------------------------------------------
        # OPTIONS
        # ---------------------------------------------------------

        self.list_widget = QListWidget()

        self.list_widget.setObjectName(
            "rounded_combo_options"
        )

        self.list_widget.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.list_widget.setFrameShadow(
            QFrame.Shadow.Plain
        )

        self.list_widget.setLineWidth(0)

        self.list_widget.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.list_widget.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.list_widget.setSpacing(3)

        self.list_widget.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        self.list_widget.setStyleSheet(
            """
            QListWidget#rounded_combo_options {
                background: transparent;
                border: none;
                outline: none;
                padding: 0px;
            }

            QListWidget#rounded_combo_options::item {
                background: transparent;

                color: #17233B;

                min-height: 38px;

                padding-left: 12px;
                padding-right: 12px;

                border-radius: 10px;

                font-size: 15px;
                font-weight: 600;
            }

            QListWidget#rounded_combo_options::item:hover {
                background: #F1F5F9;
                color: #17233B;
            }

            QListWidget#rounded_combo_options::item:selected {
                background: #E8EDF5;
                color: #17233B;
            }

            QListWidget#rounded_combo_options QScrollBar:vertical {
                width: 6px;

                background: transparent;
                border: none;

                margin: 6px 2px 6px 0px;
            }

            QListWidget#rounded_combo_options QScrollBar::handle:vertical {
                background: #CBD5E1;

                min-height: 30px;

                border-radius: 3px;
            }

            QListWidget#rounded_combo_options QScrollBar::add-line:vertical,
            QListWidget#rounded_combo_options QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QListWidget#rounded_combo_options QScrollBar::add-page:vertical,
            QListWidget#rounded_combo_options QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

        layout.addWidget(
            self.list_widget
        )

        # ---------------------------------------------------------
        # CLICK
        # ---------------------------------------------------------

        self.list_widget.itemClicked.connect(
            self._item_clicked
        )

    # -------------------------------------------------------------
    # ITEM CLICKED
    # -------------------------------------------------------------

    def _item_clicked(self, item):
        index = item.data(
            Qt.ItemDataRole.UserRole
        )

        if index is None:
            return

        self.combo_box.setCurrentIndex(
            index
        )

        self.hide()

    # -------------------------------------------------------------
    # REFRESH
    # -------------------------------------------------------------

    def refresh_items(self):
        self.list_widget.clear()

        for index in range(
            self.combo_box.count()
        ):
            item = QListWidgetItem(
                self.combo_box.itemText(index)
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                index
            )

            self.list_widget.addItem(
                item
            )

        # ---------------------------------------------------------
        # CURRENT ITEM
        # ---------------------------------------------------------

        current_index = (
            self.combo_box.currentIndex()
        )

        if current_index >= 0:
            self.list_widget.setCurrentRow(
                current_index
            )

        # ---------------------------------------------------------
        # HEIGHT
        # ---------------------------------------------------------

        item_count = (
            self.combo_box.count()
        )

        visible_items = min(
            item_count,
            7
        )

        item_height = 41

        popup_height = (
            visible_items * item_height
            + 16
        )

        self.setFixedHeight(
            max(
                54,
                popup_height
            )
        )
        
class ModernComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName(
            "modern_combo_box"
        )

        self.setFixedHeight(42)

        self.setStyleSheet(
            """
            QComboBox#modern_combo_box {
                background: #FFFFFF;

                border: 1px solid #CBD5E1;
                border-radius: 12px;

                color: #17233B;

                font-size: 15px;
                font-weight: 600;

                padding-left: 14px;
                padding-right: 42px;
            }

            QComboBox#modern_combo_box:hover {
                border: 1px solid #94A3B8;
            }

            QComboBox#modern_combo_box:focus {
                border: 1px solid #17233B;
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
            """
        )

        self.arrow_button = QToolButton(self)

        self.arrow_button.setObjectName(
            "octumo_combo_arrow"
        )

        self.arrow_button.setText("▼")

        self.arrow_button.setFixedSize(
            34,
            34,
        )

        self.arrow_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.arrow_button.setFocusPolicy(
            Qt.FocusPolicy.NoFocus
        )

        self.arrow_button.setStyleSheet(
            """
            QToolButton#octumo_combo_arrow {
                background: transparent;
                border: none;

                color: #17233B;

                font-size: 13px;
                font-weight: 700;

                padding: 0px;
                margin: 0px;
            }

            QToolButton#octumo_combo_arrow:hover {
                color: #0F172A;
            }
            """
        )

        self.arrow_button.clicked.connect(
            self.showPopup
        )

        self._custom_popup = RoundedComboPopup(
            self
        )

        self._position_arrow_button()

    def showPopup(self):
        self._custom_popup.refresh_items()

        self._custom_popup.setFixedWidth(
            self.width()
        )

        position = self.mapToGlobal(
            self.rect().bottomLeft()
        )

        self._custom_popup.move(
            position.x(),
            position.y() + 6,
        )

        self._custom_popup.show()
        self._custom_popup.raise_()

    def hidePopup(self):
        if hasattr(
            self,
            "_custom_popup",
        ):
            self._custom_popup.hide()

    def _position_arrow_button(self):
        if not hasattr(
            self,
            "arrow_button",
        ):
            return

        x = (
            self.width()
            - self.arrow_button.width()
            - 6
        )

        y = (
            self.height()
            - self.arrow_button.height()
        ) // 2

        self.arrow_button.move(
            x,
            y
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_arrow_button()


# =========================================================
# Transaction Type Selector
# =========================================================

class TransactionTypeSelector(QWidget):

    type_changed = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.selected_kind = "income"
        self._animation = None

        self.setObjectName(
            "transaction_type_selector"
        )

        self.setFixedHeight(44)

        self.indicator = QFrame(self)

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

        self.income_button.setCheckable(True)
        self.expense_button.setCheckable(True)

        self.income_button.setChecked(True)

        self.type_group = QButtonGroup(self)

        self.type_group.setExclusive(True)

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

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.update_layout(animated=False)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_layout(animated=False)

    def update_layout(
        self,
        animated: bool = True,
    ) -> None:
        margin = 1

        available_width = (
            self.width() - 2 * margin
        )

        button_width = (
            available_width // 2
        )

        button_height = (
            self.height() - 2 * margin
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

        self.update_layout(animated=True)

        self.type_changed.emit(kind)


# =========================================================
# Add Transaction Dialog
# =========================================================

class AddTransactionDialog(QWidget):

    finished = Signal()

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

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
            "dialog_title"
        )

        subtitle = QLabel(
            "Record an income or expense and assign it to an account."
        )

        subtitle.setObjectName(
            "dialog_subtitle"
        )

        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addSpacing(5)
        layout.addWidget(subtitle)

        layout.addSpacing(24)

        # -------------------------------------------------
        # Transaction
        # -------------------------------------------------

        transaction_title = QLabel(
            "Transaction"
        )

        transaction_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            transaction_title
        )

        layout.addSpacing(14)

        # -------------------------------------------------
        # Type
        # -------------------------------------------------

        type_label = QLabel("Type")

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

        type_layout.setSpacing(7)

        type_layout.addWidget(type_label)
        type_layout.addWidget(
            self.type_input
        )

        layout.addWidget(
            type_container
        )

        layout.addSpacing(15)

        # -------------------------------------------------
        # Grid
        # -------------------------------------------------

        fields_grid = QGridLayout()

        fields_grid.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        fields_grid.setHorizontalSpacing(14)
        fields_grid.setVerticalSpacing(15)

        # -------------------------------------------------
        # Amount
        # -------------------------------------------------

        amount_container = (
            self.create_field_container(
                "Amount"
            )
        )

        self.amount_input = QLineEdit()

        self.amount_input.setPlaceholderText(
            "0.00"
        )

        self.amount_input.setFixedHeight(42)

        amount_container.layout().addWidget(
            self.amount_input
        )

        # -------------------------------------------------
        # Date
        # -------------------------------------------------

        date_container = (
            self.create_field_container(
                "Date"
            )
        )

        self.date_input = OctumoDateEdit()

        date_container.layout().addWidget(
            self.date_input
        )

        # -------------------------------------------------
        # Account
        # -------------------------------------------------

        account_container = (
            self.create_field_container(
                "Account"
            )
        )

        self.account_input = ModernComboBox()

        account_container.layout().addWidget(
            self.account_input
        )

        # -------------------------------------------------
        # Category
        # -------------------------------------------------

        category_container = (
            self.create_field_container(
                "Category"
            )
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

        fields_grid.setColumnStretch(0, 1)
        fields_grid.setColumnStretch(1, 1)

        layout.addLayout(
            fields_grid
        )

        layout.addSpacing(23)

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

        layout.addWidget(separator)

        layout.addSpacing(21)

        # -------------------------------------------------
        # Details
        # -------------------------------------------------

        details_title = QLabel(
            "Details"
        )

        details_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            details_title
        )

        layout.addSpacing(13)

        # -------------------------------------------------
        # Note
        # -------------------------------------------------

        note_container = (
            self.create_field_container(
                "Note"
            )
        )

        self.note_input = QLineEdit()

        self.note_input.setPlaceholderText(
            "Optional note"
        )

        self.note_input.setFixedHeight(42)

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
            "dialog_error"
        )

        self.error_label.setWordWrap(True)
        self.error_label.hide()

        layout.addSpacing(10)

        layout.addWidget(
            self.error_label
        )

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        layout.addSpacing(20)

        buttons_layout = QHBoxLayout()

        buttons_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        buttons_layout.setSpacing(10)
        buttons_layout.addStretch()

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.cancel_button.setObjectName(
            "dialog_cancel_button"
        )

        self.cancel_button.setFixedHeight(42)

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

        self.save_button.setFixedHeight(42)
        self.save_button.setMinimumWidth(145)

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

            QLabel#dialog_error {
                color: #DC2626;
                font-size: 13px;
                font-weight: 500;
            }
            """
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

        container_layout.setSpacing(7)

        label = QLabel(label_text)

        label.setObjectName(
            "field_label"
        )

        container_layout.addWidget(label)

        return container

    # =====================================================
    # Accounts
    # =====================================================

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

    # =====================================================
    # Categories
    # =====================================================

    def load_categories(self) -> None:

        self.category_input.clear()

        kind = self.type_input.selected_kind

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

    # =====================================================
    # Save
    # =====================================================

    def save_transaction(self) -> None:

        self.error_label.hide()

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
            amount * Decimal("100")
        )

        if amount_cents <= 0:
            self.show_error(
                "Amount must be greater than zero."
            )

            self.amount_input.setFocus()
            return

        transaction_date = (
            self.date_input
            .date()
            .toString("yyyy-MM-dd")
        )

        note = (
            self.note_input
            .text()
            .strip()
        )

        kind = (
            self.type_input.selected_kind
        )

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

    # =====================================================
    # Close
    # =====================================================

    def close_dialog(self) -> None:
        self.finished.emit()