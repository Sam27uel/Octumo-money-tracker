from datetime import date, timedelta

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services.account_service import list_accounts

from app.services.category_service import list_categories

from app.services.transaction_service import (
    delete_transaction,
    get_transaction,
    list_transactions,
)

from app.services.recurring_transaction_service import (
    generate_due_transactions,
    list_recurring_transactions,
)

from app.ui.add_transaction_dialog import (
    AddTransactionDialog,
    ModernComboBox,
)

from app.ui.edit_transaction_dialog import (
    EditTransactionDialog,
)

from app.ui.modal import Modal


class TransactionsView(QWidget):

    def __init__(
        self,
        parent=None,
    ) -> None:

        super().__init__(parent)

        self.all_transactions = []
        self.recurring_transactions = []

        self.build_ui()

        self.load_filter_data()

        self.refresh_transactions()

    # =========================================================
    # UI
    # =========================================================

    def build_ui(self) -> None:

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            44,
            36,
            44,
            36,
        )

        layout.setSpacing(0)

        # -----------------------------------------------------
        # Header
        # -----------------------------------------------------

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

        title_container.setSpacing(5)

        title = QLabel("Transactions")

        title.setObjectName(
            "page_title"
        )

        subtitle = QLabel(
            "View and manage your transactions."
        )

        subtitle.setObjectName(
            "page_subtitle"
        )

        title_container.addWidget(
            title
        )

        title_container.addWidget(
            subtitle
        )

        header_layout.addLayout(
            title_container
        )

        header_layout.addStretch()

        self.add_transaction_button = QPushButton(
            "+ Add transaction"
        )

        self.add_transaction_button.setObjectName(
            "primary_button"
        )

        self.add_transaction_button.setFixedHeight(
            42
        )

        self.add_transaction_button.setMinimumWidth(
            150
        )

        self.add_transaction_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.add_transaction_button.clicked.connect(
            self.open_add_transaction_dialog
        )

        header_layout.addWidget(
            self.add_transaction_button
        )

        layout.addLayout(
            header_layout
        )

        # -----------------------------------------------------
        # Filters
        # -----------------------------------------------------

        layout.addSpacing(24)

        filters_card = QFrame()

        filters_card.setObjectName(
            "filters_card"
        )

        filters_layout = QVBoxLayout(
            filters_card
        )

        filters_layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        filters_layout.setSpacing(10)

        # -----------------------------------------------------
        # Search
        # -----------------------------------------------------

        self.search_input = QLineEdit()

        self.search_input.setObjectName(
            "transaction_search"
        )

        self.search_input.setPlaceholderText(
            "Search transactions..."
        )

        self.search_input.setFixedHeight(
            40
        )

        self.search_input.textChanged.connect(
            self.refresh_transactions
        )

        filters_layout.addWidget(
            self.search_input
        )

        # -----------------------------------------------------
        # Filter row
        # -----------------------------------------------------

        filters_row = QHBoxLayout()

        filters_row.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        filters_row.setSpacing(10)

        # -----------------------------------------------------
        # Account
        # -----------------------------------------------------

        self.account_filter = ModernComboBox()

        self.account_filter.setObjectName(
            "transaction_filter_combo"
        )

        self.account_filter.setFixedHeight(
            40
        )

        self.account_filter.currentIndexChanged.connect(
            self.refresh_transactions
        )

        filters_row.addWidget(
            self.account_filter,
            1,
        )

        # -----------------------------------------------------
        # Category
        # -----------------------------------------------------

        self.category_filter = ModernComboBox()

        self.category_filter.setObjectName(
            "transaction_filter_combo"
        )

        self.category_filter.setFixedHeight(
            40
        )

        self.category_filter.currentIndexChanged.connect(
            self.refresh_transactions
        )

        filters_row.addWidget(
            self.category_filter,
            1,
        )

        # -----------------------------------------------------
        # Type
        # -----------------------------------------------------

        self.type_filter = ModernComboBox()

        self.type_filter.setObjectName(
            "transaction_filter_combo"
        )

        self.type_filter.setFixedHeight(
            40
        )

        self.type_filter.addItem(
            "All types",
            None,
        )

        self.type_filter.addItem(
            "Income",
            "income",
        )

        self.type_filter.addItem(
            "Expenses",
            "expense",
        )

        self.type_filter.currentIndexChanged.connect(
            self.refresh_transactions
        )

        filters_row.addWidget(
            self.type_filter,
            1,
        )

        # -----------------------------------------------------
        # Date
        # -----------------------------------------------------

        self.date_filter = ModernComboBox()

        self.date_filter.setObjectName(
            "transaction_filter_combo"
        )

        self.date_filter.setFixedHeight(
            40
        )

        self.date_filter.addItem(
            "This month",
            "this_month",
        )

        self.date_filter.addItem(
            "Last month",
            "last_month",
        )

        self.date_filter.addItem(
            "Last 3 months",
            "last_3_months",
        )

        self.date_filter.addItem(
            "This year",
            "this_year",
        )

        self.date_filter.addItem(
            "All time",
            "all",
        )

        self.date_filter.currentIndexChanged.connect(
            self.refresh_transactions
        )

        filters_row.addWidget(
            self.date_filter,
            1,
        )

        # -----------------------------------------------------
        # Recurring filter
        # -----------------------------------------------------

        self.recurring_filter_button = QPushButton("↻ Recurring")

        self.recurring_filter_button.setObjectName(
            "recurring_filter_button"
        )

        self.recurring_filter_button.setCheckable(True)
        self.recurring_filter_button.setChecked(False)

        self.recurring_filter_button.setFixedHeight(40)
        self.recurring_filter_button.setFixedWidth(105)

        self.recurring_filter_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.recurring_filter_button.toggled.connect(
            self.refresh_transactions
        )

        filters_row.addWidget(
            self.recurring_filter_button
        )


        # -----------------------------------------------------
        # Clear
        # -----------------------------------------------------

        self.clear_filters_button = QPushButton(
            "Clear"
        )

        self.clear_filters_button.setObjectName(
            "clear_filters_button"
        )

        self.clear_filters_button.setFixedHeight(
            40
        )

        self.clear_filters_button.setFixedWidth(
            82
        )

        self.clear_filters_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.clear_filters_button.clicked.connect(
            self.clear_filters
        )

        filters_row.addWidget(
            self.clear_filters_button
        )

        filters_layout.addLayout(
            filters_row
        )

        layout.addWidget(
            filters_card
        )

        # -----------------------------------------------------
        # Summary
        # -----------------------------------------------------

        layout.addSpacing(16)

        self.summary_card = QFrame()

        self.summary_card.setObjectName(
            "summary_card"
        )

        summary_layout = QHBoxLayout(
            self.summary_card
        )

        summary_layout.setContentsMargins(
            20,
            11,
            20,
            11,
        )

        summary_layout.setSpacing(0)

        # -----------------------------------------------------
        # Income
        # -----------------------------------------------------

        income_container = QVBoxLayout()

        income_container.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        income_container.setSpacing(2)

        income_title = QLabel(
            "Income"
        )

        income_title.setObjectName(
            "summary_label"
        )

        self.income_value = QLabel(
            "0,00 €"
        )

        self.income_value.setObjectName(
            "summary_income"
        )

        income_container.addWidget(
            income_title
        )

        income_container.addWidget(
            self.income_value
        )

        summary_layout.addLayout(
            income_container,
            1,
        )

        # -----------------------------------------------------
        # Separator
        # -----------------------------------------------------

        separator_1 = QFrame()

        separator_1.setFrameShape(
            QFrame.Shape.VLine
        )

        separator_1.setFrameShadow(
            QFrame.Shadow.Plain
        )

        separator_1.setObjectName(
            "summary_separator"
        )

        summary_layout.addWidget(
            separator_1
        )

        # -----------------------------------------------------
        # Expenses
        # -----------------------------------------------------

        expenses_container = QVBoxLayout()

        expenses_container.setContentsMargins(
            20,
            0,
            20,
            0,
        )

        expenses_container.setSpacing(2)

        expenses_title = QLabel(
            "Expenses"
        )

        expenses_title.setObjectName(
            "summary_label"
        )

        self.expenses_value = QLabel(
            "0,00 €"
        )

        self.expenses_value.setObjectName(
            "summary_expense"
        )

        expenses_container.addWidget(
            expenses_title
        )

        expenses_container.addWidget(
            self.expenses_value
        )

        summary_layout.addLayout(
            expenses_container,
            1,
        )

        # -----------------------------------------------------
        # Separator
        # -----------------------------------------------------

        separator_2 = QFrame()

        separator_2.setFrameShape(
            QFrame.Shape.VLine
        )

        separator_2.setFrameShadow(
            QFrame.Shadow.Plain
        )

        separator_2.setObjectName(
            "summary_separator"
        )

        summary_layout.addWidget(
            separator_2
        )

        # -----------------------------------------------------
        # Net
        # -----------------------------------------------------

        net_container = QVBoxLayout()

        net_container.setContentsMargins(
            20,
            0,
            0,
            0,
        )

        net_container.setSpacing(2)

        net_title = QLabel(
            "Net"
        )

        net_title.setObjectName(
            "summary_label"
        )

        self.net_value = QLabel(
            "+0,00 €"
        )

        self.net_value.setObjectName(
            "summary_net_positive"
        )

        net_container.addWidget(
            net_title
        )

        net_container.addWidget(
            self.net_value
        )

        summary_layout.addLayout(
            net_container,
            1,
        )

        layout.addWidget(
            self.summary_card
        )

        # -----------------------------------------------------
        # Result count
        # -----------------------------------------------------

        layout.addSpacing(16)

        self.result_count_label = QLabel(
            "0 transactions"
        )

        self.result_count_label.setObjectName(
            "result_count"
        )

        layout.addWidget(
            self.result_count_label
        )

        # -----------------------------------------------------
        # Transaction scroll
        # -----------------------------------------------------

        layout.addSpacing(6)

        self.transactions_scroll = QScrollArea()

        self.transactions_scroll.setObjectName(
            "transactions_scroll"
        )

        self.transactions_scroll.setWidgetResizable(
            True
        )

        self.transactions_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.transactions_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.transactions_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.transactions_scroll.setWidget(
            self.create_transactions_container()
        )

        layout.addWidget(
            self.transactions_scroll,
            1,
        )

        # -----------------------------------------------------
        # Styling
        # -----------------------------------------------------

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
                font-weight: 500;
            }

            QPushButton#primary_button {
                background-color: #0F172A;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 0 16px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#primary_button:hover {
                background-color: #1E293B;
            }

            QPushButton#primary_button:pressed {
                background-color: #334155;
            }

            QFrame#filters_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 14px;
            }

            QLineEdit#transaction_search {
                background-color: #FFFFFF;
                color: #0F172A;
                border: 1px solid #CBD5E1;
                border-radius: 11px;
                padding-left: 13px;
                padding-right: 13px;
                font-size: 14px;
                font-weight: 500;
            }

            QLineEdit#transaction_search:hover {
                border-color: #94A3B8;
            }

            QLineEdit#transaction_search:focus {
                border-color: #64748B;
            }

            QLineEdit#transaction_search::placeholder {
                color: #94A3B8;
            }

            QComboBox#modern_combo_box::drop-down,
            QComboBox#transaction_filter_combo::drop-down {
                width: 0px;
                border: none;
                background: transparent;
            }

            QComboBox#modern_combo_box::down-arrow,
            QComboBox#transaction_filter_combo::down-arrow {
                image: none;
                width: 0px;
                height: 0px;
            }

            QComboBox#transaction_filter_combo {
                background-color: #FFFFFF;
                color: #17233B;
                border: 1px solid #CBD5E1;
                border-radius: 11px;
                font-size: 14px;
                font-weight: 600;
                padding-left: 12px;
                padding-right: 38px;
            }

            QComboBox#transaction_filter_combo:hover {
                border-color: #94A3B8;
            }

            QComboBox#transaction_filter_combo:focus {
                border-color: #64748B;
            }

            QPushButton#recurring_filter_button {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 11px;
                font-size: 14px;
                font-weight: 600;
                padding: 0px 10px;
            }

            QPushButton#recurring_filter_button:hover {
                background-color: #F8FAFC;
                color: #0F172A;
                border-color: #94A3B8;
            }

            QPushButton#recurring_filter_button:checked {
                background-color: #17243A;
                color: #FFFFFF;
                border-color: #17243A;
            }

            QPushButton#recurring_filter_button:checked:hover {
                background-color: #0F172A;
                border-color: #0F172A;
            }

            QPushButton#clear_filters_button {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 11px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#clear_filters_button:hover {
                background-color: #F8FAFC;
                color: #0F172A;
                border-color: #94A3B8;
            }

            QPushButton#clear_filters_button:pressed {
                background-color: #F1F5F9;
            }

            QFrame#summary_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 14px;
            }

            QLabel#summary_label {
                color: #64748B;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#summary_income {
                color: #15803D;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#summary_expense {
                color: #B91C1C;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#summary_net_positive {
                color: #15803D;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#summary_net_negative {
                color: #B91C1C;
                font-size: 17px;
                font-weight: 700;
            }

            QFrame#summary_separator {
                background-color: #E2E8F0;
                max-width: 1px;
            }

            QLabel#result_count {
                color: #64748B;
                font-size: 13px;
                font-weight: 600;
            }

            QScrollArea#transactions_scroll {
                background-color: transparent;
                border: none;
            }

            QWidget#transactions_scroll_content {
                background-color: transparent;
            }

            QWidget#transaction_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 13px;
            }

            QWidget#transaction_card:hover {
                background-color: #FCFDFE;
                border-color: #CBD5E1;
            }

            QLabel#transaction_category {
                color: #0F172A;
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#transaction_secondary {
                color: #64748B;
                font-size: 12px;
                font-weight: 500;
            }

            QLabel#transaction_recurring {
                color: #64748B;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#transaction_date {
                color: #64748B;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#transaction_amount_income {
                color: #15803D;
                font-size: 15px;
                font-weight: 700;
            }

            QLabel#transaction_amount_expense {
                color: #B91C1C;
                font-size: 15px;
                font-weight: 700;
            }

            QPushButton#transaction_edit_button {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 10px;
            }

            QPushButton#transaction_edit_button:hover {
                background-color: #F8FAFC;
                color: #0F172A;
                border-color: #94A3B8;
            }

            QPushButton#transaction_delete_button {
                background-color: #FFFFFF;
                color: #B91C1C;
                border: 1px solid #FCA5A5;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 10px;
            }

            QPushButton#transaction_delete_button:hover {
                background-color: #FEF2F2;
                border-color: #F87171;
            }

            QLabel#empty_state {
                color: #64748B;
                font-size: 15px;
                font-weight: 500;
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

    # =========================================================
    # Transactions container
    # =========================================================

    def create_transactions_container(self) -> QWidget:

        container = QWidget()

        container.setObjectName(
            "transactions_scroll_content"
        )

        self.transactions_container = QVBoxLayout(
            container
        )

        self.transactions_container.setContentsMargins(
            0,
            0,
            8,
            8,
        )

        self.transactions_container.setSpacing(
            10
        )

        self.transactions_container.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        return container

    # =========================================================
    # Filter data
    # =========================================================

    def load_filter_data(self) -> None:

        # -----------------------------------------------------
        # Accounts
        # -----------------------------------------------------

        self.account_filter.blockSignals(
            True
        )

        self.account_filter.clear()

        self.account_filter.addItem(
            "All accounts",
            None,
        )

        accounts = list_accounts()

        for account in accounts:

            self.account_filter.addItem(
                account["name"],
                account["id"],
            )

        self.account_filter.blockSignals(
            False
        )

        # -----------------------------------------------------
        # Categories
        # -----------------------------------------------------

        self.category_filter.blockSignals(
            True
        )

        self.category_filter.clear()

        self.category_filter.addItem(
            "All categories",
            None,
        )

        categories = list_categories()

        for category in categories:

            self.category_filter.addItem(
                category["name"],
                category["id"],
            )

        self.category_filter.blockSignals(
            False
        )

    # =========================================================
    # Refresh
    # =========================================================

    def refresh_transactions(self) -> None:

        # =====================================================
        # Keep recurring-generated transactions up to date.
        # =====================================================

        try:
            generated_count = generate_due_transactions()

            if generated_count > 0:
                print(
                    f"[Recurring] Generated "
                    f"{generated_count} transaction(s)."
                )

        except Exception as error:
            print(
                f"[Recurring ERROR] "
                f"{type(error).__name__}: {error}"
            )

        # =====================================================
        # Reload recurring templates from database.
        # =====================================================

        self.load_transaction_recurring_data()

        # =====================================================
        # Normal transactions
        # =====================================================

        self.clear_transactions()

        self.all_transactions = list_transactions()

        transactions = self.apply_filters(
            self.all_transactions
        )

        self.update_summary(
            transactions
        )

        self.update_result_count(
            len(transactions)
        )

        if not transactions:

            empty_label = QLabel(
                "No transactions match your filters."
            )

            empty_label.setObjectName(
                "empty_state"
            )

            empty_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            empty_label.setMinimumHeight(
                100
            )

            self.transactions_container.addWidget(
                empty_label
            )

            return

        for transaction in transactions:

            self.transactions_container.addWidget(
                self.create_transaction_card(
                    transaction
                )
            )

    # =========================================================
    # Transaction ↔ Recurring connection
    # =========================================================

    def load_transaction_recurring_data(
        self,
    ) -> None:
        """
        Load recurring templates directly from the database.

        Transaction View does not store its own recurring state.
        Add/Edit Transaction update the recurring table and this
        view reads that table again when it refreshes.
        """

        try:

            self.recurring_transactions = (
                list_recurring_transactions(
                    include_inactive=True
                )
            )

        except Exception:

            self.recurring_transactions = []

    def find_recurring_for_transaction(
        self,
        transaction,
    ):
        """
        Find the recurring template belonging to a transaction.

        Match:
        1. account
        2. category
        3. absolute amount
        4. income/expense kind
        5. exact start date when possible
        6. note for the broader fallback match

        Active recurring templates are preferred.
        """

        if not self.recurring_transactions:

            return None

        transaction_account_id = (
            transaction["account_id"]
        )

        transaction_category_id = (
            transaction["category_id"]
        )

        transaction_amount_cents = abs(
            transaction["amount_cents"]
        )

        transaction_kind = (
            "income"
            if transaction["amount_cents"] > 0
            else "expense"
        )

        transaction_date = (
            transaction["transaction_date"]
        )

        transaction_note = (
            transaction["note"]
            or ""
        )

        # =====================================================
        # Exact match including start_date
        # =====================================================

        exact_matches = []

        for recurring in self.recurring_transactions:

            if (
                recurring["account_id"]
                != transaction_account_id
            ):
                continue

            if (
                recurring["category_id"]
                != transaction_category_id
            ):
                continue

            if (
                abs(recurring["amount_cents"])
                != transaction_amount_cents
            ):
                continue

            if (
                recurring["kind"]
                != transaction_kind
            ):
                continue

            if (
                recurring["start_date"]
                != transaction_date
            ):
                continue

            exact_matches.append(
                recurring
            )

        if exact_matches:

            active_matches = [
                recurring
                for recurring in exact_matches
                if recurring["is_active"]
            ]

            if active_matches:

                return active_matches[0]

            return exact_matches[0]

        # =====================================================
        # Broader match
        #
        # Generated recurring transactions normally have a
        # transaction date different from start_date.
        # =====================================================

        broad_matches = []

        current_transaction_date = (
            self.parse_transaction_date(
                transaction_date
            )
        )

        for recurring in self.recurring_transactions:

            if (
                recurring["account_id"]
                != transaction_account_id
            ):
                continue

            if (
                recurring["category_id"]
                != transaction_category_id
            ):
                continue

            if (
                abs(recurring["amount_cents"])
                != transaction_amount_cents
            ):
                continue

            if (
                recurring["kind"]
                != transaction_kind
            ):
                continue

            recurring_note = (
                recurring["note"]
                or ""
            )

            if recurring_note != transaction_note:

                continue

            recurring_start_date = (
                self.parse_transaction_date(
                    recurring["start_date"]
                )
            )

            if (
                recurring_start_date is not None
                and current_transaction_date is not None
                and recurring_start_date
                > current_transaction_date
            ):
                continue

            broad_matches.append(
                recurring
            )

        if not broad_matches:

            return None

        # =====================================================
        # Prefer active templates.
        # =====================================================

        active_matches = [
            recurring
            for recurring in broad_matches
            if recurring["is_active"]
        ]

        candidates = (
            active_matches
            if active_matches
            else broad_matches
        )

        candidates.sort(
            key=lambda recurring: (
                self.parse_transaction_date(
                    recurring["start_date"]
                )
                or date.min
            ),
            reverse=True,
        )

        return candidates[0]

    @staticmethod
    def format_frequency(
        frequency: str | None,
    ) -> str:

        names = {
            "daily": "Daily",
            "weekly": "Weekly",
            "monthly": "Monthly",
            "yearly": "Yearly",
        }

        return names.get(
            frequency,
            str(frequency or "Unknown"),
        )

    @staticmethod
    def format_recurring_date(
        value: str | None,
    ) -> str:

        if not value:

            return "—"

        try:

            parsed_date = date.fromisoformat(
                value
            )

            return parsed_date.strftime(
                "%d.%m.%Y"
            )

        except (
            ValueError,
            TypeError,
        ):

            return str(value)

    def clear_transactions(
        self,
    ) -> None:

        while self.transactions_container.count():

            item = self.transactions_container.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

            else:

                child_layout = item.layout()

                if child_layout is not None:

                    self.clear_layout(
                        child_layout
                    )

    def clear_layout(
        self,
        layout,
    ) -> None:

        while layout.count():

            item = layout.takeAt(
                0
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

            child_layout = item.layout()

            if child_layout is not None:

                self.clear_layout(
                    child_layout
                )

    # =========================================================
    # Filtering
    # =========================================================

    def apply_filters(
        self,
        transactions,
    ):

        result = list(
            transactions
        )

        # -----------------------------------------------------
        # Recurring
        # -----------------------------------------------------

        if self.recurring_filter_button.isChecked():
            result = [
                transaction
                for transaction in result
                if self.find_recurring_for_transaction(
                    transaction
                ) is not None
            ]


        # -----------------------------------------------------
        # Account
        # -----------------------------------------------------

        account_id = (
            self.account_filter.currentData()
        )

        if account_id is not None:

            result = [
                transaction
                for transaction in result
                if transaction["account_id"]
                == account_id
            ]

        # -----------------------------------------------------
        # Category
        # -----------------------------------------------------

        category_id = (
            self.category_filter.currentData()
        )

        if category_id is not None:

            result = [
                transaction
                for transaction in result
                if transaction["category_id"]
                == category_id
            ]

        # -----------------------------------------------------
        # Type
        # -----------------------------------------------------

        kind = (
            self.type_filter.currentData()
        )

        if kind == "income":

            result = [
                transaction
                for transaction in result
                if transaction["amount_cents"] > 0
            ]

        elif kind == "expense":

            result = [
                transaction
                for transaction in result
                if transaction["amount_cents"] < 0
            ]

        # -----------------------------------------------------
        # Date
        # -----------------------------------------------------

        date_filter = (
            self.date_filter.currentData()
        )

        start_date, end_date = (
            self.get_date_range(
                date_filter
            )
        )

        if start_date is not None:

            filtered = []

            for transaction in result:

                transaction_date = (
                    self.parse_transaction_date(
                        transaction[
                            "transaction_date"
                        ]
                    )
                )

                if transaction_date is None:

                    continue

                if (
                    start_date
                    <= transaction_date
                    <= end_date
                ):

                    filtered.append(
                        transaction
                    )

            result = filtered

        # -----------------------------------------------------
        # Search
        # -----------------------------------------------------

        search_text = (
            self.search_input
            .text()
            .strip()
            .lower()
        )

        if search_text:

            filtered = []

            for transaction in result:

                if self.transaction_matches_search(
                    transaction,
                    search_text,
                ):

                    filtered.append(
                        transaction
                    )

            result = filtered

        result.sort(
            key=lambda transaction: (
                transaction["transaction_date"],
                transaction["id"],
            ),
            reverse=True,
        )

        return result

    def transaction_matches_search(
        self,
        transaction,
        search_text: str,
    ) -> bool:

        category_name = (
            transaction["category_name"]
            or ""
        )

        account_name = (
            transaction["account_name"]
            or ""
        )

        note = (
            transaction["note"]
            or ""
        )

        transaction_date = (
            transaction["transaction_date"]
            or ""
        )

        formatted_date = (
            self.format_date(
                transaction_date
            )
        )

        amount = (
            abs(
                transaction["amount_cents"]
            )
            / 100
        )

        amount_text = (
            self.format_amount(
                amount
            )
        )

        kind_text = (
            "income"
            if transaction["amount_cents"] > 0
            else "expense"
        )

        searchable_text = " ".join(
            [
                category_name,
                account_name,
                note,
                transaction_date,
                formatted_date,
                amount_text,
                kind_text,
            ]
        ).lower()

        return search_text in searchable_text

    # =========================================================
    # Date filters
    # =========================================================

    def get_date_range(
        self,
        filter_name: str | None,
    ):

        if (
            filter_name == "all"
            or filter_name is None
        ):

            return None, None

        today = date.today()

        if filter_name == "this_month":

            start_date = today.replace(
                day=1
            )

            end_date = today

            return start_date, end_date

        if filter_name == "last_month":

            first_this_month = (
                today.replace(
                    day=1
                )
            )

            last_day_previous_month = (
                first_this_month
                - timedelta(days=1)
            )

            start_date = (
                last_day_previous_month
                .replace(
                    day=1
                )
            )

            end_date = (
                last_day_previous_month
            )

            return start_date, end_date

        if filter_name == "last_3_months":

            first_this_month = (
                today.replace(
                    day=1
                )
            )

            start_date = (
                first_this_month
                - timedelta(days=1)
            ).replace(
                day=1
            )

            start_date = (
                start_date
                - timedelta(days=1)
            ).replace(
                day=1
            )

            end_date = today

            return start_date, end_date

        if filter_name == "this_year":

            start_date = date(
                today.year,
                1,
                1,
            )

            end_date = today

            return start_date, end_date

        return None, None

    @staticmethod
    def parse_transaction_date(
        date_value: str,
    ):

        try:

            year, month, day = (
                date_value.split("-")
            )

            return date(
                int(year),
                int(month),
                int(day),
            )

        except (
            ValueError,
            AttributeError,
        ):

            return None

    # =========================================================
    # Summary
    # =========================================================

    def update_summary(
        self,
        transactions,
    ) -> None:

        income_cents = 0
        expense_cents = 0

        for transaction in transactions:

            amount_cents = (
                transaction[
                    "amount_cents"
                ]
            )

            if amount_cents > 0:

                income_cents += amount_cents

            else:

                expense_cents += abs(
                    amount_cents
                )

        net_cents = (
            income_cents
            - expense_cents
        )

        self.income_value.setText(
            self.format_amount(
                income_cents / 100
            )
        )

        self.expenses_value.setText(
            self.format_amount(
                expense_cents / 100
            )
        )

        if net_cents >= 0:

            self.net_value.setObjectName(
                "summary_net_positive"
            )

            self.net_value.setText(
                "+"
                + self.format_amount(
                    net_cents / 100
                )
            )

        else:

            self.net_value.setObjectName(
                "summary_net_negative"
            )

            self.net_value.setText(
                "-"
                + self.format_amount(
                    abs(net_cents) / 100
                )
            )

        self.net_value.style().unpolish(
            self.net_value
        )

        self.net_value.style().polish(
            self.net_value
        )

    def update_result_count(
        self,
        count: int,
    ) -> None:

        if count == 1:

            text = "1 transaction"

        else:

            text = (
                f"{count} transactions"
            )

        self.result_count_label.setText(
            text
        )

    # =========================================================
    # Transaction card
    # =========================================================

    def create_transaction_card(
        self,
        transaction,
    ) -> QWidget:

        transaction_id = (
            transaction["id"]
        )

        amount_cents = (
            transaction["amount_cents"]
        )

        is_income = (
            amount_cents > 0
        )

        card = QWidget()

        card.setObjectName(
            "transaction_card"
        )

        card.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        card.mousePressEvent = (
            lambda event,
            transaction_id=transaction_id:
            self.open_transaction_details(
                transaction_id
            )
        )

        card_layout = QHBoxLayout(
            card
        )

        card_layout.setContentsMargins(
            18,
            10,
            16,
            10,
        )

        card_layout.setSpacing(12)

        # -----------------------------------------------------
        # Color dot
        # -----------------------------------------------------

        dot_container = QWidget()

        dot_container.setFixedWidth(
            18
        )

        dot_layout = QVBoxLayout(
            dot_container
        )

        dot_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        dot_layout.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        color_dot = QLabel()

        color_dot.setFixedSize(
            10,
            10,
        )

        color_dot.setStyleSheet(
            f"""
            background-color: {
                self.get_transaction_color(
                    transaction
                )
            };
            border-radius: 5px;
            """
        )

        dot_layout.addWidget(
            color_dot
        )

        card_layout.addWidget(
            dot_container,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )

        # -----------------------------------------------------
        # Information
        # -----------------------------------------------------

        information_layout = QVBoxLayout()

        information_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        information_layout.setSpacing(2)

        category_name = (
            transaction["category_name"]
            or "Uncategorized"
        )

        category_label = QLabel(
            category_name
        )

        category_label.setObjectName(
            "transaction_category"
        )

        information_layout.addWidget(
            category_label
        )

        note = (
            transaction["note"]
            or ""
        )

        account_name = (
            transaction["account_name"]
            or "Unknown account"
        )

        if note:

            secondary_text = (
                f"{account_name} · Note: {note}"
            )

        else:

            secondary_text = account_name

        secondary_label = QLabel(
            secondary_text
        )

        secondary_label.setObjectName(
            "transaction_secondary"
        )

        secondary_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.NoTextInteraction
        )

        secondary_label.setToolTip(
            secondary_text
        )

        information_layout.addWidget(
            secondary_label
        )

        # =====================================================
        # Recurring information
        # =====================================================

        recurring_transaction = (
            self.find_recurring_for_transaction(
                transaction
            )
        )

        if recurring_transaction is not None:

            frequency_text = (
                self.format_frequency(
                    recurring_transaction[
                        "frequency"
                    ]
                )
            )

            if recurring_transaction[
                "is_active"
            ]:

                recurring_text = (
                    f"↻ {frequency_text} · "
                    "Next payment: "
                    f"{self.format_recurring_date(
                        recurring_transaction[
                            "next_run_date"
                        ]
                    )}"
                )

            else:

                recurring_text = (
                    f"↻ {frequency_text} · Paused"
                )

            recurring_label = QLabel(
                recurring_text
            )

            recurring_label.setObjectName(
                "transaction_recurring"
            )

            recurring_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.NoTextInteraction
            )

            recurring_label.setToolTip(
                recurring_text
            )

            information_layout.addWidget(
                recurring_label
            )

        card_layout.addLayout(
            information_layout,
            1,
        )

        # -----------------------------------------------------
        # Date
        # -----------------------------------------------------

        date_label = QLabel(
            self.format_date(
                transaction[
                    "transaction_date"
                ]
            )
        )

        date_label.setObjectName(
            "transaction_date"
        )

        date_label.setFixedWidth(
            92
        )

        date_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        card_layout.addWidget(
            date_label,
            0,
        )

        # -----------------------------------------------------
        # Amount
        # -----------------------------------------------------

        amount = (
            abs(amount_cents)
            / 100
        )

        sign = (
            "+"
            if is_income
            else "-"
        )

        amount_label = QLabel(
            f"{sign}{self.format_amount(amount)}"
        )

        amount_label.setObjectName(
            "transaction_amount_income"
            if is_income
            else "transaction_amount_expense"
        )

        amount_label.setFixedWidth(
            108
        )

        amount_label.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignVCenter
        )

        card_layout.addWidget(
            amount_label,
            0,
        )

        # -----------------------------------------------------
        # Actions
        # -----------------------------------------------------

        actions_layout = QHBoxLayout()

        actions_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        actions_layout.setSpacing(8)

        # -----------------------------------------------------
        # Edit
        # -----------------------------------------------------

        edit_button = QPushButton(
            "Edit"
        )

        edit_button.setObjectName(
            "transaction_edit_button"
        )

        edit_button.setFixedSize(
            76,
            38,
        )

        edit_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        edit_button.clicked.connect(
            lambda checked=False,
            transaction_id=transaction_id:
            self.open_edit_transaction(
                transaction_id
            )
        )

        # -----------------------------------------------------
        # Delete
        # -----------------------------------------------------

        delete_button = QPushButton(
            "Delete"
        )

        delete_button.setObjectName(
            "transaction_delete_button"
        )

        delete_button.setFixedSize(
            88,
            38,
        )

        delete_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        delete_button.clicked.connect(
            lambda checked=False,
            transaction_id=transaction_id,
            category_name=category_name,
            amount_label=amount_label:
            self.confirm_delete_transaction(
                transaction_id,
                category_name,
                amount_label.text(),
            )
        )

        actions_layout.addWidget(
            edit_button
        )

        actions_layout.addWidget(
            delete_button
        )

        card_layout.addLayout(
            actions_layout
        )

        return card

    # =========================================================
    # Transaction details
    # =========================================================

    def open_transaction_details(
        self,
        transaction_id: int,
    ) -> None:

        transaction = get_transaction(
            transaction_id
        )

        if transaction is None:

            return

        category_name = (
            transaction["category_name"]
            or "Uncategorized"
        )

        account_name = (
            transaction["account_name"]
            or "Unknown account"
        )

        note = (
            transaction["note"]
            or "—"
        )

        amount_cents = (
            transaction["amount_cents"]
        )

        amount = (
            abs(amount_cents)
            / 100
        )

        if amount_cents >= 0:

            amount_text = (
                "+"
                + self.format_amount(
                    amount
                )
            )

        else:

            amount_text = (
                "-"
                + self.format_amount(
                    amount
                )
            )

        date_text = self.format_date(
            transaction[
                "transaction_date"
            ]
        )

        modal = Modal(
            title="Transaction details",
            subtitle=category_name,
            primary_text="Close",
            cancel_text="",
        )

        modal.cancel_button.hide()

        # -----------------------------------------------------
        # Amount
        # -----------------------------------------------------

        amount_label = QLabel(
            amount_text
        )

        if amount_cents >= 0:

            amount_label.setStyleSheet(
                """
                color: #15803D;
                font-size: 24px;
                font-weight: 700;
                """
            )

        else:

            amount_label.setStyleSheet(
                """
                color: #B91C1C;
                font-size: 24px;
                font-weight: 700;
                """
            )

        modal.add_content(
            amount_label
        )

        # -----------------------------------------------------
        # Details frame
        # -----------------------------------------------------

        details_frame = QFrame()

        details_frame.setObjectName(
            "transaction_details_frame"
        )

        details_frame.setStyleSheet(
            """
            QFrame#transaction_details_frame {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }

            QLabel#detail_label {
                color: #64748B;
                font-size: 12px;
                font-weight: 600;
            }

            QLabel#detail_value {
                color: #0F172A;
                font-size: 14px;
                font-weight: 600;
            }
            """
        )

        details_layout = QVBoxLayout(
            details_frame
        )

        details_layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )

        details_layout.setSpacing(
            11
        )

        self.add_detail_row(
            details_layout,
            "Date",
            date_text,
        )

        self.add_detail_row(
            details_layout,
            "Account",
            account_name,
        )

        self.add_detail_row(
            details_layout,
            "Category",
            category_name,
        )

        self.add_detail_row(
            details_layout,
            "Note",
            note,
        )

        # =====================================================
        # Recurring information
        # =====================================================

        recurring_transaction = (
            self.find_recurring_for_transaction(
                transaction
            )
        )

        if recurring_transaction is None:

            self.add_detail_row(
                details_layout,
                "Recurring",
                "No",
            )

        else:

            frequency_text = (
                self.format_frequency(
                    recurring_transaction[
                        "frequency"
                    ]
                )
            )

            self.add_detail_row(
                details_layout,
                "Recurring",
                f"Yes · {frequency_text}",
            )

            self.add_detail_row(
                details_layout,
                "Next payment",
                (
                    self.format_recurring_date(
                        recurring_transaction[
                            "next_run_date"
                        ]
                    )
                    if recurring_transaction[
                        "is_active"
                    ]
                    else "Paused"
                ),
            )

        modal.add_content(
            details_frame
        )

        modal.submitted.connect(
            self.close_nested_modal
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    def add_detail_row(
        self,
        parent_layout,
        label_text: str,
        value_text: str,
    ) -> None:

        row = QVBoxLayout()

        row.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        row.setSpacing(2)

        label = QLabel(
            label_text
        )

        label.setObjectName(
            "detail_label"
        )

        value = QLabel(
            value_text
        )

        value.setObjectName(
            "detail_value"
        )

        value.setWordWrap(
            True
        )

        row.addWidget(
            label
        )

        row.addWidget(
            value
        )

        parent_layout.addLayout(
            row
        )

    # =========================================================
    # Add transaction
    # =========================================================

    def open_add_transaction_dialog(
        self,
    ) -> None:

        dialog = AddTransactionDialog(
            parent=self.window()
        )

        dialog.finished.connect(
            self.on_transaction_dialog_finished
        )

        self.window().show_modal(
            dialog
        )

    # =========================================================
    # Edit transaction
    # =========================================================

    def open_edit_transaction(
        self,
        transaction_id: int,
    ) -> None:

        try:

            dialog = EditTransactionDialog(
                transaction_id=transaction_id,
                parent=self.window(),
            )

        except ValueError:

            return

        dialog.finished.connect(
            self.on_transaction_dialog_finished
        )

        self.window().show_modal(
            dialog
        )

    # =========================================================
    # Delete confirmation
    # =========================================================

    def confirm_delete_transaction(
        self,
        transaction_id: int,
        category_name: str,
        amount_text: str,
    ) -> None:

        modal = Modal(
            title="Delete transaction?",
            subtitle=(
                f"{category_name} · {amount_text}\n\n"
                "This transaction will be permanently "
                "deleted. This action cannot be undone."
            ),
            primary_text="Delete transaction",
            cancel_text="Cancel",
        )

        modal.primary_button.setObjectName(
            "danger_button"
        )

        modal.primary_button.setStyleSheet(
            """
            QPushButton#danger_button {
                background-color: #B91C1C;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 0 16px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#danger_button:hover {
                background-color: #991B1B;
            }

            QPushButton#danger_button:pressed {
                background-color: #7F1D1D;
            }
            """
        )

        modal.primary_button.setFixedHeight(
            42
        )

        modal.submitted.connect(
            lambda:
            self.delete_transaction(
                transaction_id
            )
        )

        modal.cancelled.connect(
            self.close_nested_modal
        )

        self.window().show_modal(
            modal
        )

    # =========================================================
    # Delete
    # =========================================================

    def delete_transaction(
        self,
        transaction_id: int,
    ) -> None:

        try:

            delete_transaction(
                transaction_id
            )

        except Exception:

            self.close_nested_modal()

            return

        self.window().close_modal()

        self.refresh_transactions()

    # =========================================================
    # Modal helpers
    # =========================================================

    def on_transaction_dialog_finished(
        self,
    ) -> None:

        self.window().close_modal()

        self.refresh_transactions()

    def close_nested_modal(
        self,
    ) -> None:

        self.window().close_modal()

    # =========================================================
    # Clear filters
    # =========================================================

    def clear_filters(
        self,
    ) -> None:

        self.search_input.clear()
        self.account_filter.setCurrentIndex(0)
        self.category_filter.setCurrentIndex(0)
        self.type_filter.setCurrentIndex(0)
        self.date_filter.setCurrentIndex(0)
        self.recurring_filter_button.setChecked(False)

        self.refresh_transactions()

    # =========================================================
    # Formatting
    # =========================================================

    @staticmethod
    def format_amount(
        amount: float,
    ) -> str:

        return (
            f"{amount:,.2f} €"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", " ")
        )

    @staticmethod
    def format_date(
        date_value: str,
    ) -> str:

        try:

            year, month, day = (
                date_value.split("-")
            )

            return (
                f"{day}.{month}.{year}"
            )

        except (
            ValueError,
            AttributeError,
        ):

            return date_value

    # =========================================================
    # Transaction color
    # =========================================================

    @staticmethod
    def get_transaction_color(
        transaction,
    ) -> str:

        colors = [
            "#3B82F6",
            "#8B5CF6",
            "#EC4899",
            "#F59E0B",
            "#10B981",
            "#06B6D4",
            "#F97316",
            "#6366F1",
        ]

        category_id = (
            transaction["category_id"]
            or 0
        )

        return colors[
            category_id % len(colors)
        ]