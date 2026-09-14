from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.modal import Modal
from app.services.category_service import (
    archive_category,
    delete_category,
    get_category,
    get_category_usage_count,
    restore_category,
    update_category,
)


class ManageCategoryModal(Modal):
    def __init__(
        self,
        category_id: int,
        parent=None,
    ) -> None:
        super().__init__(
            title="Manage category",
            subtitle="Edit the category details or manage its status.",
            primary_text="Save changes",
            cancel_text="Cancel",
            parent=parent,
        )

        self.category_id = category_id

        category = get_category(category_id)

        if category is None:
            raise ValueError("Category not found.")

        self.category = category

        # =================================================
        # Category name
        # =================================================

        name_label = QLabel("Category name")
        name_label.setObjectName("field_label")

        self.name_input = QLineEdit()
        self.name_input.setText(category["name"])
        self.name_input.setFixedHeight(42)

        name_container = QWidget()

        name_layout = QVBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(8)

        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)

        self.add_content(name_container)

        # =================================================
        # Category information
        # =================================================

        info_card = QFrame()
        info_card.setObjectName("category_info_card")

        info_layout = QVBoxLayout(info_card)
        info_layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )
        info_layout.setSpacing(10)

        # -------------------------------------------------
        # Type
        # -------------------------------------------------

        type_row = QHBoxLayout()
        type_row.setContentsMargins(0, 0, 0, 0)

        type_label = QLabel("Type")
        type_label.setObjectName("info_label")

        type_value = QLabel(
            "Income"
            if category["kind"] == "income"
            else "Expense"
        )
        type_value.setObjectName("info_value")

        type_row.addWidget(type_label)
        type_row.addStretch()
        type_row.addWidget(type_value)

        info_layout.addLayout(type_row)

        # -------------------------------------------------
        # Usage
        # -------------------------------------------------

        usage_count = get_category_usage_count(
            category_id
        )

        usage_row = QHBoxLayout()
        usage_row.setContentsMargins(0, 0, 0, 0)

        usage_label = QLabel("Usage")
        usage_label.setObjectName("info_label")

        usage_value = QLabel(
            f"{usage_count} "
            f"{'transaction' if usage_count == 1 else 'transactions'}"
        )
        usage_value.setObjectName("info_value")

        usage_row.addWidget(usage_label)
        usage_row.addStretch()
        usage_row.addWidget(usage_value)

        info_layout.addLayout(usage_row)

        self.add_content(info_card)

        self.add_spacing(4)

        # =================================================
        # Status section
        # =================================================

        status_card = self.create_status_section(
            usage_count
        )

        self.add_content(status_card)

        # =================================================
        # Styling
        # =================================================

        info_card.setStyleSheet(
            """
            QFrame#category_info_card {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }

            QLabel#info_label {
                color: #64748B;
                font-size: 13px;
                font-weight: 500;
            }

            QLabel#info_value {
                color: #0F172A;
                font-size: 13px;
                font-weight: 600;
            }
            """
        )

        self.submitted.connect(
            self.handle_submit
        )

        self.name_input.returnPressed.connect(
            self.submit
        )

        self.name_input.setFocus()

    # =================================================
    # Status section
    # =================================================

    def create_status_section(
        self,
        usage_count: int,
    ) -> QWidget:
        section = QFrame()
        section.setObjectName(
            "category_status_card"
        )

        layout = QVBoxLayout(section)

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        layout.setSpacing(12)

        # -------------------------------------------------
        # Status header
        # -------------------------------------------------

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        title_container = QVBoxLayout()
        title_container.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        title_container.setSpacing(4)

        title = QLabel()
        title.setObjectName(
            "category_status_title"
        )

        description = QLabel()
        description.setObjectName(
            "category_status_description"
        )

        description.setWordWrap(True)

        title_container.addWidget(title)
        title_container.addWidget(description)

        header_layout.addLayout(
            title_container,
            1,
        )

        layout.addLayout(
            header_layout
        )

        # -------------------------------------------------
        # Actions
        # -------------------------------------------------

        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        actions_layout.setSpacing(8)

        if self.category["is_active"]:

            # ---------------------------------------------
            # Active category
            # ---------------------------------------------

            title.setText(
                "Category is active"
            )

            description.setText(
                "This category is currently available "
                "for new transactions."
            )

            archive_button = QPushButton(
                "Archive"
            )

            archive_button.setObjectName(
                "category_action_button"
            )

            archive_button.setFixedHeight(
                38
            )

            archive_button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            archive_button.clicked.connect(
                self.handle_archive
            )

            actions_layout.addWidget(
                archive_button
            )

            # ---------------------------------------------
            # Permanent delete
            # ---------------------------------------------

            if usage_count == 0:
                delete_button = QPushButton(
                    "Delete permanently"
                )

                delete_button.setObjectName(
                    "category_delete_button"
                )

                delete_button.setFixedHeight(
                    38
                )

                delete_button.setCursor(
                    Qt.CursorShape.PointingHandCursor
                )

                delete_button.clicked.connect(
                    self.handle_delete
                )

                actions_layout.addWidget(
                    delete_button
                )

        else:

            # ---------------------------------------------
            # Archived category
            # ---------------------------------------------

            title.setText(
                "Category is archived"
            )

            description.setText(
                "This category is hidden from new "
                "transactions but existing transactions "
                "remain unchanged."
            )

            restore_button = QPushButton(
                "Restore"
            )

            restore_button.setObjectName(
                "category_action_button"
            )

            restore_button.setFixedHeight(
                38
            )

            restore_button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            restore_button.clicked.connect(
                self.handle_restore
            )

            actions_layout.addWidget(
                restore_button
            )

        actions_layout.addStretch()

        layout.addLayout(
            actions_layout
        )

        # =================================================
        # Styling
        # =================================================

        section.setStyleSheet(
            """
            QFrame#category_status_card {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }

            QLabel#category_status_title {
                color: #0F172A;
                font-size: 14px;
                font-weight: 600;
            }

            QLabel#category_status_description {
                color: #64748B;
                font-size: 12px;
            }

            QPushButton#category_action_button {
                background-color: #FFFFFF;
                color: #334155;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 14px;
                min-width: 90px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#category_action_button:hover {
                background-color: #F1F5F9;
                border-color: #94A3B8;
                color: #0F172A;
            }

            QPushButton#category_delete_button {
                background-color: #FFFFFF;
                color: #B91C1C;
                border: 1px solid #FCA5A5;
                border-radius: 8px;
                padding: 0 14px;
                min-width: 130px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#category_delete_button:hover {
                background-color: #FEF2F2;
                border-color: #F87171;
            }
            """
        )

        return section

    # =================================================
    # Actions
    # =================================================

    def handle_submit(self) -> None:
        name = self.name_input.text().strip()

        if not name:
            self.name_input.setFocus()
            return

        update_category(
            category_id=self.category_id,
            name=name,
        )

        self.cancelled.emit()

    def handle_archive(self) -> None:
        archive_category(
            self.category_id
        )

        self.cancelled.emit()

    def handle_restore(self) -> None:
        restore_category(
            self.category_id
        )

        self.cancelled.emit()

    def handle_delete(self) -> None:
        delete_category(
            self.category_id
        )

        self.cancelled.emit()