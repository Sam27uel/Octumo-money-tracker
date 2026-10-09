from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from app.ui.modal import Modal


class EditProfileModal(Modal):

    def __init__(
        self,
        current_name: str = "",
        parent=None,
    ) -> None:

        super().__init__(
            title="Edit profile",
            subtitle="Update your personal information.",
            primary_text="Save changes",
            cancel_text="Cancel",
            parent=parent,
        )

        # =================================================
        # Name
        # =================================================

        name_label = QLabel(
            "Name"
        )

        name_label.setObjectName(
            "field_label"
        )

        self.name_input = QLineEdit()

        self.name_input.setPlaceholderText(
            "e.g. Samuel"
        )

        self.name_input.setFixedHeight(
            42
        )

        self.name_input.setText(
            current_name
        )

        # =================================================
        # Container
        # =================================================

        name_container = QWidget()

        name_layout = QVBoxLayout(
            name_container
        )

        name_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        name_layout.setSpacing(
            8
        )

        name_layout.addWidget(
            name_label
        )

        name_layout.addWidget(
            self.name_input
        )

        self.add_content(
            name_container
        )

        # =================================================
        # Focus
        # =================================================

        self.name_input.setFocus()

        self.name_input.selectAll()

        # =================================================
        # Enter
        # =================================================

        self.name_input.returnPressed.connect(
            self.submit
        )