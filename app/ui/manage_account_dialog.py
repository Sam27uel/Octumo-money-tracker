from datetime import date

from PySide6.QtCore import Qt, QRegularExpression, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.account_service import (
    add_balance_adjustment,
    archive_account,
    delete_account_permanently,
    get_current_balance,
    rename_account,
    restore_account,
)

from app.ui.modal import Modal


class ManageAccountDialog(QWidget):
    finished = Signal()

    def __init__(
        self,
        account_id: int,
        account_name: str,
        is_active: bool,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.account_id = account_id
        self.account_name = account_name
        self.is_active = is_active

        self.build_ui()

    # =========================================================
    # MAIN UI
    # =========================================================

    def build_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(0)

        # -----------------------------------------------------
        # Title
        # -----------------------------------------------------

        title = QLabel("Manage account")
        title.setObjectName("manage_title")

        layout.addWidget(title)

        # -----------------------------------------------------
        # Subtitle
        # -----------------------------------------------------

        subtitle = QLabel(
            f"Manage settings and balance for {self.account_name}."
        )

        subtitle.setObjectName(
            "manage_subtitle"
        )

        subtitle.setWordWrap(True)

        layout.addSpacing(6)
        layout.addWidget(subtitle)

        # -----------------------------------------------------
        # Balance section
        # -----------------------------------------------------

        layout.addSpacing(28)

        balance_section_title = QLabel(
            "Balance"
        )

        balance_section_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            balance_section_title
        )

        layout.addSpacing(12)

        current_balance = get_current_balance(
            self.account_id
        )

        balance_row = self.create_action_row(
            title="Current balance",
            description=(
                "The current balance recorded for this account."
            ),
            value=self.format_money(
                current_balance
            ),
            button_text="Adjust",
            button_object_name="secondary_button",
            callback=self.adjust_balance,
        )

        layout.addWidget(
            balance_row
        )

        # -----------------------------------------------------
        # Separator
        # -----------------------------------------------------

        layout.addSpacing(20)

        separator_1 = self.create_separator()

        layout.addWidget(
            separator_1
        )

        # -----------------------------------------------------
        # Account section
        # -----------------------------------------------------

        layout.addSpacing(20)

        account_section_title = QLabel(
            "Account"
        )

        account_section_title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            account_section_title
        )

        layout.addSpacing(12)

        # -----------------------------------------------------
        # Rename
        # -----------------------------------------------------

        rename_row = self.create_action_row(
            title="Rename account",
            description=(
                "Change the name used to identify this account."
            ),
            button_text="Rename",
            button_object_name="secondary_button",
            callback=self.rename,
        )

        layout.addWidget(
            rename_row
        )

        layout.addSpacing(12)

        # -----------------------------------------------------
        # Archive / Restore
        # -----------------------------------------------------

        if self.is_active:
            archive_row = self.create_action_row(
                title="Archive account",
                description=(
                    "Hide this account from your active accounts."
                ),
                button_text="Archive",
                button_object_name="secondary_button",
                callback=self.archive,
            )
        else:
            archive_row = self.create_action_row(
                title="Restore account",
                description=(
                    "Return this account to your active accounts."
                ),
                button_text="Restore",
                button_object_name="secondary_button",
                callback=self.restore,
            )

        layout.addWidget(
            archive_row
        )

        # -----------------------------------------------------
        # Separator
        # -----------------------------------------------------

        layout.addSpacing(20)

        separator_2 = self.create_separator()

        layout.addWidget(
            separator_2
        )

        # -----------------------------------------------------
        # Danger zone
        # -----------------------------------------------------

        layout.addSpacing(20)

        danger_title = QLabel(
            "Danger zone"
        )

        danger_title.setObjectName(
            "danger_title"
        )

        layout.addWidget(
            danger_title
        )

        layout.addSpacing(10)

        delete_row = self.create_action_row(
            title="Delete account",
            description=(
                "Permanently delete this account and its data."
            ),
            button_text="Delete",
            button_object_name="danger_button",
            callback=self.delete_permanently,
        )

        layout.addWidget(
            delete_row
        )

        # -----------------------------------------------------
        # Close button
        # -----------------------------------------------------

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

        close_button = QPushButton(
            "Close"
        )

        close_button.setObjectName(
            "secondary_button"
        )

        close_button.setFixedSize(
            100,
            42,
        )

        close_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        close_button.clicked.connect(
            self.close_modal
        )

        bottom_layout.addWidget(
            close_button
        )

        layout.addLayout(
            bottom_layout
        )

        # -----------------------------------------------------
        # Styling
        # -----------------------------------------------------

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

            QLabel#row_title {
                color: #334155;
                font-size: 14px;
                font-weight: 600;
            }

            QLabel#row_description {
                color: #64748B;
                font-size: 13px;
            }

            QLabel#row_value {
                color: #0F172A;
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#separator {
                background-color: #E2E8F0;
            }

            QLabel#danger_title {
                color: #B91C1C;
                font-size: 16px;
                font-weight: 700;
            }

            QPushButton#secondary_button {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 16px;
                text-align: left;
            }

            QPushButton#secondary_button:hover {
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #94A3B8;
            }

            QPushButton#secondary_button:pressed {
                background-color: #F1F5F9;
            }

            QPushButton#danger_button {
                background-color: #FFFFFF;
                color: #B91C1C;
                border: 1px solid #FCA5A5;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 16px;
                text-align: left;
            }

            QPushButton#danger_button:hover {
                background-color: #FEF2F2;
                color: #991B1B;
                border: 1px solid #F87171;
            }

            QPushButton#danger_button:pressed {
                background-color: #FEE2E2;
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
            """
        )

    # =========================================================
    # ACTION ROW
    # =========================================================

    def create_action_row(
        self,
        title: str,
        description: str,
        button_text: str,
        button_object_name: str,
        callback,
        value: str | None = None,
    ) -> QWidget:
        row = QWidget()

        row_layout = QHBoxLayout(
            row
        )

        row_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        row_layout.setSpacing(
            12
        )

        # -----------------------------------------------------
        # Left side
        # -----------------------------------------------------

        text_layout = QVBoxLayout()

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text_layout.setSpacing(
            3
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "row_title"
        )

        description_label = QLabel(
            description
        )

        description_label.setObjectName(
            "row_description"
        )

        description_label.setWordWrap(
            True
        )

        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            description_label
        )

        row_layout.addLayout(
            text_layout,
            1,
        )

        # -----------------------------------------------------
        # Right side
        # -----------------------------------------------------

        if value is not None:
            value_label = QLabel(
                value
            )

            value_label.setObjectName(
                "row_value"
            )

            value_label.setAlignment(
                Qt.AlignmentFlag.AlignVCenter
                | Qt.AlignmentFlag.AlignRight
            )

            row_layout.addWidget(
                value_label
            )

        button = QPushButton(
            button_text
        )

        button.setObjectName(
            button_object_name
        )

        button.setFixedSize(
            105,
            42,
        )

        button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        button.clicked.connect(
            callback
        )

        row_layout.addWidget(
            button
        )

        return row

    # =========================================================
    # SEPARATOR
    # =========================================================

    def create_separator(
        self,
    ) -> QWidget:
        separator = QLabel()

        separator.setObjectName(
            "separator"
        )

        separator.setFixedHeight(
            1
        )

        return separator

    # =========================================================
    # MONEY
    # =========================================================

    @staticmethod
    def format_money(
        amount_cents: int,
    ) -> str:
        amount = amount_cents / 100

        return f"{amount:,.2f} €".replace(
            ",",
            " ",
        )

    # =========================================================
    # ERROR
    # =========================================================

    def show_error(
        self,
        message: str,
    ) -> None:
        modal = Modal(
            title="Something went wrong",
            subtitle=message,
            primary_text="OK",
            cancel_text="",
        )

        modal.cancel_button.hide()

        modal.primary_button.setFixedSize(
            90,
            42,
        )

        modal.primary_button.clicked.connect(
            self.close_nested_modal
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    def close_nested_modal(
        self,
    ) -> None:
        self.window().close_modal()

    # =========================================================
    # RENAME
    # =========================================================

    def rename(
        self,
    ) -> None:
        modal = Modal(
            title="Rename account",
            subtitle=(
                "Enter a new name for this account."
            ),
            primary_text="Rename",
        )

        name_input = QLineEdit()

        name_input.setText(
            self.account_name
        )

        name_input.setPlaceholderText(
            "e.g. Revolut"
        )

        name_input.setMinimumHeight(
            44
        )

        modal.add_content(
            self.create_form_field(
                "Account name",
                name_input,
            )
        )

        def save_name() -> None:
            new_name = (
                name_input.text()
                .strip()
            )

            if not new_name:
                self.window().close_modal()

                self.show_error(
                    "Account name cannot be empty."
                )

                return

            try:
                rename_account(
                    self.account_id,
                    new_name,
                )
            except Exception:
                self.window().close_modal()

                self.show_error(
                    "This account name may already be in use."
                )

                return

            self.account_name = new_name

            self.window().close_modal()

            self.close_modal()

        modal.submitted.connect(
            save_name
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    # =========================================================
    # ADJUST BALANCE
    # =========================================================

    def adjust_balance(
        self,
    ) -> None:
        current_balance = get_current_balance(
            self.account_id
        )

        current_balance_text = (
            f"{current_balance / 100:.2f}"
        )

        modal = Modal(
            title="Adjust balance",
            subtitle=(
                "Enter the actual balance of the account."
            ),
            primary_text="Adjust balance",
        )

        balance_input = QLineEdit()

        balance_input.setText(
            current_balance_text
        )

        balance_input.setMinimumHeight(
            44
        )

        balance_input.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        balance_validator = (
            QRegularExpressionValidator(
                QRegularExpression(
                    r"^-?\d{0,10}([.,]\d{0,2})?$"
                )
            )
        )

        balance_input.setValidator(
            balance_validator
        )

        note_input = QLineEdit()

        note_input.setPlaceholderText(
            "e.g. Cash withdrawal"
        )

        note_input.setMinimumHeight(
            44
        )

        modal.add_content(
            self.create_form_field(
                "Actual balance",
                balance_input,
            )
        )

        modal.add_content(
            self.create_form_field(
                "Note",
                note_input,
            )
        )

        def save_adjustment() -> None:
            balance_text = (
                balance_input.text()
                .strip()
                .replace(",", ".")
            )

            if not balance_text:
                self.window().close_modal()

                self.show_error(
                    "Please enter a valid balance."
                )

                return

            try:
                actual_balance_cents = round(
                    float(balance_text) * 100
                )
            except ValueError:
                self.window().close_modal()

                self.show_error(
                    "Please enter a valid balance."
                )

                return

            adjustment_cents = (
                actual_balance_cents
                - current_balance
            )

            if adjustment_cents == 0:
                self.window().close_modal()

                self.show_error(
                    "The balance is already set to this amount."
                )

                return

            add_balance_adjustment(
                account_id=self.account_id,
                amount_cents=adjustment_cents,
                adjustment_date=date.today().isoformat(),
                note=note_input.text().strip(),
            )

            self.window().close_modal()

            self.close_modal()

        modal.submitted.connect(
            save_adjustment
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    # =========================================================
    # ARCHIVE
    # =========================================================

    def archive(
        self,
    ) -> None:
        modal = Modal(
            title="Archive account",
            subtitle=(
                f"Are you sure you want to archive "
                f"{self.account_name}?"
            ),
            primary_text="Archive",
        )

        def confirm_archive() -> None:
            archive_account(
                self.account_id
            )

            self.window().close_modal()

            self.close_modal()

        modal.submitted.connect(
            confirm_archive
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    # =========================================================
    # RESTORE
    # =========================================================

    def restore(
        self,
    ) -> None:
        modal = Modal(
            title="Restore account",
            subtitle=(
                f"Restore {self.account_name} "
                "to your active accounts?"
            ),
            primary_text="Restore",
        )

        def confirm_restore() -> None:
            restore_account(
                self.account_id
            )

            self.window().close_modal()

            self.close_modal()

        modal.submitted.connect(
            confirm_restore
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    # =========================================================
    # DELETE
    # =========================================================

    def delete_permanently(
        self,
    ) -> None:
        modal = Modal(
            title="Delete account",
            subtitle=(
                f"Are you sure you want to permanently "
                f"delete {self.account_name}?"
            ),
            primary_text="Continue",
        )

        modal.submitted.connect(
            self.delete_second_confirmation
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    def delete_second_confirmation(
        self,
    ) -> None:
        modal = Modal(
            title="Permanently delete account?",
            subtitle=(
                "This action cannot be undone. "
                "All transactions and balance adjustments "
                "for this account will be permanently deleted."
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
            self.confirm_delete
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    def confirm_delete(
        self,
    ) -> None:
        delete_account_permanently(
            self.account_id
        )

        # Close second confirmation.
        self.window().close_modal()

        # Close first confirmation.
        self.window().close_modal()

        # Close Manage Account.
        self.close_modal()

    # =========================================================
    # FORM FIELD
    # =========================================================

    def create_form_field(
        self,
        label_text: str,
        input_widget: QWidget,
    ) -> QWidget:
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
            18
        )

        label = QLabel(
            label_text
        )

        label.setObjectName(
            "form_label"
        )

        label.setFixedWidth(
            120
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

        return container

    # =========================================================
    # CLOSE
    # =========================================================

    def close_modal(
        self,
    ) -> None:
        self.finished.emit()

        self.window().close_modal()