from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QDoubleSpinBox,
    QDialogButtonBox,
)


class AddAccountDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Add account")
        self.setMinimumWidth(350)

        layout = QFormLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Revolut")

        self.balance_input = QDoubleSpinBox()
        self.balance_input.setRange(0, 1_000_000_000)
        self.balance_input.setDecimals(2)
        self.balance_input.setSuffix(" €")

        layout.addRow("Account name:", self.name_input)
        layout.addRow("Starting balance:", self.balance_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)

    def get_data(self) -> tuple[str, int]:
        name = self.name_input.text().strip()
        balance_cents = round(self.balance_input.value() * 100)

        return name, balance_cents