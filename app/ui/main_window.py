from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QStackedWidget,
)
from PySide6.QtCore import Qt, QEvent

from app.ui.dashboard_view import DashboardView
from app.ui.transactions_view import TransactionsView
from app.ui.accounts_view import AccountsView
from app.ui.categories_view import CategoriesView
from app.ui.settings_view import SettingsView
from app.ui.modal_overlay import ModalOverlay


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Octumo")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)

        # Main application container
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Modal overlay
        self.modal_overlay = None
        self.modal_stack = []

        # Install global keyboard event filter
        QApplication.instance().installEventFilter(self)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(
            20,
            24,
            20,
            24,
        )
        sidebar_layout.setSpacing(8)

        logo = QLabel("Octumo 🐙")
        logo.setObjectName("logo")

        sidebar_layout.addWidget(logo)
        sidebar_layout.addSpacing(24)

        # Navigation buttons
        self.dashboard_button = QPushButton("Dashboard")
        self.transactions_button = QPushButton(
            "Transactions"
        )
        self.accounts_button = QPushButton("Accounts")
        self.categories_button = QPushButton(
            "Categories"
        )
        self.settings_button = QPushButton("Settings")

        buttons = [
            self.dashboard_button,
            self.transactions_button,
            self.accounts_button,
            self.categories_button,
            self.settings_button,
        ]

        for button in buttons:
            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )
            sidebar_layout.addWidget(button)

        sidebar_layout.addStretch()

        # Pages
        self.pages = QStackedWidget()

        self.pages.addWidget(DashboardView())
        self.pages.addWidget(TransactionsView())
        self.pages.addWidget(AccountsView())
        self.pages.addWidget(CategoriesView())
        self.pages.addWidget(SettingsView())

        # Navigation connections
        self.dashboard_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(0)
        )

        self.transactions_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(1)
        )

        self.accounts_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(2)
        )

        self.categories_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(3)
        )

        self.settings_button.clicked.connect(
            lambda: self.pages.setCurrentIndex(4)
        )

        # Main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)

        self.setCentralWidget(central_widget)

        # Styling
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #F8FAFC;
            }

            QWidget#sidebar {
                background-color: #FFFFFF;
                border-right: 1px solid #E2E8F0;
            }

            QLabel#logo {
                color: #0F172A;
                font-size: 24px;
                font-weight: 700;
            }

            QPushButton {
                background-color: transparent;
                color: #475569;
                border: none;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }

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
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#primary_button:hover {
                background-color: #1E293B;
            }

            QWidget#account_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }

            QLabel#account_name {
                color: #0F172A;
                font-size: 16px;
                font-weight: 600;
            }

            QLabel#account_balance {
                color: #0F172A;
                font-size: 16px;
                font-weight: 700;
            }

            QLabel#empty_state {
                color: #64748B;
                font-size: 15px;
            }

            QPushButton#delete_button {
                background-color: #FEE2E2;
                color: #B91C1C;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
            }

            QPushButton#delete_button:hover {
                background-color: #FECACA;
            }
            """
        )

    def eventFilter(
        self,
        watched,
        event,
    ) -> bool:
        """
        Handle global keyboard shortcuts while a modal is open.
        """

        if self.modal_overlay is None:
            return super().eventFilter(
                watched,
                event,
            )

        if event.type() != QEvent.Type.KeyPress:
            return super().eventFilter(
                watched,
                event,
            )

        # ESC = go back / close current modal
        if event.key() == Qt.Key.Key_Escape:
            self.close_modal()
            event.accept()
            return True

        # ENTER = confirm primary action
        if event.key() in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):
            primary_button = self.modal_overlay.findChild(
                QPushButton,
                "modal_primary_button",
            )

            if (
                primary_button is not None
                and primary_button.isVisible()
                and primary_button.isEnabled()
            ):
                primary_button.click()
                event.accept()
                return True

        return super().eventFilter(
            watched,
            event,
        )

    def show_modal(self, content: QWidget) -> None:
        """
        Display a content widget inside the application
        modal overlay.

        Existing overlays are hidden and stored in a stack
        so nested modals can be opened safely.
        """

        if self.modal_overlay is not None:
            self.modal_stack.append(
                self.modal_overlay
            )

            self.modal_overlay.hide()

        self.modal_overlay = ModalOverlay(
            content=content,
            parent=self.centralWidget(),
        )

        self.modal_overlay.setGeometry(
            self.centralWidget().rect()
        )

        self.modal_overlay.show()
        self.modal_overlay.raise_()

    def close_modal(self) -> None:
        """
        Close the currently displayed modal overlay.

        If a previous modal exists in the stack,
        restore it instead of destroying it.
        """

        if self.modal_overlay is not None:
            current_overlay = self.modal_overlay

            self.modal_overlay = None

            current_overlay.close_modal()

        if self.modal_stack:
            previous_overlay = self.modal_stack.pop()

            self.modal_overlay = previous_overlay

            previous_overlay.setGeometry(
                self.centralWidget().rect()
            )

            previous_overlay.show()
            previous_overlay.raise_()