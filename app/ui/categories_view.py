from PySide6.QtCore import Qt
from app.ui.add_category_modal import AddCategoryModal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services.category_service import (
    list_categories,
)


class CategoriesView(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.build_ui()
        self.refresh_categories()

    # =================================================
    # UI
    # =================================================

    def build_ui(self) -> None:
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            44,
            36,
            44,
            44,
        )

        layout.setSpacing(0)

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        header_layout = QHBoxLayout()

        header_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        header_layout.setSpacing(20)

        title_container = QVBoxLayout()

        title_container.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        title_container.setSpacing(6)

        title = QLabel("Categories")
        title.setObjectName("page_title")

        subtitle = QLabel(
            "Manage the categories used to organize your transactions."
        )
        subtitle.setObjectName("page_subtitle")

        title_container.addWidget(title)
        title_container.addWidget(subtitle)

        header_layout.addLayout(
            title_container
        )

        header_layout.addStretch()

        self.add_category_button = QPushButton(
            "+ Add category"
        )

        self.add_category_button.setObjectName(
            "primary_button"
        )

        self.add_category_button.setFixedHeight(
            42
        )

        self.add_category_button.setMinimumWidth(
            130
        )

        self.add_category_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.add_category_button.clicked.connect(
            self.open_add_category_modal
        )

        header_layout.addWidget(
            self.add_category_button
        )

        layout.addLayout(
            header_layout
        )

        # -------------------------------------------------
        # Categories scroll area
        # -------------------------------------------------

        layout.addSpacing(34)

        self.categories_scroll = QScrollArea()

        self.categories_scroll.setObjectName(
            "categories_scroll"
        )

        self.categories_scroll.setWidgetResizable(
            True
        )

        self.categories_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.categories_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.categories_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.categories_scroll.setWidget(
            self.create_categories_container()
        )

        layout.addWidget(
            self.categories_scroll,
            1,
        )

        # -------------------------------------------------
        # Styling
        # -------------------------------------------------

        self.setStyleSheet(
            """
            QLabel#page_title {
                color: #0F172A;
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#page_subtitle {
                color: #64748B;
                font-size: 15px;
            }

            QPushButton#primary_button {
                background-color: #0F172A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#primary_button:hover {
                background-color: #1E293B;
            }

            QScrollArea#categories_scroll {
                background-color: transparent;
                border: none;
            }

            QWidget#categories_scroll_content {
                background-color: transparent;
            }

            QLabel#section_title {
                color: #0F172A;
                font-size: 15px;
                font-weight: 600;
            }

            QWidget#category_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }

            QLabel#category_name {
                color: #0F172A;
                font-size: 16px;
                font-weight: 600;
            }

            QLabel#archived_label {
                color: #64748B;
                background-color: #F1F5F9;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: 600;
            }

            QPushButton#manage_button {
                background-color: transparent;
                color: #475569;
                border: none;
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 14px;
                font-weight: 500;
            }

            QPushButton#manage_button:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }

            QLabel#empty_state {
                color: #64748B;
                font-size: 15px;
            }

            QScrollBar:vertical {
                width: 8px;
                background: transparent;
                margin: 2px 0 2px 0;
            }

            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 4px;
                min-height: 32px;
            }

            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

    def create_categories_container(self) -> QWidget:
        container = QWidget()

        container.setObjectName(
            "categories_scroll_content"
        )

        self.categories_container = QVBoxLayout(
            container
        )

        self.categories_container.setContentsMargins(
            0,
            0,
            8,
            0,
        )

        self.categories_container.setSpacing(
            0
        )

        self.categories_container.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        return container

    # =================================================
    # Categories
    # =================================================

    def refresh_categories(self) -> None:
        self.clear_categories()

        # Active categories
        income_categories = list_categories(
            "income"
        )

        expense_categories = list_categories(
            "expense"
        )

        # Archived categories
        all_categories = list_categories(
            include_archived=True
        )

        archived_categories = [
            category
            for category in all_categories
            if not category["is_active"]
        ]

        # -------------------------------------------------
        # Income
        # -------------------------------------------------

        self.add_category_section(
            title="Income",
            categories=income_categories,
        )

        self.categories_container.addSpacing(
            28
        )

        # -------------------------------------------------
        # Expenses
        # -------------------------------------------------

        self.add_category_section(
            title="Expenses",
            categories=expense_categories,
        )

        # -------------------------------------------------
        # Archived
        # -------------------------------------------------

        if archived_categories:
            self.categories_container.addSpacing(
                32
            )

            self.add_category_section(
                title="Archived",
                categories=archived_categories,
                archived=True,
            )

        self.categories_container.addStretch()

    def clear_categories(self) -> None:
        while self.categories_container.count():
            item = self.categories_container.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def add_category_section(
        self,
        title: str,
        categories,
        archived: bool = False,
    ) -> None:
        section_title = QLabel(
            title
        )

        section_title.setObjectName(
            "section_title"
        )

        self.categories_container.addWidget(
            section_title
        )

        self.categories_container.addSpacing(
            10
        )

        if not categories:
            empty_label = QLabel(
                "No categories yet."
            )

            empty_label.setObjectName(
                "empty_state"
            )

            self.categories_container.addWidget(
                empty_label
            )

            return

        for category in categories:
            self.add_category_card(
                category,
                archived=archived,
            )

            self.categories_container.addSpacing(
                12
            )

    def add_category_card(
        self,
        category,
        archived: bool = False,
    ) -> None:
        category_id = category["id"]
        category_name = category["name"]

        # -------------------------------------------------
        # Card
        # -------------------------------------------------

        card = QWidget()

        card.setObjectName(
            "category_card"
        )

        card_layout = QHBoxLayout(card)

        card_layout.setContentsMargins(
            26,
            18,
            18,
            18,
        )

        card_layout.setSpacing(
            16
        )

        # -------------------------------------------------
        # Name
        # -------------------------------------------------

        name_label = QLabel(
            category_name
        )

        name_label.setObjectName(
            "category_name"
        )

        card_layout.addWidget(
            name_label
        )

        # -------------------------------------------------
        # Archived label
        # -------------------------------------------------

        if archived:
            archived_label = QLabel(
                "Archived"
            )

            archived_label.setObjectName(
                "archived_label"
            )

            card_layout.addWidget(
                archived_label
            )

        # -------------------------------------------------
        # Manage
        # -------------------------------------------------

        card_layout.addStretch()

        manage_button = QPushButton(
            "Manage"
        )

        manage_button.setObjectName(
            "manage_button"
        )

        manage_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        manage_button.clicked.connect(
            lambda checked=False,
            category_id=category_id:
            self.open_manage_category(
                category_id
            )
        )

        card_layout.addWidget(
            manage_button
        )

        self.categories_container.addWidget(
            card
        )

    # =================================================
    # Add category
    # =================================================

    def open_add_category_modal(self) -> None:
        from PySide6.QtWidgets import QApplication

        main_window = QApplication.activeWindow()

        modal = AddCategoryModal(
            parent=main_window
        )

        modal.cancelled.connect(
            lambda: self.close_category_modal(
                modal
            )
        )

        main_window.show_modal(
            modal
        )

    # =================================================
    # Manage category
    # =================================================

    def open_manage_category(
        self,
        category_id: int,
    ) -> None:
        from PySide6.QtWidgets import QApplication
        from app.ui.manage_category_modal import (
            ManageCategoryModal,
        )

        main_window = QApplication.activeWindow()

        modal = ManageCategoryModal(
            category_id=category_id,
            parent=main_window,
        )

        modal.cancelled.connect(
            lambda: self.close_category_modal(
                modal
            )
        )

        main_window.show_modal(
            modal
        )

    # =================================================
    # Close modal
    # =================================================

    def close_category_modal(
        self,
        modal,
    ) -> None:
        from PySide6.QtWidgets import QApplication

        main_window = QApplication.activeWindow()

        if main_window.modal_overlay is not None:
            main_window.close_modal()

        self.refresh_categories()