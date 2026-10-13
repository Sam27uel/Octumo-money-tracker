from __future__ import annotations

import calendar
import math
from datetime import date, datetime
from typing import Optional

from PySide6.QtCore import (
    Qt,
    Signal,
    QRectF,
    QPointF,
)
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QBrush,
    QFont,
)
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.services.account_service import (
    get_current_balance,
    list_accounts,
)
from app.services.category_service import list_categories
from app.services.transaction_service import list_transactions
from app.services.recurring_transaction_service import (
    list_recurring_transactions,
)
from app.services.user_settings_service import get_user_name
from app.ui.modal import Modal


# ============================================================
# HELPERS
# ============================================================


def row_get(row, key, default=None):
    """
    Works with both sqlite3.Row and normal dictionaries.
    """
    try:
        return row[key]
    except (KeyError, IndexError, TypeError):
        return default


def format_money(cents: int) -> str:
    value = cents / 100
    formatted = (
        f"{value:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", " ")
    )
    return f"{formatted} €"


def format_signed_money(cents: int) -> str:
    if cents > 0:
        return f"+{format_money(cents)}"

    if cents < 0:
        return f"-{format_money(abs(cents))}"

    return "0,00 €"


def month_name(year: int, month: int) -> str:
    names = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    return f"{names[month - 1]} {year}"


def short_month_name(year: int, month: int) -> str:
    names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    return f"{names[month - 1]} {year}"


def month_start(year: int, month: int) -> date:
    return date(year, month, 1)


def month_end(year: int, month: int) -> date:
    last_day = calendar.monthrange(
        year,
        month,
    )[1]

    return date(
        year,
        month,
        last_day,
    )


def previous_month(
    year: int,
    month: int,
) -> tuple[int, int]:

    if month == 1:
        return year - 1, 12

    return year, month - 1


# ============================================================
# CLICKABLE CARD
# ============================================================


class ClickableCard(QFrame):

    clicked = Signal()

    def __init__(
        self,
        parent=None,
        object_name: str = "dashboard_card",
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            object_name
        )

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

    def mousePressEvent(self, event) -> None:

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self.clicked.emit()

        super().mousePressEvent(event)


# ============================================================
# DASHBOARD SCROLL AREA
# ============================================================


class DashboardScrollArea(QScrollArea):
    """Responsive dashboard scroll area.

    QScrollArea can retain the content widget's old width while the
    native window is being resized/maximized.  This subclass explicitly
    keeps the content at least as wide as the current viewport, without
    imposing a stale maximum width.
    """

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.sync_content_width()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.sync_content_width()

    def sync_content_width(self) -> None:
        content = self.widget()

        if content is None:
            return

        viewport_width = self.viewport().width()

        if viewport_width <= 0:
            return

        # The dashboard has no horizontal scrolling.  Its content must
        # therefore always have exactly the width of the current viewport.
        # Using a fixed width here is intentional: it prevents Qt from
        # keeping the old content width after maximize/restore operations.
        content.setFixedWidth(viewport_width)
        content.updateGeometry()




# ============================================================
# CASHFLOW CHART
# ============================================================


class CashflowChart(QWidget):

    hovered = Signal(int)

    def __init__(
        self,
        parent=None,
        large: bool = False,
    ) -> None:

        super().__init__(parent)

        self.income_values: list[int] = []
        self.expense_values: list[int] = []
        self.labels: list[str] = []
        self.hover_index: Optional[int] = None

        if large:
            self.setMinimumHeight(195)
            self.setMaximumHeight(220)
        else:
            self.setMinimumHeight(145)
            self.setMaximumHeight(165)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_data(
        self,
        income_values: list[int],
        expense_values: list[int],
        labels: list[str],
    ) -> None:

        self.income_values = income_values
        self.expense_values = expense_values
        self.labels = labels
        self.hover_index = None
        self.update()

    def _index_at_x(self, x: float) -> Optional[int]:

        if not self.income_values:
            return None

        left = 44
        right = 18
        usable_width = max(
            1,
            self.width() - left - right,
        )

        count = len(self.income_values)

        if count <= 1:
            return 0

        index_float = (
            (x - left)
            / usable_width
        ) * (count - 1)

        index = int(round(index_float))

        if index < 0 or index >= count:
            return None

        return index

    def mouseMoveEvent(self, event) -> None:

        index = self._index_at_x(
            event.position().x()
        )

        if index != self.hover_index:
            self.hover_index = index
            self.hovered.emit(
                index if index is not None else -1
            )
            self.update()

        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:

        self.hover_index = None
        self.update()

        super().leaveEvent(event)

    def paintEvent(self, event) -> None:

        painter = QPainter(self)

        try:

            painter.setRenderHint(
                QPainter.RenderHint.Antialiasing,
                True,
            )

            width = self.width()
            height = self.height()

            if not self.income_values:

                painter.setPen(
                    QColor("#94A3B8")
                )
                painter.setFont(
                    QFont("Arial", 11)
                )
                painter.drawText(
                    self.rect(),
                    Qt.AlignmentFlag.AlignCenter,
                    "No transaction data",
                )
                return

            left = 44
            right = 18
            top = 24
            bottom = 38

            chart_width = max(
                1,
                width - left - right,
            )
            chart_height = max(
                1,
                height - top - bottom,
            )

            values = (
                self.income_values
                + self.expense_values
            )

            maximum = max(values) if values else 1
            maximum = max(
                1,
                maximum,
            )

            # Give the top of the graph some breathing room.
            maximum = maximum * 1.18

            count = len(
                self.income_values
            )

            def point_for(
                index: int,
                value: int,
            ) -> QPointF:

                if count <= 1:
                    x = (
                        left
                        + chart_width / 2
                    )
                else:
                    x = (
                        left
                        + (
                            index
                            / (count - 1)
                        )
                        * chart_width
                    )

                y = (
                    top
                    + chart_height
                    - (
                        value
                        / maximum
                    )
                    * chart_height
                )

                return QPointF(x, y)

            # ------------------------------------------------
            # GRID
            # ------------------------------------------------

            grid_pen = QPen(
                QColor("#E2E8F0"),
                1,
            )
            painter.setPen(grid_pen)

            for level in range(4):

                ratio = level / 3
                y = (
                    top
                    + chart_height
                    * (1 - ratio)
                )

                painter.drawLine(
                    left,
                    int(y),
                    width - right,
                    int(y),
                )

                if level < 3:

                    value = (
                        maximum
                        * ratio
                    )

                    painter.setPen(
                        QColor("#94A3B8")
                    )
                    painter.setFont(
                        QFont(
                            "Arial",
                            7,
                        )
                    )

                    painter.drawText(
                        QRectF(
                            0,
                            y - 7,
                            left - 7,
                            14,
                        ),
                        Qt.AlignmentFlag.AlignRight
                        | Qt.AlignmentFlag.AlignVCenter,
                        format_money(
                            int(value)
                        ),
                    )

                    painter.setPen(
                        grid_pen
                    )

            # ------------------------------------------------
            # LINES
            # ------------------------------------------------

            income_path = QPainterPath()
            expense_path = QPainterPath()

            income_path.moveTo(
                point_for(
                    0,
                    self.income_values[0],
                )
            )

            expense_path.moveTo(
                point_for(
                    0,
                    self.expense_values[0],
                )
            )

            for index in range(
                1,
                count,
            ):

                previous_income = point_for(
                    index - 1,
                    self.income_values[index - 1],
                )
                current_income = point_for(
                    index,
                    self.income_values[index],
                )

                previous_expense = point_for(
                    index - 1,
                    self.expense_values[index - 1],
                )
                current_expense = point_for(
                    index,
                    self.expense_values[index],
                )

                income_delta = (
                    current_income.x()
                    - previous_income.x()
                )

                income_path.cubicTo(
                    previous_income.x()
                    + income_delta * 0.45,
                    previous_income.y(),
                    current_income.x()
                    - income_delta * 0.45,
                    current_income.y(),
                    current_income.x(),
                    current_income.y(),
                )

                expense_delta = (
                    current_expense.x()
                    - previous_expense.x()
                )

                expense_path.cubicTo(
                    previous_expense.x()
                    + expense_delta * 0.45,
                    previous_expense.y(),
                    current_expense.x()
                    - expense_delta * 0.45,
                    current_expense.y(),
                    current_expense.x(),
                    current_expense.y(),
                )

            income_pen = QPen(
                QColor("#15803D"),
                2,
            )
            expense_pen = QPen(
                QColor("#B91C1C"),
                2,
            )

            painter.setBrush(
                Qt.BrushStyle.NoBrush
            )

            painter.setPen(
                income_pen
            )
            painter.drawPath(
                income_path
            )

            painter.setPen(
                expense_pen
            )
            painter.drawPath(
                expense_path
            )

            # ------------------------------------------------
            # LEGEND
            # ------------------------------------------------

            legend_y = 5

            painter.setPen(
                QColor("#15803D")
            )
            painter.setFont(
                QFont(
                    "Arial",
                    8,
                    QFont.Weight.DemiBold,
                )
            )

            painter.drawText(
                QRectF(
                    left,
                    legend_y,
                    62,
                    14,
                ),
                Qt.AlignmentFlag.AlignLeft,
                "Income",
            )

            painter.setPen(
                QColor("#B91C1C")
            )

            painter.drawText(
                QRectF(
                    left + 66,
                    legend_y,
                    72,
                    14,
                ),
                Qt.AlignmentFlag.AlignLeft,
                "Expenses",
            )

            # ------------------------------------------------
            # HOVER
            # ------------------------------------------------

            active_index = self.hover_index

            if active_index is not None:

                income_point = point_for(
                    active_index,
                    self.income_values[
                        active_index
                    ],
                )

                expense_point = point_for(
                    active_index,
                    self.expense_values[
                        active_index
                    ],
                )

                hover_pen = QPen(
                    QColor("#CBD5E1"),
                    1,
                )

                painter.setPen(
                    hover_pen
                )

                painter.drawLine(
                    int(
                        income_point.x()
                    ),
                    top,
                    int(
                        income_point.x()
                    ),
                    int(
                        top + chart_height
                    ),
                )

                painter.setPen(
                    QPen(
                        QColor("#15803D"),
                        2,
                    )
                )
                painter.setBrush(
                    QBrush(
                        QColor("#FFFFFF")
                    )
                )

                painter.drawEllipse(
                    income_point,
                    4,
                    4,
                )

                painter.setPen(
                    QPen(
                        QColor("#B91C1C"),
                        2,
                    )
                )

                painter.drawEllipse(
                    expense_point,
                    4,
                    4,
                )

                # Keep the bubble completely inside the graph.
                bubble_width = 176
                bubble_height = 74

                bubble_x = (
                    income_point.x()
                    + 12
                )

                if (
                    bubble_x
                    + bubble_width
                    > width - 8
                ):
                    bubble_x = (
                        income_point.x()
                        - bubble_width
                        - 12
                    )

                bubble_x = max(
                    8,
                    min(
                        bubble_x,
                        width
                        - bubble_width
                        - 8,
                    ),
                )

                bubble_y = 22

                bubble_rect = QRectF(
                    bubble_x,
                    bubble_y,
                    bubble_width,
                    bubble_height,
                )

                painter.setPen(
                    QPen(
                        QColor("#E2E8F0"),
                        1,
                    )
                )
                painter.setBrush(
                    QBrush(
                        QColor("#FFFFFF")
                    )
                )

                painter.drawRoundedRect(
                    bubble_rect,
                    10,
                    10,
                )

                label = (
                    self.labels[
                        active_index
                    ]
                    if active_index
                    < len(self.labels)
                    else str(
                        active_index + 1
                    )
                )

                income = self.income_values[
                    active_index
                ]
                expense = self.expense_values[
                    active_index
                ]
                net = income - expense

                painter.setPen(
                    QColor("#0F172A")
                )
                painter.setFont(
                    QFont(
                        "Arial",
                        9,
                        QFont.Weight.DemiBold,
                    )
                )

                painter.drawText(
                    QRectF(
                        bubble_x + 12,
                        bubble_y + 8,
                        bubble_width - 24,
                        16,
                    ),
                    Qt.AlignmentFlag.AlignLeft,
                    label,
                )

                painter.setFont(
                    QFont(
                        "Arial",
                        8,
                    )
                )

                painter.setPen(
                    QColor("#15803D")
                )

                painter.drawText(
                    QRectF(
                        bubble_x + 12,
                        bubble_y + 30,
                        bubble_width - 24,
                        15,
                    ),
                    Qt.AlignmentFlag.AlignLeft,
                    f"Income  {format_money(income)}",
                )

                painter.setPen(
                    QColor("#B91C1C")
                )

                painter.drawText(
                    QRectF(
                        bubble_x + 12,
                        bubble_y + 46,
                        bubble_width - 24,
                        15,
                    ),
                    Qt.AlignmentFlag.AlignLeft,
                    f"Expenses  {format_money(expense)}",
                )

                painter.setPen(
                    QColor(
                        "#15803D"
                        if net >= 0
                        else "#B91C1C"
                    )
                )

                painter.setFont(
                    QFont(
                        "Arial",
                        8,
                        QFont.Weight.DemiBold,
                    )
                )

                painter.drawText(
                    QRectF(
                        bubble_x + 94,
                        bubble_y + 30,
                        70,
                        15,
                    ),
                    Qt.AlignmentFlag.AlignRight,
                    f"Net {format_signed_money(net)}",
                )

            # ------------------------------------------------
            # DATE LABELS
            # ------------------------------------------------

            if self.labels:

                label_count = len(
                    self.labels
                )

                if label_count <= 5:
                    indices = list(
                        range(label_count)
                    )
                else:
                    indices = [
                        0,
                        round(
                            (label_count - 1)
                            * 0.25
                        ),
                        round(
                            (label_count - 1)
                            * 0.50
                        ),
                        round(
                            (label_count - 1)
                            * 0.75
                        ),
                        label_count - 1,
                    ]

                indices = list(
                    dict.fromkeys(
                        indices
                    )
                )

                painter.setPen(
                    QColor("#64748B")
                )
                painter.setFont(
                    QFont(
                        "Arial",
                        8,
                        QFont.Weight.DemiBold,
                    )
                )

                for index in indices:

                    if label_count <= 1:
                        x = (
                            left
                            + chart_width / 2
                        )
                    else:
                        x = (
                            left
                            + (
                                index
                                / (
                                    label_count
                                    - 1
                                )
                            )
                            * chart_width
                        )

                    painter.drawText(
                        QRectF(
                            x - 25,
                            height - 27,
                            50,
                            16,
                        ),
                        Qt.AlignmentFlag.AlignCenter,
                        self.labels[index],
                    )

        finally:

            painter.end()


# ============================================================
# PIE / DONUT CHART
# ============================================================


class DonutChart(QWidget):

    def __init__(
        self,
        data: list[tuple[str, int]],
        center_label: str,
        parent=None,
    ) -> None:

        super().__init__(parent)

        self.data = [
            (str(label), int(value))
            for label, value in data
            if int(value) > 0
        ]

        self.center_label = center_label

        self.setMinimumHeight(190)
        self.setMaximumHeight(215)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

    def _prepare_data(
        self,
    ) -> list[tuple[str, int]]:

        if not self.data:
            return []

        sorted_data = sorted(
            self.data,
            key=lambda item: item[1],
            reverse=True,
        )

        # Keep the donut readable. Smaller slices are grouped.
        if len(sorted_data) <= 6:
            return sorted_data

        visible = sorted_data[:5]
        other = sum(
            value
            for _, value
            in sorted_data[5:]
        )

        if other > 0:
            visible.append(
                ("Other", other)
            )

        return visible

    def paintEvent(self, event) -> None:

        painter = QPainter(self)

        try:

            painter.setRenderHint(
                QPainter.RenderHint.Antialiasing,
                True,
            )

            data = self._prepare_data()

            if not data:

                painter.setPen(
                    QColor("#94A3B8")
                )
                painter.setFont(
                    QFont(
                        "Arial",
                        11,
                    )
                )
                painter.drawText(
                    self.rect(),
                    Qt.AlignmentFlag.AlignCenter,
                    "No data",
                )
                return

            width = self.width()
            height = self.height()

            legend_width = min(
                245,
                max(
                    185,
                    width * 0.36,
                ),
            )

            chart_area_width = max(
                180,
                width - legend_width,
            )

            diameter = min(
                210,
                max(
                    165,
                    height - 20,
                ),
                chart_area_width - 28,
            )

            circle_x = (
                (chart_area_width - diameter)
                / 2
            )

            circle_y = (
                (height - diameter)
                / 2
            )

            rect = QRectF(
                circle_x,
                circle_y,
                diameter,
                diameter,
            )

            total = sum(
                value
                for _, value in data
            )

            palette = [
                "#0F172A",
                "#15803D",
                "#3B82F6",
                "#F59E0B",
                "#8B5CF6",
                "#B91C1C",
            ]

            start_angle = 90 * 16

            for index, (_, value) in enumerate(
                data
            ):

                span = int(
                    round(
                        360
                        * 16
                        * value
                        / total
                    )
                )

                painter.setPen(
                    QPen(
                        QColor("#FFFFFF"),
                        3,
                    )
                )

                painter.setBrush(
                    QBrush(
                        QColor(
                            palette[
                                index
                                % len(palette)
                            ]
                        )
                    )
                )

                painter.drawPie(
                    rect,
                    start_angle,
                    -span,
                )

                start_angle -= span

            # White center creates the donut.
            inner_margin = diameter * 0.30

            inner_rect = rect.adjusted(
                inner_margin,
                inner_margin,
                -inner_margin,
                -inner_margin,
            )

            painter.setPen(
                Qt.PenStyle.NoPen
            )
            painter.setBrush(
                QBrush(
                    QColor("#F8FAFC")
                )
            )

            painter.drawEllipse(
                inner_rect
            )

            painter.setPen(
                QColor("#0F172A")
            )
            painter.setFont(
                QFont(
                    "Arial",
                    12,
                    QFont.Weight.DemiBold,
                )
            )

            painter.drawText(
                QRectF(
                    inner_rect.x(),
                    inner_rect.y()
                    + inner_rect.height() * 0.26,
                    inner_rect.width(),
                    20,
                ),
                Qt.AlignmentFlag.AlignCenter,
                self.center_label,
            )

            painter.setFont(
                QFont(
                    "Arial",
                    13,
                    QFont.Weight.Bold,
                )
            )

            painter.drawText(
                QRectF(
                    inner_rect.x() - 8,
                    inner_rect.y()
                    + inner_rect.height() * 0.49,
                    inner_rect.width() + 16,
                    24,
                ),
                Qt.AlignmentFlag.AlignCenter,
                format_money(total),
            )

            # ------------------------------------------------
            # LEGEND
            # ------------------------------------------------

            legend_x = (
                chart_area_width
                + 12
            )

            row_height = 34
            legend_top = max(
                16,
                (height
                 - len(data) * row_height)
                / 2,
            )

            for index, (
                label,
                value,
            ) in enumerate(data):

                y = (
                    legend_top
                    + index * row_height
                )

                color = QColor(
                    palette[
                        index
                        % len(palette)
                    ]
                )

                painter.setPen(
                    Qt.PenStyle.NoPen
                )
                painter.setBrush(
                    QBrush(color)
                )

                painter.drawRoundedRect(
                    QRectF(
                        legend_x,
                        y + 5,
                        10,
                        10,
                    ),
                    3,
                    3,
                )

                painter.setPen(
                    QColor("#0F172A")
                )
                painter.setFont(
                    QFont(
                        "Arial",
                        9,
                        QFont.Weight.DemiBold,
                    )
                )

                label_text = label

                if len(label_text) > 20:
                    label_text = (
                        label_text[:19]
                        + "…"
                    )

                painter.drawText(
                    QRectF(
                        legend_x + 17,
                        y,
                        max(
                            70,
                            legend_width - 95,
                        ),
                        20,
                    ),
                    Qt.AlignmentFlag.AlignLeft
                    | Qt.AlignmentFlag.AlignVCenter,
                    label_text,
                )

                painter.setPen(
                    QColor("#64748B")
                )
                painter.setFont(
                    QFont(
                        "Arial",
                        8,
                    )
                )

                percentage = (
                    value
                    / total
                    * 100
                )

                painter.drawText(
                    QRectF(
                        legend_x + 17,
                        y + 17,
                        max(
                            70,
                            legend_width - 95,
                        ),
                        15,
                    ),
                    Qt.AlignmentFlag.AlignLeft
                    | Qt.AlignmentFlag.AlignVCenter,
                    (
                        f"{format_money(value)}"
                        f"  ·  {percentage:.1f}%"
                    ),
                )

        finally:

            painter.end()


# ============================================================
# DASHBOARD VIEW
# ============================================================


class DashboardView(QWidget):

    def __init__(self) -> None:

        super().__init__()

        today = date.today()

        self.selected_year = (
            today.year
        )

        self.selected_month = (
            today.month
        )

        self.accounts = []
        self.transactions = []
        self.categories = []
        self.recurring = []
        self.user_name = "User"

        self.month_transactions = []

        self.total_balance = 0
        self.month_income = 0
        self.month_expenses = 0
        self.month_net = 0

        self.content_layout = None
        self.month_label = None

        self.build_ui()
        self.refresh()

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self) -> None:

        layout = QVBoxLayout(
            self
        )

        # Same base geometry as AccountsView.
        layout.setContentsMargins(
            44,
            36,
            44,
            44,
        )

        layout.setSpacing(
            0
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header_layout = QHBoxLayout()

        header_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        header_layout.setSpacing(
            20
        )

        title_container = QVBoxLayout()

        title_container.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        title_container.setSpacing(
            6
        )

        title = QLabel(
            "Dashboard"
        )

        title.setObjectName(
            "page_title"
        )

        self.page_subtitle = QLabel(
            ""
        )

        self.page_subtitle.setObjectName(
            "page_subtitle"
        )

        title_container.addWidget(
            title
        )

        title_container.addWidget(
            self.page_subtitle
        )

        header_layout.addLayout(
            title_container
        )

        header_layout.addStretch()

        # ----------------------------------------------------
        # MONTH SELECTOR
        # ----------------------------------------------------

        month_selector = QFrame()

        month_selector.setObjectName(
            "month_selector"
        )

        month_layout = QHBoxLayout(
            month_selector
        )

        month_layout.setContentsMargins(
            3,
            3,
            3,
            3,
        )

        month_layout.setSpacing(
            1
        )

        previous_button = QPushButton(
            "‹"
        )

        previous_button.setObjectName(
            "month_arrow"
        )

        previous_button.setFixedSize(
            34,
            34,
        )

        previous_button.setContentsMargins(0, 0, 0, 0)
        previous_button.setFlat(True)

        previous_button.clicked.connect(
            self.go_previous_month
        )

        next_button = QPushButton(
            "›"
        )

        next_button.setObjectName(
            "month_arrow"
        )

        next_button.setFixedSize(
            34,
            34,
        )

        next_button.setContentsMargins(0, 0, 0, 0)
        next_button.setFlat(True)

        next_button.clicked.connect(
            self.go_next_month
        )

        self.month_label = QLabel(
            short_month_name(
                self.selected_year,
                self.selected_month,
            )
        )

        self.month_label.setObjectName(
            "month_label"
        )

        self.month_label.setMinimumWidth(
            90
        )

        self.month_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        month_layout.addWidget(
            previous_button
        )

        month_layout.addWidget(
            self.month_label
        )

        month_layout.addWidget(
            next_button
        )

        header_layout.addWidget(
            month_selector
        )

        # ----------------------------------------------------
        # ADD TRANSACTION
        # ----------------------------------------------------

        add_button = QPushButton(
            "+ Add transaction"
        )

        add_button.setObjectName(
            "primary_button"
        )

        # Same dimensions as AccountsView.
        add_button.setFixedHeight(
            42
        )

        add_button.setMinimumWidth(
            130
        )

        add_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        add_button.clicked.connect(
            self.open_add_transaction
        )

        header_layout.addWidget(
            add_button
        )

        layout.addLayout(
            header_layout
        )

        # ----------------------------------------------------
        # SCROLL
        # ----------------------------------------------------

        layout.addSpacing(
            28
        )

        scroll = DashboardScrollArea()

        scroll.setObjectName(
            "dashboard_scroll"
        )

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        content = QWidget()

        content.setObjectName(
            "dashboard_scroll_content"
        )
        content.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        content.setMinimumWidth(
            0
        )

        content.setMaximumWidth(
            16777215
        )

        self.content_layout = QVBoxLayout(
            content
        )

        self.content_layout.setContentsMargins(
            0,
            0,
            8,
            0,
        )

        self.content_layout.setSpacing(
            12
        )

        self.content_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        scroll.setWidget(
            content
        )

        # The dashboard is vertically scrollable but must always fill
        # the available width when the main window is resized/maximized.
        scroll.viewport().setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        layout.addWidget(
            scroll,
            1,
        )

        # ----------------------------------------------------
        # STYLING
        # ----------------------------------------------------

        self.setStyleSheet(
            """
            QWidget {
                font-family: Arial;
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

            QScrollArea#dashboard_scroll {
                background-color: transparent;
                border: none;
            }

            QWidget#dashboard_scroll_content {
                background-color: transparent;
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

            QFrame#month_selector {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
            }

            QLabel#month_label {
                color: #0F172A;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#month_arrow {
                background-color: transparent;
                color: #475569;
                border: none;
                border-radius: 6px;
                padding: 0px;
                margin: 0px;
                text-align: center;
                font-family: Arial;
                font-size: 20px;
                font-weight: 500;
            }

            QPushButton#month_arrow:hover {
                background-color: transparent;
                color: #334155;
            }

            QFrame#dashboard_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }

            QFrame#dashboard_card:hover {
                border-color: #CBD5E1;
            }

            QFrame#metric_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }

            QFrame#metric_card:hover {
                border-color: #CBD5E1;
            }

            QLabel#metric_title {
                color: #64748B;
                font-size: 13px;
                font-weight: 500;
            }

            QLabel#metric_value {
                color: #0F172A;
                font-family: ".AppleSystemUIFont";
                font-size: 21px;
                font-weight: 700;
                font-style: normal;
            }

            QLabel#metric_change {
                color: #94A3B8;
                font-size: 11px;
            }

            QLabel#section_title {
                color: #0F172A;
                font-size: 16px;
                font-weight: 700;
            }

            QLabel#section_action {
                color: #64748B;
                font-size: 12px;
                font-weight: 500;
            }

            QLabel#normal_label {
                color: #0F172A;
                font-size: 13px;
            }

            QLabel#bold_label {
                color: #0F172A;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#positive_label {
                color: #15803D;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#negative_label {
                color: #B91C1C;
                font-size: 13px;
                font-weight: 600;
            }

            QLabel#muted_label {
                color: #94A3B8;
                font-size: 11px;
            }

            QFrame#category_row,
            QFrame#account_row,
            QFrame#transaction_row,
            QFrame#recurring_row {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }

            QFrame#category_row:hover,
            QFrame#account_row:hover,
            QFrame#transaction_row:hover,
            QFrame#recurring_row:hover {
                background-color: #F1F5F9;
                border-color: #CBD5E1;
            }

            QPushButton#quick_action {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
                padding: 0 16px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton#quick_action:hover {
                background-color: #F1F5F9;
                color: #0F172A;
                border-color: #CBD5E1;
            }

            QFrame#progress_background {
                background-color: #E2E8F0;
                border-radius: 3px;
            }

            QFrame#progress_fill {
                background-color: #0F172A;
                border-radius: 3px;
            }

            QScrollArea#recurring_scroll {
                background-color: #FFFFFF;
                border: none;
            }

            QScrollArea#recurring_scroll > QWidget {
                background-color: #FFFFFF;
                border: none;
            }

            QWidget#recurring_scroll_content {
                background-color: #FFFFFF;
            }
            """
        )

    # ========================================================
    # RESPONSIVE RESIZE
    # ========================================================

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)

        scroll = self.findChild(
            DashboardScrollArea,
            "dashboard_scroll",
        )

        if scroll is not None:
            scroll.sync_content_width()

        if self.content_layout is not None:
            self.content_layout.invalidate()
            self.content_layout.activate()

    # ========================================================
    # DATA
    # ========================================================

    def showEvent(self, event) -> None:
        """Always reload Dashboard data when the page becomes visible.

        Transactions can be created from the Transactions page (or from
        another dialog), so relying only on the Dashboard's own
        AddTransaction button is not enough. Refreshing on show guarantees
        that KPIs, balances, charts and recent transactions reflect the
        latest database state immediately when returning to Dashboard.
        """
        super().showEvent(event)
        self.refresh()

    def refresh(self) -> None:

        try:
            self.user_name = get_user_name()
        except Exception:
            self.user_name = "User"

        if not self.user_name:
            self.user_name = "User"

        self.load_data()

        if self.month_label:

            self.month_label.setText(
                short_month_name(
                    self.selected_year,
                    self.selected_month,
                )
            )

        now_hour = datetime.now().hour

        if now_hour < 12:
            greeting = "Good morning"
        elif now_hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        if hasattr(self, "page_subtitle"):
            self.page_subtitle.setText(
                f"{greeting}, {self.user_name}."
            )

        self.rebuild_content()

    def load_data(self) -> None:

        try:

            self.accounts = list_accounts(
                include_archived=False
            )

        except Exception:

            self.accounts = []

        try:

            self.transactions = (
                list_transactions()
            )

        except Exception:

            self.transactions = []

        try:

            self.categories = (
                list_categories(
                    include_inactive=False
                )
            )

        except TypeError:

            try:

                self.categories = (
                    list_categories()
                )

            except Exception:

                self.categories = []

        except Exception:

            self.categories = []

        try:

            self.recurring = (
                list_recurring_transactions(
                    include_inactive=False
                )
            )

        except TypeError:

            try:

                self.recurring = (
                    list_recurring_transactions()
                )

            except Exception:

                self.recurring = []

        except Exception:

            self.recurring = []

        self.calculate_values()

    def calculate_values(self) -> None:

        self.total_balance = 0

        for account in self.accounts:

            account_id = row_get(
                account,
                "id",
            )

            try:

                balance = (
                    get_current_balance(
                        account_id
                    )
                )

                self.total_balance += int(
                    balance
                )

            except Exception:

                self.total_balance += int(
                    row_get(
                        account,
                        "starting_balance_cents",
                        0,
                    )
                )

        start = month_start(
            self.selected_year,
            self.selected_month,
        )

        end = month_end(
            self.selected_year,
            self.selected_month,
        )

        self.month_transactions = []

        for transaction in self.transactions:

            transaction_date = (
                self.parse_date(
                    row_get(
                        transaction,
                        "transaction_date",
                    )
                )
            )

            if not transaction_date:
                continue

            if (
                start
                <= transaction_date
                <= end
            ):

                self.month_transactions.append(
                    transaction
                )

        self.month_income = 0
        self.month_expenses = 0

        for transaction in (
            self.month_transactions
        ):

            amount = int(
                row_get(
                    transaction,
                    "amount_cents",
                    0,
                )
            )

            if amount > 0:

                self.month_income += amount

            elif amount < 0:

                self.month_expenses += abs(
                    amount
                )

        self.month_net = (
            self.month_income
            - self.month_expenses
        )

    # ========================================================
    # CONTENT
    # ========================================================

    def clear_layout(
        self,
        layout,
    ) -> None:
        """Recursively remove widgets and nested layouts.

        Dashboard rows are stored as nested QHBoxLayouts inside the main
        QVBoxLayout.  Removing only item.widget() leaves those nested
        layouts and their child widgets alive, which caused duplicate
        Dashboard content after every refresh/navigation.
        """

        while layout.count():
            item = layout.takeAt(0)

            child_layout = item.layout()

            if child_layout is not None:
                self.clear_layout(child_layout)
                child_layout.deleteLater()
                continue

            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

    def rebuild_content(self) -> None:

        if not self.content_layout:
            return

        self.clear_layout(
            self.content_layout
        )

        # ----------------------------------------------------
        # KPI CARDS
        # ----------------------------------------------------

        metrics = QHBoxLayout()

        metrics.setSpacing(
            12
        )

        metrics.addWidget(
            self.create_metric_card(
                "Total balance",
                format_money(
                    self.total_balance
                ),
                "Active accounts",
                "neutral",
                self.open_balance_modal,
            )
        )

        metrics.addWidget(
            self.create_metric_card(
                "Income",
                format_money(
                    self.month_income
                ),
                short_month_name(
                    self.selected_year,
                    self.selected_month,
                ),
                "positive",
                self.open_income_modal,
            )
        )

        metrics.addWidget(
            self.create_metric_card(
                "Expenses",
                format_money(
                    self.month_expenses
                ),
                short_month_name(
                    self.selected_year,
                    self.selected_month,
                ),
                "negative",
                self.open_expenses_modal,
            )
        )

        metrics.addWidget(
            self.create_metric_card(
                "Net cashflow",
                format_signed_money(
                    self.month_net
                ),
                "Income − expenses",
                (
                    "positive"
                    if self.month_net >= 0
                    else "negative"
                ),
                self.open_cashflow_modal,
            )
        )

        self.content_layout.addLayout(
            metrics
        )

        # ----------------------------------------------------
        # QUICK ACTIONS
        # ----------------------------------------------------

        quick_actions = QHBoxLayout()

        quick_actions.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        quick_actions.setSpacing(
            10
        )

        quick_actions.addWidget(
            self.create_quick_button(
                "Transactions",
                lambda: self.navigate_to(1),
            ),
            1,
        )

        quick_actions.addWidget(
            self.create_quick_button(
                "Accounts",
                lambda: self.navigate_to(2),
            ),
            1,
        )

        quick_actions.addWidget(
            self.create_quick_button(
                "Categories",
                lambda: self.navigate_to(3),
            ),
            1,
        )

        quick_actions.addWidget(
            self.create_quick_button(
                "Recurring",
                self.open_recurring_modal,
            ),
            1,
        )

        self.content_layout.addLayout(
            quick_actions
        )

        # ----------------------------------------------------
        # CASHFLOW + SPENDING
        # ----------------------------------------------------

        top_grid = QHBoxLayout()

        top_grid.setSpacing(
            12
        )

        top_grid.addWidget(
            self.create_cashflow_card(),
            3,
        )

        top_grid.addWidget(
            self.create_spending_card(),
            2,
        )

        self.content_layout.addLayout(
            top_grid
        )

        # ----------------------------------------------------
        # ACCOUNTS + TRANSACTIONS
        # ----------------------------------------------------

        middle_grid = QHBoxLayout()

        middle_grid.setSpacing(
            12
        )

        middle_grid.addWidget(
            self.create_accounts_card(),
            1,
        )

        middle_grid.addWidget(
            self.create_recent_transactions_card(),
            2,
        )

        self.content_layout.addLayout(
            middle_grid
        )

        # ----------------------------------------------------
        # RECURRING + INSIGHTS
        # ----------------------------------------------------

        bottom_grid = QHBoxLayout()

        bottom_grid.setSpacing(
            12
        )

        bottom_grid.addWidget(
            self.create_recurring_card(),
            1,
        )

        bottom_grid.addWidget(
            self.create_insights_card(),
            1,
        )

        self.content_layout.addLayout(
            bottom_grid
        )

        self.content_layout.addSpacing(
            8
        )

    # ========================================================
    # QUICK BUTTON
    # ========================================================

    def create_quick_button(
        self,
        text: str,
        callback,
    ) -> QPushButton:

        button = QPushButton(
            text
        )

        button.setObjectName(
            "quick_action"
        )

        button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        button.setFixedHeight(
            44
        )

        button.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        button.clicked.connect(
            callback
        )

        return button

    # ========================================================
    # NAVIGATION
    # ========================================================

    def navigate_to(
        self,
        index: int,
    ) -> None:

        main_window = (
            QApplication.activeWindow()
        )

        if not main_window:
            return

        pages = getattr(
            main_window,
            "pages",
            None,
        )

        if pages is not None:

            pages.setCurrentIndex(
                index
            )

    # ========================================================
    # METRIC CARD
    # ========================================================

    def create_metric_card(
        self,
        title: str,
        value: str,
        subtitle: str,
        value_type: str,
        callback,
    ) -> QWidget:

        card = ClickableCard(
            object_name="metric_card"
        )

        card.setMinimumHeight(
            94
        )

        card.setMaximumHeight(
            102
        )

        card.clicked.connect(
            callback
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            15,
            11,
            15,
            10,
        )

        layout.setSpacing(
            2
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "metric_title"
        )

        value_label = QLabel(
            value
        )

        value_label.setObjectName(
            "metric_value"
        )

        if value_type == "positive":

            value_label.setStyleSheet(
                "color: #15803D;"
            )

        elif value_type == "negative":

            value_label.setStyleSheet(
                "color: #B91C1C;"
            )

        subtitle_label = QLabel(
            subtitle
        )

        subtitle_label.setObjectName(
            "metric_change"
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            value_label
        )

        layout.addWidget(
            subtitle_label
        )

        for child in (
            title_label,
            value_label,
            subtitle_label,
        ):

            child.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents
            )

        return card

    # ========================================================
    # CASHFLOW CARD
    # ========================================================

    def create_cashflow_card(
        self,
    ) -> QWidget:

        card = ClickableCard()

        card.clicked.connect(
            self.open_cashflow_modal
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            16,
            14,
            16,
            12,
        )

        layout.setSpacing(
            7
        )

        header = QHBoxLayout()

        title = QLabel(
            "Cashflow"
        )

        title.setObjectName(
            "section_title"
        )

        header.addWidget(
            title
        )

        header.addStretch()

        income_label = QLabel(
            "Income "
            + format_money(
                self.month_income
            )
        )

        income_label.setStyleSheet(
            """
            color:#15803D;
            font-size:11px;
            font-weight:600;
            """
        )

        expenses_label = QLabel(
            "Expenses "
            + format_money(
                self.month_expenses
            )
        )

        expenses_label.setStyleSheet(
            """
            color:#B91C1C;
            font-size:11px;
            font-weight:600;
            """
        )

        header.addWidget(
            income_label
        )

        header.addSpacing(
            10
        )

        header.addWidget(
            expenses_label
        )

        layout.addLayout(
            header
        )

        chart = CashflowChart()

        days = calendar.monthrange(
            self.selected_year,
            self.selected_month,
        )[1]

        income = [
            0 for _ in range(days)
        ]

        expenses = [
            0 for _ in range(days)
        ]

        for transaction in (
            self.month_transactions
        ):

            transaction_date = (
                self.parse_date(
                    row_get(
                        transaction,
                        "transaction_date",
                    )
                )
            )

            if not transaction_date:
                continue

            index = (
                transaction_date.day
                - 1
            )

            amount = int(
                row_get(
                    transaction,
                    "amount_cents",
                    0,
                )
            )

            if amount > 0:

                income[index] += amount

            elif amount < 0:

                expenses[index] += abs(
                    amount
                )

        labels = [
            str(
                index + 1
            )
            for index in range(days)
        ]

        chart.set_data(
            income,
            expenses,
            labels,
        )

        layout.addWidget(
            chart
        )

        footer = QLabel(
            "Daily income vs. expenses"
        )

        footer.setObjectName(
            "muted_label"
        )

        footer.setAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        layout.addWidget(
            footer
        )

        return card

    # ========================================================
    # SPENDING CARD
    # ========================================================

    def create_spending_card(
        self,
    ) -> QWidget:

        card = ClickableCard()

        card.clicked.connect(
            self.open_spending_modal
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            15,
            14,
            15,
            13,
        )

        layout.setSpacing(
            8
        )

        header = QHBoxLayout()

        title = QLabel(
            "Spending by category"
        )

        title.setObjectName(
            "section_title"
        )

        header.addWidget(
            title
        )

        header.addStretch()

        action = QLabel(
            "View all ›"
        )

        action.setObjectName(
            "section_action"
        )

        header.addWidget(
            action
        )

        layout.addLayout(
            header
        )

        totals = {}

        for transaction in (
            self.month_transactions
        ):

            amount = int(
                row_get(
                    transaction,
                    "amount_cents",
                    0,
                )
            )

            if amount >= 0:
                continue

            category = (
                row_get(
                    transaction,
                    "category_name",
                )
                or "Uncategorized"
            )

            totals[category] = (
                totals.get(
                    category,
                    0,
                )
                + abs(amount)
            )

        sorted_categories = sorted(
            totals.items(),
            key=lambda item: item[1],
            reverse=True,
        )

        total = sum(
            totals.values()
        )

        if not sorted_categories:

            empty = QLabel(
                "No expenses this month."
            )

            empty.setObjectName(
                "muted_label"
            )

            layout.addWidget(
                empty
            )

        else:

            for category, amount in (
                sorted_categories[:4]
            ):

                percentage = (
                    amount / total * 100
                    if total
                    else 0
                )

                row = QFrame()

                row.setObjectName(
                    "category_row"
                )

                row.setCursor(
                    Qt.CursorShape.PointingHandCursor
                )

                row_layout = QVBoxLayout(
                    row
                )

                row_layout.setContentsMargins(
                    10,
                    7,
                    10,
                    7,
                )

                row_layout.setSpacing(
                    3
                )

                top = QHBoxLayout()

                name = QLabel(
                    str(category)
                )

                name.setObjectName(
                    "normal_label"
                )

                amount_label = QLabel(
                    format_money(
                        amount
                    )
                )

                amount_label.setObjectName(
                    "bold_label"
                )

                top.addWidget(
                    name
                )

                top.addStretch()

                top.addWidget(
                    amount_label
                )

                row_layout.addLayout(
                    top
                )

                progress = QProgressBar()

                progress.setRange(0, 100)
                progress.setValue(
                    max(
                        0,
                        min(
                            100,
                            int(round(percentage)),
                        ),
                    )
                )
                progress.setTextVisible(False)
                progress.setFixedHeight(5)
                progress.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Fixed,
                )
                progress.setStyleSheet(
                    """
                    QProgressBar {
                        background:#E2E8F0;
                        border:none;
                        border-radius:3px;
                    }
                    QProgressBar::chunk {
                        background:#0F172A;
                        border:none;
                        border-radius:3px;
                    }
                    """
                )

                row_layout.addWidget(
                    progress
                )

                percentage_label = QLabel(
                    f"{percentage:.0f}%"
                )

                percentage_label.setObjectName(
                    "muted_label"
                )

                row_layout.addWidget(
                    percentage_label
                )

                def category_click(
                    event,
                    category=category,
                ):

                    self.open_category_modal(
                        category
                    )

                row.mousePressEvent = (
                    category_click
                )

                for child in (
                    name,
                    amount_label,
                    progress,
                    percentage_label,
                ):

                    child.setAttribute(
                        Qt.WidgetAttribute.WA_TransparentForMouseEvents
                    )

                layout.addWidget(
                    row
                )

        return card

    # ========================================================
    # ACCOUNTS CARD
    # ========================================================

    def create_accounts_card(
        self,
    ) -> QWidget:

        card = ClickableCard()

        card.clicked.connect(
            lambda: self.navigate_to(2)
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            15,
            14,
            15,
            13,
        )

        layout.setSpacing(
            8
        )

        header = QHBoxLayout()

        title = QLabel(
            "Accounts"
        )

        title.setObjectName(
            "section_title"
        )

        header.addWidget(
            title
        )

        header.addStretch()

        count_label = QLabel(
            f"{len(self.accounts)} active"
        )

        count_label.setObjectName(
            "muted_label"
        )

        header.addWidget(
            count_label
        )

        layout.addLayout(
            header
        )

        if not self.accounts:

            empty = QLabel(
                "No active accounts."
            )

            empty.setObjectName(
                "muted_label"
            )

            layout.addWidget(
                empty
            )

        else:

            for account in self.accounts[:5]:

                account_id = row_get(
                    account,
                    "id",
                )

                name_value = row_get(
                    account,
                    "name",
                    "Account",
                )

                try:

                    balance = (
                        get_current_balance(
                            account_id
                        )
                    )

                except Exception:

                    balance = row_get(
                        account,
                        "starting_balance_cents",
                        0,
                    )

                row = QFrame()

                row.setObjectName(
                    "account_row"
                )

                row.setCursor(
                    Qt.CursorShape.PointingHandCursor
                )

                row_layout = QHBoxLayout(
                    row
                )

                row_layout.setContentsMargins(
                    10,
                    9,
                    10,
                    9,
                )

                name = QLabel(
                    str(name_value)
                )

                name.setObjectName(
                    "normal_label"
                )

                balance_label = QLabel(
                    format_money(
                        int(balance)
                    )
                )

                balance_label.setObjectName(
                    "bold_label"
                )

                row_layout.addWidget(
                    name
                )

                row_layout.addStretch()

                row_layout.addWidget(
                    balance_label
                )

                def account_click(
                    event,
                    account_id=account_id,
                ):

                    self.open_account_modal(
                        account_id
                    )

                row.mousePressEvent = (
                    account_click
                )

                name.setAttribute(
                    Qt.WidgetAttribute.WA_TransparentForMouseEvents
                )

                balance_label.setAttribute(
                    Qt.WidgetAttribute.WA_TransparentForMouseEvents
                )

                layout.addWidget(
                    row
                )

        return card

    # ========================================================
    # RECENT TRANSACTIONS
    # ========================================================

    def create_recent_transactions_card(
        self,
    ) -> QWidget:

        card = ClickableCard()

        card.clicked.connect(
            lambda: self.navigate_to(1)
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            15,
            14,
            15,
            13,
        )

        layout.setSpacing(
            8
        )

        header = QHBoxLayout()

        title = QLabel(
            "Recent transactions"
        )

        title.setObjectName(
            "section_title"
        )

        header.addWidget(
            title
        )

        header.addStretch()

        action = QLabel(
            "View all ›"
        )

        action.setObjectName(
            "section_action"
        )

        header.addWidget(
            action
        )

        layout.addLayout(
            header
        )

        transactions = sorted(
            self.transactions,
            key=lambda transaction: (
                self.parse_date(
                    row_get(
                        transaction,
                        "transaction_date",
                    )
                )
                or date.min
            ),
            reverse=True,
        )

        if not transactions:

            empty = QLabel(
                "No transactions yet."
            )

            empty.setObjectName(
                "muted_label"
            )

            layout.addWidget(
                empty
            )

        else:

            for transaction in (
                transactions[:5]
            ):

                row = QFrame()

                row.setObjectName(
                    "transaction_row"
                )

                row.setCursor(
                    Qt.CursorShape.PointingHandCursor
                )

                row_layout = QHBoxLayout(
                    row
                )

                row_layout.setContentsMargins(
                    10,
                    8,
                    10,
                    8,
                )

                row_layout.setSpacing(
                    9
                )

                info = QVBoxLayout()

                info.setSpacing(
                    2
                )

                note = (
                    row_get(
                        transaction,
                        "note",
                    )
                    or row_get(
                        transaction,
                        "category_name",
                    )
                    or "Transaction"
                )

                note_label = QLabel(
                    str(note)
                )

                note_label.setObjectName(
                    "normal_label"
                )

                category = (
                    row_get(
                        transaction,
                        "category_name",
                    )
                    or "Uncategorized"
                )

                category_label = QLabel(
                    str(category)
                )

                category_label.setObjectName(
                    "muted_label"
                )

                info.addWidget(
                    note_label
                )

                info.addWidget(
                    category_label
                )

                row_layout.addLayout(
                    info
                )

                row_layout.addStretch()

                transaction_date = (
                    self.parse_date(
                        row_get(
                            transaction,
                            "transaction_date",
                        )
                    )
                )

                date_label = QLabel(
                    transaction_date.strftime(
                        "%d.%m."
                    )
                    if transaction_date
                    else ""
                )

                date_label.setObjectName(
                    "muted_label"
                )

                row_layout.addWidget(
                    date_label
                )

                amount = int(
                    row_get(
                        transaction,
                        "amount_cents",
                        0,
                    )
                )

                amount_label = QLabel(
                    format_signed_money(
                        amount
                    )
                )

                amount_label.setObjectName(
                    (
                        "positive_label"
                        if amount >= 0
                        else "negative_label"
                    )
                )

                row_layout.addWidget(
                    amount_label
                )

                transaction_id = row_get(
                    transaction,
                    "id",
                )

                def transaction_click(
                    event,
                    transaction_id=transaction_id,
                ):

                    self.open_transaction_modal(
                        transaction_id
                    )

                row.mousePressEvent = (
                    transaction_click
                )

                for child in (
                    note_label,
                    category_label,
                    date_label,
                    amount_label,
                ):

                    child.setAttribute(
                        Qt.WidgetAttribute.WA_TransparentForMouseEvents
                    )

                layout.addWidget(
                    row
                )

        return card

    # ========================================================
    # RECURRING CARD
    # ========================================================

    def create_recurring_card(
        self,
    ) -> QWidget:

        card = ClickableCard()

        card.setMinimumHeight(
            230
        )

        card.setMaximumHeight(
            270
        )

        card.clicked.connect(
            self.open_recurring_modal
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            15,
            14,
            15,
            13,
        )

        layout.setSpacing(
            8
        )

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = QHBoxLayout()

        title = QLabel(
            "Upcoming recurring"
        )

        title.setObjectName(
            "section_title"
        )

        header.addWidget(
            title
        )

        header.addStretch()

        count_label = QLabel(
            str(
                len(self.recurring)
            )
        )

        count_label.setObjectName(
            "muted_label"
        )

        header.addWidget(
            count_label
        )

        layout.addLayout(
            header
        )

        # ----------------------------------------------------
        # INNER SCROLL
        # ----------------------------------------------------

        scroll = QScrollArea()

        scroll.setObjectName(
            "recurring_scroll"
        )

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        scroll.setStyleSheet(
            """
            QScrollArea#recurring_scroll {
                background: #FFFFFF;
                border: none;
            }

            QScrollArea#recurring_scroll > QWidget {
                background: #FFFFFF;
                border: none;
            }

            QScrollArea#recurring_scroll QWidget {
                background: #FFFFFF;
            }

            QScrollBar:vertical {
                width: 8px;
                background: transparent;
                margin: 2px 0;
            }

            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border: none;
                border-radius: 4px;
                min-height: 25px;
                margin: 0 0 0 0;
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

        scroll_content = QWidget()

        scroll_content.setObjectName(
            "recurring_scroll_content"
        )

        scroll_content.setStyleSheet(
            "background: #FFFFFF;"
        )

        scroll_layout = QVBoxLayout(
            scroll_content
        )

        scroll_layout.setContentsMargins(
            0,
            0,
            3,
            0,
        )

        scroll_layout.setSpacing(
            7
        )

        if not self.recurring:

            empty = QLabel(
                "No recurring transactions."
            )

            empty.setObjectName(
                "muted_label"
            )

            scroll_layout.addWidget(
                empty
            )

        else:

            sorted_recurring = sorted(
                self.recurring,
                key=lambda item: str(
                    row_get(
                        item,
                        "next_run_date",
                        "",
                    )
                ),
            )

            for item in sorted_recurring:

                row = QFrame()

                row.setObjectName(
                    "recurring_row"
                )

                row.setCursor(
                    Qt.CursorShape.PointingHandCursor
                )

                row_layout = QHBoxLayout(
                    row
                )

                row_layout.setContentsMargins(
                    10,
                    8,
                    10,
                    8,
                )

                row_layout.setSpacing(
                    8
                )

                info = QVBoxLayout()

                info.setSpacing(
                    2
                )

                name_label = QLabel(
                    str(
                        row_get(
                            item,
                            "name",
                            "Recurring",
                        )
                    )
                )

                name_label.setObjectName(
                    "normal_label"
                )

                frequency_label = QLabel(
                    str(
                        row_get(
                            item,
                            "frequency",
                            "",
                        )
                    ).capitalize()
                )

                frequency_label.setObjectName(
                    "muted_label"
                )

                info.addWidget(
                    name_label
                )

                info.addWidget(
                    frequency_label
                )

                row_layout.addLayout(
                    info,
                    1,
                )

                next_run = QLabel(
                    str(
                        row_get(
                            item,
                            "next_run_date",
                            "",
                        )
                    )
                )

                next_run.setObjectName(
                    "muted_label"
                )

                row_layout.addWidget(
                    next_run
                )

                amount = int(
                    row_get(
                        item,
                        "amount_cents",
                        0,
                    )
                )

                if (
                    row_get(
                        item,
                        "kind",
                    )
                    == "expense"
                ):

                    amount = -abs(
                        amount
                    )

                else:

                    amount = abs(
                        amount
                    )

                amount_label = QLabel(
                    format_signed_money(
                        amount
                    )
                )

                amount_label.setObjectName(
                    (
                        "positive_label"
                        if amount >= 0
                        else "negative_label"
                    )
                )

                row_layout.addWidget(
                    amount_label
                )

                recurring_id = row_get(
                    item,
                    "id",
                )

                def recurring_click(
                    event,
                    recurring_id=recurring_id,
                ):

                    self.open_recurring_detail_modal(
                        recurring_id
                    )

                row.mousePressEvent = (
                    recurring_click
                )

                for child in (
                    name_label,
                    frequency_label,
                    next_run,
                    amount_label,
                ):

                    child.setAttribute(
                        Qt.WidgetAttribute.WA_TransparentForMouseEvents
                    )

                scroll_layout.addWidget(
                    row
                )

        scroll_layout.addStretch()

        scroll.setWidget(
            scroll_content
        )

        layout.addWidget(
            scroll,
            1,
        )

        return card

    # ========================================================
    # INSIGHTS
    # ========================================================

    def create_insights_card(
        self,
    ) -> QWidget:

        card = ClickableCard()

        card.setMinimumHeight(
            230
        )

        card.clicked.connect(
            self.open_insights_modal
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            15,
            14,
            15,
            13,
        )

        layout.setSpacing(
            8
        )

        title = QLabel(
            "Financial insights"
        )

        title.setObjectName(
            "section_title"
        )

        layout.addWidget(
            title
        )

        insights = self.build_insights()

        for text in insights[:4]:

            row = QFrame()

            row.setObjectName(
                "category_row"
            )

            row_layout = QHBoxLayout(
                row
            )

            row_layout.setContentsMargins(
                10,
                9,
                10,
                9,
            )

            dot = QLabel(
                "•"
            )

            dot.setStyleSheet(
                """
                color:#0F172A;
                font-size:17px;
                font-weight:700;
                background:transparent;
                """
            )

            label = QLabel(
                text
            )

            label.setObjectName(
                "normal_label"
            )

            label.setWordWrap(
                True
            )

            row_layout.addWidget(
                dot
            )

            row_layout.addWidget(
                label,
                1,
            )

            dot.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents
            )

            label.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents
            )

            layout.addWidget(
                row
            )

        return card

    def build_insights(self) -> list[str]:

        insights = []

        if (
            self.month_income == 0
            and self.month_expenses == 0
        ):

            insights.append(
                "No activity recorded this month."
            )

        elif self.month_net > 0:

            rate = (
                self.month_net
                / self.month_income
                * 100
                if self.month_income
                else 0
            )

            insights.append(
                f"Positive cashflow — "
                f"{rate:.0f}% of income remains."
            )

        elif self.month_net < 0:

            insights.append(
                "Expenses are higher than income this month."
            )

        else:

            insights.append(
                "Income and expenses are currently balanced."
            )

        totals = {}

        for transaction in (
            self.month_transactions
        ):

            amount = int(
                row_get(
                    transaction,
                    "amount_cents",
                    0,
                )
            )

            if amount >= 0:
                continue

            category = (
                row_get(
                    transaction,
                    "category_name",
                )
                or "Uncategorized"
            )

            totals[category] = (
                totals.get(
                    category,
                    0,
                )
                + abs(amount)
            )

        if totals:

            category = max(
                totals,
                key=totals.get,
            )

            insights.append(
                "Top spending category: "
                f"{category} "
                f"({format_money(totals[category])})."
            )

        if self.accounts:

            insights.append(
                f"You have {len(self.accounts)} "
                f"active account"
                f"{'s' if len(self.accounts) != 1 else ''}."
            )

        return insights

    # ========================================================
    # MONTH
    # ========================================================

    def go_previous_month(
        self,
    ) -> None:

        (
            self.selected_year,
            self.selected_month,
        ) = previous_month(
            self.selected_year,
            self.selected_month,
        )

        self.refresh()

    def go_next_month(
        self,
    ) -> None:

        if self.selected_month == 12:

            self.selected_year += 1
            self.selected_month = 1

        else:

            self.selected_month += 1

        self.refresh()

    # ========================================================
    # DATE
    # ========================================================

    @staticmethod
    def parse_date(
        value,
    ) -> Optional[date]:

        if value is None:
            return None

        if isinstance(
            value,
            datetime,
        ):
            return value.date()

        if isinstance(
            value,
            date,
        ):
            return value

        value = str(
            value
        )

        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%d.%m.%Y",
        ]

        for fmt in formats:

            try:

                return datetime.strptime(
                    value,
                    fmt,
                ).date()

            except ValueError:

                pass

        return None

    # ========================================================
    # GENERIC INFO MODAL
    # ========================================================

    def create_info_modal(
        self,
        title: str,
        subtitle: str,
    ) -> Optional[Modal]:

        main_window = (
            QApplication.activeWindow()
        )

        if not main_window:
            return None

        modal = Modal(
            title=title,
            subtitle=subtitle,
            primary_text="Close",
            cancel_text="",
        )

        modal.cancel_button.hide()

        return modal

    def add_modal_info_row(
        self,
        modal: Modal,
        label_text: str,
        value_text: str,
        value_style: str = "normal",
    ) -> None:

        row = QFrame()

        row.setStyleSheet(
            """
            QFrame {
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }
            """
        )

        layout = QVBoxLayout(
            row
        )

        layout.setContentsMargins(
            14,
            10,
            14,
            10,
        )

        layout.setSpacing(
            3
        )

        label = QLabel(
            label_text
        )

        label.setStyleSheet(
            """
            color:#64748B;
            font-size:11px;
            font-weight:600;
            background:transparent;
            border:none;
            """
        )

        value = QLabel(
            value_text
        )

        if value_style == "positive":

            value.setStyleSheet(
                """
                color:#15803D;
                font-size:16px;
                font-weight:700;
                background:transparent;
                border:none;
                """
            )

        elif value_style == "negative":

            value.setStyleSheet(
                """
                color:#B91C1C;
                font-size:16px;
                font-weight:700;
                background:transparent;
                border:none;
                """
            )

        else:

            value.setStyleSheet(
                """
                color:#0F172A;
                font-size:16px;
                font-weight:700;
                background:transparent;
                border:none;
                """
            )

        layout.addWidget(
            label
        )

        layout.addWidget(
            value
        )

        modal.add_content(
            row
        )

    def show_modal(
        self,
        modal: Modal,
    ) -> None:

        main_window = (
            QApplication.activeWindow()
        )

        if not main_window:
            return

        modal.submitted.connect(
            main_window.close_modal
        )

        main_window.show_modal(
            modal
        )

    # ========================================================
    # BALANCE
    # ========================================================

    def open_balance_modal(
        self,
    ) -> None:

        modal = self.create_info_modal(
            "Total balance",
            "Current balance across all active accounts.",
        )

        if not modal:
            return

        self.add_modal_info_row(
            modal,
            "CURRENT BALANCE",
            format_money(
                self.total_balance
            ),
            (
                "positive"
                if self.total_balance >= 0
                else "negative"
            ),
        )

        self.add_modal_info_row(
            modal,
            "ACTIVE ACCOUNTS",
            str(
                len(self.accounts)
            ),
        )

        self.show_modal(
            modal
        )

    # ========================================================
    # INCOME
    # ========================================================

    def open_income_modal(
        self,
    ) -> None:

        modal = self.create_info_modal(
            "Income",
            (
                "Income recorded during "
                f"{month_name(self.selected_year, self.selected_month)}."
            ),
        )

        if not modal:
            return

        self.add_modal_info_row(
            modal,
            "TOTAL INCOME",
            format_money(
                self.month_income
            ),
            "positive",
        )

        income_transactions = [
            transaction
            for transaction
            in self.month_transactions
            if int(
                row_get(
                    transaction,
                    "amount_cents",
                    0,
                )
            )
            > 0
        ]

        self.add_modal_info_row(
            modal,
            "TRANSACTIONS",
            str(
                len(
                    income_transactions
                )
            ),
        )

        self.show_modal(
            modal
        )

    # ========================================================
    # EXPENSES
    # ========================================================

    def open_expenses_modal(
        self,
    ) -> None:

        modal = self.create_info_modal(
            "Expenses",
            (
                "Expenses recorded during "
                f"{month_name(self.selected_year, self.selected_month)}."
            ),
        )

        if not modal:
            return

        self.add_modal_info_row(
            modal,
            "TOTAL EXPENSES",
            format_money(
                self.month_expenses
            ),
            "negative",
        )

        expense_transactions = [
            transaction
            for transaction
            in self.month_transactions
            if int(
                row_get(
                    transaction,
                    "amount_cents",
                    0,
                )
            )
            < 0
        ]

        self.add_modal_info_row(
            modal,
            "TRANSACTIONS",
            str(
                len(
                    expense_transactions
                )
            ),
        )

        self.show_modal(
            modal
        )

    # ========================================================
    # CASHFLOW
    # ========================================================

    def open_cashflow_modal(
        self,
    ) -> None:

        modal = self.create_info_modal(
            "Cashflow",
            (
                "Monthly income and expenses "
                f"for {month_name(self.selected_year, self.selected_month)}."
            ),
        )

        if not modal:
            return

        self.add_modal_info_row(
            modal,
            "INCOME",
            format_money(
                self.month_income
            ),
            "positive",
        )

        self.add_modal_info_row(
            modal,
            "EXPENSES",
            format_money(
                self.month_expenses
            ),
            "negative",
        )

        self.add_modal_info_row(
            modal,
            "NET CASHFLOW",
            format_signed_money(
                self.month_net
            ),
            (
                "positive"
                if self.month_net >= 0
                else "negative"
            ),
        )

        self.show_modal(
            modal
        )

    # ========================================================
    # SPENDING
    # ========================================================

    def open_spending_modal(
        self,
    ) -> None:

        totals = {}

        for transaction in (
            self.month_transactions
        ):

            amount = int(
                row_get(
                    transaction,
                    "amount_cents",
                    0,
                )
            )

            if amount >= 0:
                continue

            category = (
                row_get(
                    transaction,
                    "category_name",
                )
                or "Uncategorized"
            )

            totals[category] = (
                totals.get(
                    category,
                    0,
                )
                + abs(amount)
            )

        modal = self.create_info_modal(
            "Spending by category",
            (
                "Where your money went during "
                f"{month_name(self.selected_year, self.selected_month)}."
            ),
        )

        if not modal:
            return

        if not totals:

            self.add_modal_info_row(
                modal,
                "STATUS",
                "No expenses recorded this month.",
            )

        else:

            for category, amount in sorted(
                totals.items(),
                key=lambda item: item[1],
                reverse=True,
            ):

                self.add_modal_info_row(
                    modal,
                    category.upper(),
                    format_money(
                        amount
                    ),
                    "negative",
                )

        self.show_modal(
            modal
        )

    # ========================================================
    # CATEGORY
    # ========================================================

    def open_category_modal(
        self,
        category: str,
    ) -> None:

        transactions = [
            transaction
            for transaction
            in self.month_transactions
            if (
                row_get(
                    transaction,
                    "category_name",
                )
                or "Uncategorized"
            )
            == category
        ]

        total = 0

        for transaction in transactions:

            amount = int(
                row_get(
                    transaction,
                    "amount_cents",
                    0,
                )
            )

            if amount < 0:

                total += abs(
                    amount
                )

        modal = self.create_info_modal(
            category,
            (
                "Category activity for "
                f"{month_name(self.selected_year, self.selected_month)}."
            ),
        )

        if not modal:
            return

        self.add_modal_info_row(
            modal,
            "TOTAL SPENT",
            format_money(
                total
            ),
            "negative",
        )

        self.add_modal_info_row(
            modal,
            "TRANSACTIONS",
            str(
                len(transactions)
            ),
        )

        self.show_modal(
            modal
        )

    # ========================================================
    # ACCOUNT
    # ========================================================

    def open_account_modal(
        self,
        account_id: int,
    ) -> None:

        account = next(
            (
                account
                for account
                in self.accounts
                if row_get(
                    account,
                    "id",
                )
                == account_id
            ),
            None,
        )

        if not account:
            return

        try:

            balance = (
                get_current_balance(
                    account_id
                )
            )

        except Exception:

            balance = row_get(
                account,
                "starting_balance_cents",
                0,
            )

        modal = self.create_info_modal(
            str(
                row_get(
                    account,
                    "name",
                    "Account",
                )
            ),
            "Current account overview.",
        )

        if not modal:
            return

        self.add_modal_info_row(
            modal,
            "CURRENT BALANCE",
            format_money(
                int(balance)
            ),
            (
                "positive"
                if int(balance) >= 0
                else "negative"
            ),
        )

        self.show_modal(
            modal
        )

    # ========================================================
    # TRANSACTION
    # ========================================================

    def open_transaction_modal(
        self,
        transaction_id: int,
    ) -> None:

        transaction = next(
            (
                transaction
                for transaction
                in self.transactions
                if row_get(
                    transaction,
                    "id",
                )
                == transaction_id
            ),
            None,
        )

        if not transaction:
            return

        note = (
            row_get(
                transaction,
                "note",
            )
            or row_get(
                transaction,
                "category_name",
            )
            or "Transaction"
        )

        amount = int(
            row_get(
                transaction,
                "amount_cents",
                0,
            )
        )

        account_name = (
            row_get(
                transaction,
                "account_name",
            )
            or "Account"
        )

        category_name = (
            row_get(
                transaction,
                "category_name",
            )
            or "Uncategorized"
        )

        transaction_date = (
            row_get(
                transaction,
                "transaction_date",
            )
            or ""
        )

        modal = self.create_info_modal(
            str(note),
            "Transaction details.",
        )

        if not modal:
            return

        self.add_modal_info_row(
            modal,
            "AMOUNT",
            format_signed_money(
                amount
            ),
            (
                "positive"
                if amount >= 0
                else "negative"
            ),
        )

        self.add_modal_info_row(
            modal,
            "ACCOUNT",
            str(account_name),
        )

        self.add_modal_info_row(
            modal,
            "CATEGORY",
            str(category_name),
        )

        self.add_modal_info_row(
            modal,
            "DATE",
            str(transaction_date),
        )

        self.show_modal(
            modal
        )

    # ========================================================
    # RECURRING
    # ========================================================

    def open_recurring_modal(
        self,
    ) -> None:

        modal = self.create_info_modal(
            "Upcoming recurring",
            "Your scheduled recurring transactions.",
        )

        if not modal:
            return

        # ----------------------------------------------------
        # Scrollable modal content
        # ----------------------------------------------------

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        scroll.setMinimumHeight(
            300
        )

        scroll.setStyleSheet(
            """
            QScrollArea {
                background:#FFFFFF;
                border:none;
            }

            QScrollArea > QWidget {
                background:#FFFFFF;
                border:none;
            }

            QScrollArea QWidget {
                background:#FFFFFF;
            }

            QScrollBar:vertical {
                width:8px;
                background:transparent;
                border:none;
                margin:2px 0;
            }

            QScrollBar::handle:vertical {
                background:#CBD5E1;
                border:none;
                border-radius:4px;
                min-height:30px;
                margin:0;
            }

            QScrollBar::handle:vertical:hover {
                background:#94A3B8;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height:0px;
                border:none;
                background:transparent;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background:transparent;
            }
            """
        )

        content = QWidget()

        content.setObjectName(
            "recurring_modal_content"
        )

        content.setStyleSheet(
            "background:#FFFFFF;"
        )

        content_layout = QVBoxLayout(
            content
        )

        content_layout.setContentsMargins(
            2,
            2,
            6,
            2,
        )

        content_layout.setSpacing(
            10
        )

        if not self.recurring:

            empty = QLabel(
                "No recurring transactions."
            )

            empty.setStyleSheet(
                """
                color:#64748B;
                font-size:13px;
                """
            )

            content_layout.addWidget(
                empty
            )

        else:

            sorted_recurring = sorted(
                self.recurring,
                key=lambda item: str(
                    row_get(
                        item,
                        "next_run_date",
                        "",
                    )
                ),
            )

            for item in sorted_recurring:

                row = QFrame()

                row.setStyleSheet(
                    """
                    QFrame {
                        background:#F8FAFC;
                        border:1px solid #E2E8F0;
                        border-radius:10px;
                    }

                    QFrame:hover {
                        background:#F1F5F9;
                        border-color:#CBD5E1;
                    }
                    """
                )

                row_layout = QVBoxLayout(
                    row
                )

                row_layout.setContentsMargins(
                    13,
                    10,
                    13,
                    10,
                )

                row_layout.setSpacing(
                    4
                )

                top = QHBoxLayout()

                name = QLabel(
                    str(
                        row_get(
                            item,
                            "name",
                            "Recurring",
                        )
                    )
                )

                name.setStyleSheet(
                    """
                    color:#0F172A;
                    font-size:14px;
                    font-weight:600;
                    background:transparent;
                    border:none;
                    """
                )

                top.addWidget(
                    name
                )

                top.addStretch()

                amount = int(
                    row_get(
                        item,
                        "amount_cents",
                        0,
                    )
                )

                if (
                    row_get(
                        item,
                        "kind",
                    )
                    == "expense"
                ):

                    amount = -abs(
                        amount
                    )

                else:

                    amount = abs(
                        amount
                    )

                amount_label = QLabel(
                    format_signed_money(
                        amount
                    )
                )

                amount_label.setStyleSheet(
                    (
                        """
                        color:#15803D;
                        font-size:14px;
                        font-weight:700;
                        background:transparent;
                        border:none;
                        """
                        if amount >= 0
                        else
                        """
                        color:#B91C1C;
                        font-size:14px;
                        font-weight:700;
                        background:transparent;
                        border:none;
                        """
                    )
                )

                top.addWidget(
                    amount_label
                )

                row_layout.addLayout(
                    top
                )

                details = QLabel(
                    (
                        f"{str(row_get(item, 'frequency', '')).capitalize()}"
                        f"  •  Next run: "
                        f"{row_get(item, 'next_run_date', '')}"
                    )
                )

                details.setStyleSheet(
                    """
                    color:#64748B;
                    font-size:11px;
                    background:transparent;
                    border:none;
                    """
                )

                row_layout.addWidget(
                    details
                )

                note = row_get(
                    item,
                    "note",
                )

                if note:

                    note_label = QLabel(
                        str(note)
                    )

                    note_label.setWordWrap(
                        True
                    )

                    note_label.setStyleSheet(
                        """
                        color:#94A3B8;
                        font-size:11px;
                        background:transparent;
                        border:none;
                        """
                    )

                    row_layout.addWidget(
                        note_label
                    )

                content_layout.addWidget(
                    row
                )

        content_layout.addStretch()

        scroll.setWidget(
            content
        )

        modal.add_content(
            scroll
        )

        self.show_modal(
            modal
        )

    # ========================================================
    # RECURRING DETAIL
    # ========================================================

    def open_recurring_detail_modal(
        self,
        recurring_id: int,
    ) -> None:

        item = next(
            (
                item
                for item
                in self.recurring
                if row_get(
                    item,
                    "id",
                )
                == recurring_id
            ),
            None,
        )

        if not item:
            return

        amount = int(
            row_get(
                item,
                "amount_cents",
                0,
            )
        )

        if (
            row_get(
                item,
                "kind",
            )
            == "expense"
        ):

            amount = -abs(
                amount
            )

        else:

            amount = abs(
                amount
            )

        modal = self.create_info_modal(
            str(
                row_get(
                    item,
                    "name",
                    "Recurring",
                )
            ),
            "Recurring transaction details.",
        )

        if not modal:
            return

        self.add_modal_info_row(
            modal,
            "AMOUNT",
            format_signed_money(
                amount
            ),
            (
                "positive"
                if amount >= 0
                else "negative"
            ),
        )

        self.add_modal_info_row(
            modal,
            "FREQUENCY",
            str(
                row_get(
                    item,
                    "frequency",
                    "",
                )
            ).capitalize(),
        )

        self.add_modal_info_row(
            modal,
            "NEXT RUN",
            str(
                row_get(
                    item,
                    "next_run_date",
                    "",
                )
            ),
        )

        note = (
            row_get(
                item,
                "note",
            )
            or "No note"
        )

        self.add_modal_info_row(
            modal,
            "NOTE",
            str(note),
        )

        self.show_modal(
            modal
        )

    # ========================================================
    # INSIGHTS
    # ========================================================

    def open_insights_modal(
        self,
    ) -> None:

        modal = self.create_info_modal(
            "Financial insights",
            "Calculated from your recorded Octumo data.",
        )

        if not modal:
            return

        for index, text in enumerate(
            self.build_insights()[:5]
        ):

            self.add_modal_info_row(
                modal,
                f"INSIGHT {index + 1}",
                text,
            )

        self.show_modal(
            modal
        )

    # ========================================================
    # ADD TRANSACTION
    # ========================================================

    def open_add_transaction(
        self,
    ) -> None:

        main_window = QApplication.activeWindow()

        if not main_window:
            return

        # Use the exact same AddTransactionDialog as the
        # Transactions page. This keeps validation, recurring
        # transactions, account/category loading and all other
        # transaction creation logic in one place.
        from app.ui.add_transaction_dialog import (
            AddTransactionDialog,
        )

        dialog = AddTransactionDialog(
            parent=main_window
        )

        dialog.finished.connect(
            self.on_transaction_dialog_finished
        )

        main_window.show_modal(
            dialog
        )

    def on_transaction_dialog_finished(
        self,
    ) -> None:

        main_window = QApplication.activeWindow()

        if main_window and getattr(
            main_window,
            "modal_overlay",
            None,
        ) is not None:
            main_window.close_modal()

        # The transaction is already committed by
        # AddTransactionDialog before finished is emitted.
        # Reload every Dashboard data source so all KPIs,
        # charts, account balances, recent transactions and
        # recurring sections show the new state immediately.
        self.refresh()