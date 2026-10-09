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
        # Name container
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
        # Signals
        # =================================================

        self.submitted.connect(
            self.handle_submit
        )

        self.name_input.returnPressed.connect(
            self.submit
        )

        # =================================================
        # Focus
        # =================================================

        self.name_input.setFocus()

        self.name_input.selectAll()

    # =====================================================
    # Submit
    # =====================================================

    def handle_submit(self) -> None:

        name = (
            self.name_input
            .text()
            .strip()
        )

        # Do not close modal when empty
        if not name:
            self.name_input.setFocus()
            return

        self.current_name = name

        # Existing Octumo modal system uses
        # cancelled to close the modal overlay.
        self.cancelled.emit()