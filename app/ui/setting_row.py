from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class SettingRow(QWidget):

    clicked = Signal()

    def __init__(
        self,
        title: str,
        value: str,
        clickable: bool = True,
        parent=None,
    ) -> None:

        super().__init__(parent)

        self.clickable = clickable

        self.setObjectName(
            "setting_row"
        )

        # IMPORTANT:
        # Without this Qt may not paint the
        # background / border of QWidget.
        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        if clickable:
            self.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            18,
            12,
            14,
            12,
        )

        layout.setSpacing(0)

        # =================================================
        # Text
        # =================================================

        text_layout = QVBoxLayout()

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text_layout.setSpacing(3)

        self.title_label = QLabel(
            title
        )

        self.title_label.setObjectName(
            "setting_name"
        )

        self.value_label = QLabel(
            value
        )

        self.value_label.setObjectName(
            "setting_value"
        )

        text_layout.addWidget(
            self.title_label
        )

        text_layout.addWidget(
            self.value_label
        )

        layout.addLayout(
            text_layout
        )

        layout.addStretch()

        # =================================================
        # Arrow
        # =================================================

        self.arrow = QLabel(
            "›" if clickable else ""
        )

        self.arrow.setObjectName(
            "setting_arrow"
        )

        self.arrow.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.arrow.setFixedWidth(
            30
        )

        layout.addWidget(
            self.arrow
        )

    # =====================================================
    # Set value
    # =====================================================

    def set_value(
        self,
        value: str,
    ) -> None:

        self.value_label.setText(
            value
        )

    # =====================================================
    # Mouse
    # =====================================================

    def mousePressEvent(
        self,
        event,
    ) -> None:

        if (
            self.clickable
            and event.button()
            == Qt.MouseButton.LeftButton
        ):
            self.clicked.emit()

        super().mousePressEvent(
            event
        )