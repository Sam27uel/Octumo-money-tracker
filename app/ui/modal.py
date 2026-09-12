from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class Modal(QWidget):
    submitted = Signal()
    cancelled = Signal()

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        primary_text: str = "Save",
        cancel_text: str = "Cancel",
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("modal_content")

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(0)

        # =================================================
        # Title
        # =================================================

        title_label = QLabel(title)

        title_label.setObjectName(
            "modal_title"
        )

        layout.addWidget(
            title_label
        )

        # =================================================
        # Subtitle
        # =================================================

        if subtitle:
            subtitle_label = QLabel(
                subtitle
            )

            subtitle_label.setObjectName(
                "modal_subtitle"
            )

            subtitle_label.setWordWrap(
                True
            )

            layout.addSpacing(6)

            layout.addWidget(
                subtitle_label
            )

        # =================================================
        # Content
        # =================================================

        self.content_layout = QVBoxLayout()

        self.content_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        self.content_layout.setSpacing(
            16
        )

        layout.addSpacing(
            28
        )

        layout.addLayout(
            self.content_layout
        )

        # =================================================
        # Buttons
        # =================================================

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
            cancel_text
        )

        self.cancel_button.setObjectName(
            "modal_cancel_button"
        )

        self.cancel_button.setFixedHeight(
            42
        )

        self.cancel_button.clicked.connect(
            self.cancel
        )

        buttons_layout.addWidget(
            self.cancel_button
        )

        self.primary_button = QPushButton(
            primary_text
        )

        self.primary_button.setObjectName(
            "modal_primary_button"
        )

        self.primary_button.setFixedHeight(
            42
        )

        self.primary_button.clicked.connect(
            self.submit
        )

        buttons_layout.addWidget(
            self.primary_button
        )

        layout.addSpacing(
            28
        )

        layout.addLayout(
            buttons_layout
        )

        # =================================================
        # Styling
        # =================================================

        self.setStyleSheet(
            """
            QWidget#modal_content {
                background-color: transparent;
            }

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

            QLineEdit {
                background-color: #F8FAFC;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 14px;
                selection-background-color: #CBD5E1;
                selection-color: #0F172A;
            }

            QLineEdit:focus {
                background-color: #FFFFFF;
                border: 1px solid #64748B;
            }

            QLineEdit::placeholder {
                color: #94A3B8;
            }

            QWidget#balance_card {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }

            QLabel#balance_value {
                color: #0F172A;
                font-size: 22px;
                font-weight: 700;
            }

            QWidget#action_row {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }

            QLabel#action_title {
                color: #0F172A;
                font-size: 14px;
                font-weight: 600;
            }

            QLabel#action_description {
                color: #64748B;
                font-size: 12px;
            }

            QPushButton#modal_primary_button {
                background-color: #0F172A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 16px;
                min-width: 88px;
            }

            QPushButton#modal_primary_button:hover {
                background-color: #1E293B;
            }

            QPushButton#modal_secondary_button {
                background-color: #FFFFFF;
                color: #334155;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                padding: 0 14px;
                min-width: 90px;
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
                padding: 0 16px;
                min-width: 80px;
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
                font-size: 13px;
                font-weight: 500;
                padding: 0 14px;
                min-width: 90px;
            }

            QPushButton#danger_button:hover {
                background-color: #FEF2F2;
            }
            """
        )

    # =================================================
    # Content helpers
    # =================================================

    def add_content(
        self,
        widget: QWidget,
    ) -> None:
        self.content_layout.addWidget(
            widget
        )

    def add_spacing(
        self,
        spacing: int,
    ) -> None:
        self.content_layout.addSpacing(
            spacing
        )

    # =================================================
    # Actions
    # =================================================

    def submit(self) -> None:
        self.submitted.emit()

    def cancel(self) -> None:
        self.cancelled.emit()