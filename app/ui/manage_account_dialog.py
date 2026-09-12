from datetime import date

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        title = QLabel("Manage account")
        title.setObjectName("modal_title")

        layout.addWidget(title)

        subtitle = QLabel(
            f"Manage settings and balance for {account_name}."
        )
        subtitle.setObjectName("modal_subtitle")
        subtitle.setWordWrap(True)

        layout.addSpacing(6)
        layout.addWidget(subtitle)

        # -------------------------------------------------
        # Current balance
        # -------------------------------------------------

        layout.addSpacing(26)

        balance_section = QLabel("Current balance")
        balance_section.setObjectName("section_label")

        layout.addWidget(balance_section)

        current_balance = get_current_balance(
            account_id
        )

        balance_card = QWidget()
        balance_card.setObjectName("balance_card")

        balance_layout = QHBoxLayout(balance_card)
        balance_layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        balance_value = QLabel(
            f"{current_balance / 100:.2f} €"
        )
        balance_value.setObjectName("balance_value")

        balance_layout.addWidget(balance_value)
        balance_layout.addStretch()

        layout.addSpacing(8)
        layout.addWidget(balance_card)

        # Adjust balance
        adjust_button = QPushButton(
            "Adjust balance"
        )
        adjust_button.setObjectName(
            "modal_secondary_button"
        )
        adjust_button.setFixedHeight(42)

        adjust_button.clicked.connect(
            self.adjust_balance
        )

        layout.addSpacing(10)
        layout.addWidget(adjust_button)

        # -------------------------------------------------
        # Account
        # -------------------------------------------------

        layout.addSpacing(24)

        account_section = QLabel("Account")
        account_section.setObjectName(
            "section_label"
        )

        layout.addWidget(account_section)

        layout.addSpacing(8)

        # Rename
        rename_button = QPushButton(
            "Rename account"
        )
        rename_button.setObjectName(
            "modal_secondary_button"
        )
        rename_button.setFixedHeight(42)

        rename_button.clicked.connect(
            self.rename
        )

        layout.addWidget(rename_button)

        layout.addSpacing(8)

        # Archive / Restore
        if self.is_active:
            archive_button = QPushButton(
                "Archive account"
            )
            archive_button.setObjectName(
                "modal_secondary_button"
            )
            archive_button.setFixedHeight(42)

            archive_button.clicked.connect(
                self.archive
            )

            layout.addWidget(archive_button)

        else:
            restore_button = QPushButton(
                "Restore account"
            )
            restore_button.setObjectName(
                "modal_primary_button"
            )
            restore_button.setFixedHeight(42)

            restore_button.clicked.connect(
                self.restore
            )

            layout.addWidget(restore_button)

        # -------------------------------------------------
        # Danger zone
        # -------------------------------------------------

        layout.addSpacing(24)

        danger_section = QLabel("Danger zone")
        danger_section.setObjectName(
            "danger_section"
        )

        layout.addWidget(danger_section)

        layout.addSpacing(8)

        delete_button = QPushButton(
            "Delete account permanently"
        )
        delete_button.setObjectName(
            "danger_button"
        )
        delete_button.setFixedHeight(42)

        delete_button.clicked.connect(
            self.delete_permanently
        )

        layout.addWidget(delete_button)

        # -------------------------------------------------
        # Close
        # -------------------------------------------------

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        buttons_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.setObjectName(
            "modal_cancel_button"
        )
        close_button.setFixedSize(100, 42)

        close_button.clicked.connect(
            self.close_modal
        )

        buttons_layout.addWidget(close_button)

        layout.addSpacing(28)
        layout.addLayout(buttons_layout)

        # -------------------------------------------------
        # Styling
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QLabel#modal_title {
                color: #0F172A;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#modal_subtitle {
                color: #64748B;
                font-size: 14px;
            }

            QLabel#section_label {
                color: #334155;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#danger_section {
                color: #B91C1C;
                font-size: 13px;
                font-weight: 600;
            }

            QWidget#balance_card {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }

            QLabel#balance_value {
                color: #0F172A;
                font-size: 22px;
                font-weight: 700;
            }

            QPushButton#modal_primary_button {
                background-color: #0F172A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 16px;
            }

            QPushButton#modal_primary_button:hover {
                background-color: #1E293B;
            }

            QPushButton#modal_secondary_button {
                background-color: #FFFFFF;
                color: #334155;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 16px;
            }

            QPushButton#modal_secondary_button:hover {
                background-color: #F8FAFC;
                color: #0F172A;
            }

            QPushButton#modal_cancel_button {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0;
            }

            QPushButton#modal_cancel_button:hover {
                background-color: #F8FAFC;
                color: #0F172A;
            }

            QPushButton#danger_button {
                background-color: #FFFFFF;
                color: #B91C1C;
                border: 1px solid #FCA5A5;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 16px;
            }

            QPushButton#danger_button:hover {
                background-color: #FEF2F2;
            }
            """
        )

    def close_modal(self) -> None:
        self.finished.emit()
        self.window().close_modal()

    def rename(self) -> None:
        new_name, accepted = QInputDialog.getText(
            self,
            "Rename account",
            "Account name:",
            QLineEdit.EchoMode.Normal,
            self.account_name,
        )

        if not accepted:
            return

        new_name = new_name.strip()

        if not new_name:
            QMessageBox.warning(
                self,
                "Invalid name",
                "Account name cannot be empty.",
            )
            return

        try:
            rename_account(
                self.account_id,
                new_name,
            )
        except Exception as error:
            QMessageBox.warning(
                self,
                "Could not rename account",
                f"Could not rename account:\n\n{error}",
            )
            return

        self.account_name = new_name
        self.close_modal()

    def adjust_balance(self) -> None:
        current_balance = get_current_balance(
            self.account_id
        )

        current_balance_euros = (
            current_balance / 100
        )

        amount, accepted = QInputDialog.getDouble(
            self,
            "Adjust balance",
            (
                "Enter the actual balance of the account.\n\n"
                f"Calculated balance: "
                f"{current_balance_euros:.2f} €"
            ),
            current_balance_euros,
            -1_000_000_000,
            1_000_000_000,
            2,
        )

        if not accepted:
            return

        actual_balance_cents = round(
            amount * 100
        )

        adjustment_cents = (
            actual_balance_cents
            - current_balance
        )

        if adjustment_cents == 0:
            QMessageBox.information(
                self,
                "No adjustment needed",
                (
                    "The actual balance already "
                    "matches the calculated balance."
                ),
            )
            return

        note, accepted = QInputDialog.getText(
            self,
            "Adjustment note",
            "Why are you adjusting the balance?",
        )

        if not accepted:
            return

        try:
            add_balance_adjustment(
                account_id=self.account_id,
                amount_cents=adjustment_cents,
                adjustment_date=date.today().isoformat(),
                note=note,
            )
        except Exception as error:
            QMessageBox.warning(
                self,
                "Could not adjust balance",
                f"Could not adjust balance:\n\n{error}",
            )
            return

        QMessageBox.information(
            self,
            "Balance adjusted",
            (
                f"Balance adjusted by "
                f"{adjustment_cents / 100:.2f} €."
            ),
        )

        self.close_modal()

    def archive(self) -> None:
        answer = QMessageBox.question(
            self,
            "Archive account",
            (
                f"Archive '{self.account_name}'?\n\n"
                "The account and its transaction "
                "history will remain available, but "
                "the account will no longer be active."
            ),
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            archive_account(
                self.account_id
            )
        except Exception as error:
            QMessageBox.warning(
                self,
                "Could not archive account",
                f"Could not archive account:\n\n{error}",
            )
            return

        self.close_modal()

    def restore(self) -> None:
        try:
            restore_account(
                self.account_id
            )
        except Exception as error:
            QMessageBox.warning(
                self,
                "Could not restore account",
                f"Could not restore account:\n\n{error}",
            )
            return

        self.close_modal()

    def delete_permanently(self) -> None:
        first_confirmation = QMessageBox.question(
            self,
            "Delete account permanently",
            (
                f"Are you sure you want to permanently "
                f"delete '{self.account_name}'?\n\n"
                "All transactions and balance adjustments "
                "belonging to this account will also be deleted."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if (
            first_confirmation
            != QMessageBox.StandardButton.Yes
        ):
            return

        second_confirmation = QMessageBox.question(
            self,
            "Final confirmation",
            (
                "This action cannot be undone.\n\n"
                "Delete the account permanently?"
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if (
            second_confirmation
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:
            delete_account_permanently(
                self.account_id
            )
        except Exception as error:
            QMessageBox.warning(
                self,
                "Could not delete account",
                f"Could not delete account:\n\n{error}",
            )
            return

        self.close_modal()