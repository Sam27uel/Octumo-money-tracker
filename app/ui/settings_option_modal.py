from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QWidget,
)

from app.ui.modal import Modal


# =========================================================
# Selection circle
# =========================================================


class SelectionCircle(QWidget):

    def __init__(
        self,
        selected: bool = False,
        parent=None,
    ) -> None:

        super().__init__(parent)

        self.selected = selected

        self.setFixedSize(
            20,
            20,
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

    # =====================================================
    # Set selected
    # =====================================================

    def set_selected(
        self,
        selected: bool,
    ) -> None:

        self.selected = selected

        self.update()

    # =====================================================
    # Paint
    # =====================================================

    def paintEvent(
        self,
        event,
    ) -> None:

        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        # -------------------------------------------------
        # Selected
        # -------------------------------------------------

        if self.selected:

            painter.setBrush(
                QColor("#2563EB")
            )

            painter.drawEllipse(
                1,
                1,
                18,
                18,
            )

            # White inner dot

            painter.setBrush(
                QColor("#FFFFFF")
            )

            painter.drawEllipse(
                6,
                6,
                8,
                8,
            )

        # -------------------------------------------------
        # Not selected
        # -------------------------------------------------

        else:

            painter.setBrush(
                QColor("#FFFFFF")
            )

            painter.setPen(
                QPen(
                    QColor("#CBD5E1"),
                    1.6,
                )
            )

            painter.drawEllipse(
                2,
                2,
                16,
                16,
            )


# =========================================================
# Option row
# =========================================================


class SettingsOptionRow(QFrame):

    clicked = Signal()

    def __init__(
        self,
        text: str,
        selected: bool = False,
        parent=None,
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            "settings_option_row"
        )

        # IMPORTANT:
        # This forces Qt to actually paint the
        # background/border of the rounded bubble.

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.setFixedHeight(
            50
        )

        self.selected = selected

        # =================================================
        # Layout
        # =================================================

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            16,
            0,
            14,
            0,
        )

        layout.setSpacing(
            10
        )

        # =================================================
        # Text
        # =================================================

        self.text_label = QLabel(
            text
        )

        self.text_label.setObjectName(
            "settings_option_text"
        )

        self.text_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        layout.addWidget(
            self.text_label
        )

        layout.addStretch()

        # =================================================
        # Selector
        # =================================================

        self.selector = SelectionCircle(
            selected=selected
        )

        layout.addWidget(
            self.selector
        )

        self.update_visual_state()

    # =====================================================
    # Update visual state
    # =====================================================

    def update_visual_state(self) -> None:

        if self.selected:

            background_color = "#F8FBFF"
            border_color = "#93C5FD"

        else:

            background_color = "#FFFFFF"
            border_color = "#E2E8F0"

        self.setStyleSheet(
            f"""
            QFrame#settings_option_row {{
                background-color: {background_color};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}

            QFrame#settings_option_row:hover {{
                background-color: #F8FAFC;
                border-color: #CBD5E1;
            }}

            QLabel#settings_option_text {{
                background-color: transparent;
                color: #0F172A;
                font-size: 14px;
                font-weight: 600;
            }}
            """
        )

    # =====================================================
    # Set selected
    # =====================================================

    def set_selected(
        self,
        selected: bool,
    ) -> None:

        self.selected = selected

        self.selector.set_selected(
            selected
        )

        self.update_visual_state()

    # =====================================================
    # Click
    # =====================================================

    def mousePressEvent(
        self,
        event,
    ) -> None:

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):

            self.clicked.emit()

        super().mousePressEvent(
            event
        )


# =========================================================
# Settings Option Modal
# =========================================================


class SettingsOptionModal(Modal):

    def __init__(
        self,
        title: str,
        subtitle: str,
        options: list[str],
        current_value: str,
        parent=None,
    ) -> None:

        super().__init__(
            title=title,
            subtitle=subtitle,
            primary_text="Save",
            cancel_text="Cancel",
            parent=parent,
        )

        # =================================================
        # Values
        # =================================================

        self.current_value = current_value

        self.selected_value = current_value

        self.option_rows = []

        # =================================================
        # Modal styling
        # =================================================

        self.setStyleSheet(
            """
            QWidget#modal_content {
                background-color: transparent;
            }

            QLabel#modal_title {
                background-color: transparent;
                color: #0F172A;
                font-size: 24px;
                font-weight: 700;
            }

            QLabel#modal_subtitle {
                background-color: transparent;
                color: #64748B;
                font-size: 14px;
            }

            QLabel#field_label {
                background-color: transparent;
                color: #334155;
                font-size: 13px;
                font-weight: 600;
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

            QPushButton#modal_primary_button:pressed {
                background-color: #334155;
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

            QPushButton#modal_cancel_button:pressed {
                background-color: #F1F5F9;
            }
            """
        )

        # =================================================
        # Options container
        # =================================================

        options_container = QWidget()

        options_container.setObjectName(
            "settings_options_container"
        )

        options_layout = QVBoxLayout(
            options_container
        )

        options_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        options_layout.setSpacing(
            8
        )

        # =================================================
        # Create bubbles
        # =================================================

        for option in options:

            row = SettingsOptionRow(
                text=option,
                selected=(
                    option == current_value
                ),
            )

            row.clicked.connect(
                lambda value=option:
                self.select_option(value)
            )

            self.option_rows.append(
                (
                    option,
                    row,
                )
            )

            options_layout.addWidget(
                row
            )

        self.add_content(
            options_container
        )

        # =================================================
        # Save
        # =================================================

        self.submitted.connect(
            self.handle_submit
        )

    # =====================================================
    # Select option
    # =====================================================

    def select_option(
        self,
        value: str,
    ) -> None:

        self.selected_value = value

        for option, row in self.option_rows:

            row.set_selected(
                option == value
            )

    # =====================================================
    # Save
    # =====================================================

    def handle_submit(
        self,
    ) -> None:

        if not self.selected_value:
            return

        # Existing Octumo modal system closes the modal
        # through the cancelled signal.

        self.cancelled.emit()