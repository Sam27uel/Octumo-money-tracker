from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.modal import Modal
from app.services.category_service import create_category


class CategoryTypeSelector(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.selected_kind = "income"
        self._animation = None

        self.setObjectName("category_type_selector")
        self.setFixedHeight(42)

        self.indicator = QFrame(self)
        self.indicator.setObjectName("category_type_indicator")
        self.indicator.setGeometry(1, 1, 1, 40)

        self.income_button = QPushButton("Income", self)
        self.expense_button = QPushButton("Expense", self)

        self.income_button.setObjectName("category_type_button")
        self.expense_button.setObjectName("category_type_button")

        self.income_button.setCheckable(True)
        self.expense_button.setCheckable(True)

        self.income_button.setChecked(True)

        self.type_group = QButtonGroup(self)
        self.type_group.setExclusive(True)
        self.type_group.addButton(self.income_button)
        self.type_group.addButton(self.expense_button)

        self.income_button.clicked.connect(
            lambda: self.set_category_type("income")
        )
        self.expense_button.clicked.connect(
            lambda: self.set_category_type("expense")
        )

        self.setStyleSheet(
            """
            QWidget#category_type_selector {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
            }

            QFrame#category_type_indicator {
                background-color: #0F172A;
                border-radius: 7px;
            }

            QPushButton#category_type_button {
                background-color: transparent;
                color: #475569;
                border: none;
                border-radius: 7px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#category_type_button:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }

            QPushButton#category_type_button:checked {
                background-color: transparent;
                color: #FFFFFF;
            }

            QPushButton#category_type_button:checked:hover {
                background-color: transparent;
                color: #FFFFFF;
            }
            """
        )

        self.income_button.raise_()
        self.expense_button.raise_()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.update_layout(animated=False)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update_layout(animated=False)

    def update_layout(self, animated: bool = True) -> None:
        margin = 1
        half_width = (self.width() - 2 * margin) / 2
        indicator_width = int(half_width)

        if self.selected_kind == "income":
            target_x = margin
        else:
            target_x = margin + indicator_width

        target_rect = QRect(
            int(target_x),
            margin,
            indicator_width,
            self.height() - 2 * margin,
        )

        if not animated:
            self.indicator.setGeometry(target_rect)

            self.income_button.setGeometry(
                margin,
                margin,
                indicator_width,
                self.height() - 2 * margin,
            )

            self.expense_button.setGeometry(
                margin + indicator_width,
                margin,
                indicator_width,
                self.height() - 2 * margin,
            )

            return

        animation = QPropertyAnimation(
            self.indicator,
            b"geometry",
            self,
        )

        animation.setDuration(180)
        animation.setStartValue(self.indicator.geometry())
        animation.setEndValue(target_rect)
        animation.setEasingCurve(
            QEasingCurve.Type.OutCubic
        )

        self._animation = animation
        animation.start()

    def set_category_type(self, kind: str) -> None:
        if kind == self.selected_kind:
            return

        self.selected_kind = kind
        self.update_layout(animated=True)


class AddCategoryModal(Modal):
    def __init__(self, parent=None) -> None:
        super().__init__(
            title="Add category",
            subtitle="Create a category for organizing your transactions.",
            primary_text="Add category",
            cancel_text="Cancel",
            parent=parent,
        )

        name_label = QLabel("Category name")
        name_label.setObjectName("field_label")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Salary")
        self.name_input.setFixedHeight(42)

        kind_label = QLabel("Type")
        kind_label.setObjectName("field_label")

        self.kind_input = CategoryTypeSelector()

        name_container = QWidget()
        name_layout = QVBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(8)
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)

        kind_container = QWidget()
        kind_layout = QVBoxLayout(kind_container)
        kind_layout.setContentsMargins(0, 0, 0, 0)
        kind_layout.setSpacing(8)
        kind_layout.addWidget(kind_label)
        kind_layout.addWidget(self.kind_input)

        self.add_content(name_container)
        self.add_content(kind_container)

        self.submitted.connect(self.handle_submit)
        self.name_input.returnPressed.connect(self.submit)

    def handle_submit(self) -> None:
        name = self.name_input.text().strip()

        if not name:
            self.name_input.setFocus()
            return

        create_category(
            name=name,
            kind=self.kind_input.selected_kind,
        )

        self.cancelled.emit()