from PySide6.QtCore import QRegularExpression, Signal
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class AddAccountDialog(QWidget):
    submitted = Signal()
    cancelled = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # -------------------------------------------------
        # Title
        # -------------------------------------------------

        title = QLabel("Add account")
        title.setObjectName("modal_title")

        layout.addWidget(title)

        # -------------------------------------------------
        # Subtitle
        # -------------------------------------------------

        subtitle = QLabel(
            "Add a new account to track your money."
        )
        subtitle.setObjectName("modal_subtitle")
        subtitle.setWordWrap(True)

        layout.addSpacing(6)
        layout.addWidget(subtitle)

        # -------------------------------------------------
        # Form
        # -------------------------------------------------

        form_layout = QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setHorizontalSpacing(18)
        form_layout.setVerticalSpacing(18)

        # Account name
        name_label = QLabel("Account name")
        name_label.setObjectName("field_label")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Revolut")
        self.name_input.setMinimumHeight(44)

        form_layout.addRow(
            name_label,
            self.name_input,
        )

        # Starting balance
        balance_label = QLabel("Starting balance")
        balance_label.setObjectName("field_label")

        self.balance_input = QLineEdit()
        self.balance_input.setPlaceholderText("0.00 €")
        self.balance_input.setMinimumHeight(44)

        # Allow only:
        # 123
        # 123.4
        # 123.45
        # 123,4
        # 123,45
        #
        # Maximum of two decimal places.
        balance_validator = QRegularExpressionValidator(
            QRegularExpression(
                r"^\d{0,10}([.,]\d{0,2})?$"
            )
        )

        self.balance_input.setValidator(
            balance_validator
        )

        form_layout.addRow(
            balance_label,
            self.balance_input,
        )

        layout.addSpacing(28)
        layout.addLayout(form_layout)

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        buttons_layout.setSpacing(10)

        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName(
            "modal_cancel_button"
        )
        cancel_button.setFixedSize(100, 42)

        cancel_button.clicked.connect(
            self.cancel
        )

        add_button = QPushButton("Add account")
        add_button.setObjectName(
            "modal_primary_button"
        )
        add_button.setFixedSize(125, 42)

        add_button.clicked.connect(
            self.submit
        )

        buttons_layout.addWidget(
            cancel_button
        )

        buttons_layout.addWidget(
            add_button
        )

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

            QLabel#field_label {
                color: #334155;
                font-size: 13px;
                font-weight: 600;
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

            QPushButton#modal_primary_button {
                background-color: #0F172A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 0;
                text-align: center;
            }

            QPushButton#modal_primary_button:hover {
                background-color: #1E293B;
            }

            QPushButton#modal_cancel_button {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0;
                text-align: center;
            }

            QPushButton#modal_cancel_button:hover {
                background-color: #F8FAFC;
                color: #0F172A;
            }
            """
        )

    def get_data(self) -> tuple[str, int]:
        name = self.name_input.text().strip()

        balance_text = (
            self.balance_input.text()
            .strip()
            .replace(",", ".")
        )

        if not balance_text:
            balance_text = "0"

        try:
            balance_cents = round(
                float(balance_text) * 100
            )
        except ValueError:
            balance_cents = 0

        return name, balance_cents

    def submit(self) -> None:
        self.submitted.emit()

    def cancel(self) -> None:
        self.cancelled.emit()