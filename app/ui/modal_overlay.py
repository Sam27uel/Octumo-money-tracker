from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)


class ModalOverlay(QWidget):
    def __init__(
        self,
        content: QWidget,
        parent: QWidget,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("modal_overlay")

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        overlay_layout = QHBoxLayout(self)
        overlay_layout.setContentsMargins(
            24,
            24,
            24,
            24,
        )
        overlay_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.card = QFrame()
        self.card.setObjectName("modal_card")
        self.card.setFixedWidth(500)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(
            32,
            30,
            32,
            30,
        )
        card_layout.setSpacing(0)

        card_layout.addWidget(content)

        overlay_layout.addWidget(self.card)

        self.setStyleSheet(
            """
            QWidget#modal_overlay {
                background-color: rgba(15, 23, 42, 135);
            }

            QFrame#modal_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 18px;
            }
            """
        )

        self.raise_()

    def close_modal(self) -> None:
        self.deleteLater()