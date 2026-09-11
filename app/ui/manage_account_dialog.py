from datetime import date

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.services.account_service import (
    add_balance_adjustment,
    archive_account,
    delete_account_permanently,
    get_current_balance,
    rename_account,
    restore_account,
)


class ManageAccountDialog(QDialog):
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

        self.setWindowTitle("Manage account")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Account header
        title = QLabel(account_name)
        title.setStyleSheet(
            """
            font-size: 22px;
            font-weight: 700;
            """
        )

        layout.addWidget(title)

        # Balance section
        balance_group = QGroupBox("Balance")
        balance_layout = QVBoxLayout(balance_group)

        current_balance = get_current_balance(account_id)

        balance_label = QLabel(
            f"{current_balance / 100:.2f} €"
        )
        balance_label.setStyleSheet(
            """
            font-size: 24px;
            font-weight: 700;
            """
        )

        balance_layout.addWidget(QLabel("Current balance"))
        balance_layout.addWidget(balance_label)

        adjust_button = QPushButton("Adjust balance")
        adjust_button.clicked.connect(self.adjust_balance)

        balance_layout.addWidget(adjust_button)

        layout.addWidget(balance_group)

        # Account section
        account_group = QGroupBox("Account")
        account_layout = QVBoxLayout(account_group)

        rename_button = QPushButton("Rename account")
        rename_button.clicked.connect(self.rename)

        account_layout.addWidget(rename_button)

        if self.is_active:
            archive_button = QPushButton("Archive account")
            archive_button.clicked.connect(self.archive)

            account_layout.addWidget(archive_button)

        else:
            restore_button = QPushButton("Restore account")
            restore_button.clicked.connect(self.restore)

            account_layout.addWidget(restore_button)

        layout.addWidget(account_group)

        # Danger zone
        danger_group = QGroupBox("Danger zone")
        danger_layout = QVBoxLayout(danger_group)

        danger_label = QLabel(
            "Permanently deleting an account also deletes all "
            "transactions associated with it."
        )
        danger_label.setWordWrap(True)

        danger_layout.addWidget(danger_label)

        delete_button = QPushButton("Delete account permanently")
        delete_button.setStyleSheet(
            """
            QPushButton {
                color: #B91C1C;
                border: 1px solid #FCA5A5;
                background-color: #FEF2F2;
            }

            QPushButton:hover {
                background-color: #FEE2E2;
            }
            """
        )
        delete_button.clicked.connect(self.delete_permanently)

        danger_layout.addWidget(delete_button)

        layout.addWidget(danger_group)

        # Bottom buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )

        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

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
        self.accept()

    def adjust_balance(self) -> None:
        current_balance = get_current_balance(
            self.account_id
        )

        current_balance_euros = current_balance / 100

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

        actual_balance_cents = round(amount * 100)

        adjustment_cents = (
            actual_balance_cents - current_balance
        )

        if adjustment_cents == 0:
            QMessageBox.information(
                self,
                "No adjustment needed",
                "The actual balance already matches the "
                "calculated balance.",
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

        self.accept()

    def archive(self) -> None:
        answer = QMessageBox.question(
            self,
            "Archive account",
            (
                f"Archive '{self.account_name}'?\n\n"
                "The account and its transaction history "
                "will remain available, but the account will "
                "no longer be active."
            ),
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            archive_account(self.account_id)

        except Exception as error:
            QMessageBox.warning(
                self,
                "Could not archive account",
                f"Could not archive account:\n\n{error}",
            )
            return

        self.accept()

    def restore(self) -> None:
        try:
            restore_account(self.account_id)

        except Exception as error:
            QMessageBox.warning(
                self,
                "Could not restore account",
                f"Could not restore account:\n\n{error}",
            )
            return

        self.accept()

    def delete_permanently(self) -> None:
        first_confirmation = QMessageBox.question(
            self,
            "Delete account permanently",
            (
                f"Are you sure you want to permanently delete "
                f"'{self.account_name}'?\n\n"
                "All transactions and balance adjustments "
                "belonging to this account will also be deleted."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if first_confirmation != QMessageBox.StandardButton.Yes:
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

        if second_confirmation != QMessageBox.StandardButton.Yes:
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

        self.accept()