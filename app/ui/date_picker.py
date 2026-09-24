from PySide6.QtCore import (
    QDate,
    QEvent,
    QLocale,
    QPoint,
    Qt,
)
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPen,
)
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QCalendarWidget,
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QLabel,
    QStyle,
    QStyledItemDelegate,
    QTableView,
    QToolButton,
)


class OctumoCalendarDelegate(QStyledItemDelegate):
    """
    Custom rendering for calendar days.

    - Selected day: dark rounded rectangle
    - Hovered day: light rounded rectangle
    - Normal days: clean text
    """

    def paint(
        self,
        painter: QPainter,
        option,
        index,
    ) -> None:
        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        rect = option.rect.adjusted(
            4,
            3,
            -4,
            -3,
        )

        selected = bool(
            option.state
            & QStyle.StateFlag.State_Selected
        )

        hovered = bool(
            option.state
            & QStyle.StateFlag.State_MouseOver
        )

        # -------------------------------------------------
        # Background
        # -------------------------------------------------

        if selected:
            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.setBrush(
                QColor("#0F172A")
            )

            painter.drawRoundedRect(
                rect,
                8,
                8,
            )

        elif hovered:
            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.setBrush(
                QColor("#F1F5F9")
            )

            painter.drawRoundedRect(
                rect,
                8,
                8,
            )

        # -------------------------------------------------
        # Date text
        # -------------------------------------------------

        text = index.data(
            Qt.ItemDataRole.DisplayRole
        )

        if text is not None:
            if selected:
                text_color = QColor(
                    "#FFFFFF"
                )
            else:
                text_color = QColor(
                    "#334155"
                )

            painter.setPen(
                text_color
            )

            painter.setFont(
                option.font
            )

            painter.drawText(
                rect,
                Qt.AlignmentFlag.AlignCenter,
                str(text),
            )

        painter.restore()


class OctumoCalendar(QCalendarWidget):
    """
    Custom Octumo calendar.

    - Monday is the first day of the week
    - Three-letter English weekday names
    - No month/year dropdowns
    - Previous/next month arrows only
    - Clean Octumo style
    - Rounded selected date
    - Rounded hover state
    """

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName(
            "octumo_calendar"
        )

        # -------------------------------------------------
        # Calendar configuration
        # -------------------------------------------------

        self.setNavigationBarVisible(
            False
        )

        self.setGridVisible(
            False
        )

        self.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )

        self.setLocale(
            QLocale(
                QLocale.Language.English,
                QLocale.Country.UnitedStates,
            )
        )

        # Monday is the first day.
        # This must be set AFTER the locale.
        self.setFirstDayOfWeek(
            Qt.DayOfWeek.Monday
        )

        # Three-letter weekday names:
        # Mon Tue Wed Thu Fri Sat Sun
        self.setHorizontalHeaderFormat(
            QCalendarWidget.HorizontalHeaderFormat.ShortDayNames
        )

        self.setFixedSize(
            390,
            330,
        )

        self._create_custom_header()

        self._apply_calendar_style()

        self._install_day_delegate()

        self.currentPageChanged.connect(
            self._update_month_label
        )

        self._update_month_label(
            self.yearShown(),
            self.monthShown(),
        )

    def _install_day_delegate(self) -> None:
        """
        Apply custom rendering to the calendar day table.
        """

        calendar_view = self.findChild(
            QTableView,
            "qt_calendar_calendarview",
        )

        if calendar_view is None:
            return

        self._day_delegate = (
            OctumoCalendarDelegate(
                calendar_view
            )
        )

        calendar_view.setItemDelegate(
            self._day_delegate
        )

        calendar_view.setMouseTracking(
            True
        )

        calendar_view.viewport().setMouseTracking(
            True
        )

    def _create_custom_header(self) -> None:
        """
        Creates the clean Octumo month navigation.
        """

        self.header = QFrame(
            self
        )

        self.header.setObjectName(
            "octumo_calendar_header"
        )

        self.header_layout = QHBoxLayout(
            self.header
        )

        self.header_layout.setContentsMargins(
            10,
            10,
            10,
            8,
        )

        self.header_layout.setSpacing(
            6
        )

        # -------------------------------------------------
        # Previous month
        # -------------------------------------------------

        self.previous_button = QToolButton(
            self.header
        )

        self.previous_button.setObjectName(
            "calendar_previous_button"
        )

        self.previous_button.setText(
            "‹"
        )

        self.previous_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.previous_button.setFixedSize(
            36,
            36,
        )

        self.previous_button.clicked.connect(
            self._go_to_previous_month
        )

        # -------------------------------------------------
        # Month label
        # -------------------------------------------------

        self.month_label = QLabel(
            self.header
        )

        self.month_label.setObjectName(
            "calendar_month_label"
        )

        self.month_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        # -------------------------------------------------
        # Next month
        # -------------------------------------------------

        self.next_button = QToolButton(
            self.header
        )

        self.next_button.setObjectName(
            "calendar_next_button"
        )

        self.next_button.setText(
            "›"
        )

        self.next_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.next_button.setFixedSize(
            36,
            36,
        )

        self.next_button.clicked.connect(
            self._go_to_next_month
        )

        # -------------------------------------------------
        # Header layout
        # -------------------------------------------------

        self.header_layout.addWidget(
            self.previous_button
        )

        self.header_layout.addWidget(
            self.month_label,
            1,
        )

        self.header_layout.addWidget(
            self.next_button
        )

        calendar_layout = self.layout()

        if calendar_layout is not None:
            calendar_layout.insertWidget(
                0,
                self.header,
            )

    def _go_to_previous_month(self) -> None:
        year = self.yearShown()
        month = self.monthShown()

        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1

        self.setCurrentPage(
            year,
            month,
        )

    def _go_to_next_month(self) -> None:
        year = self.yearShown()
        month = self.monthShown()

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

        self.setCurrentPage(
            year,
            month,
        )

    def _update_month_label(
        self,
        year: int,
        month: int,
    ) -> None:
        date = QDate(
            year,
            month,
            1,
        )

        month_name = date.toString(
            "MMMM"
        )

        self.month_label.setText(
            f"{month_name} {year}"
        )

    def _apply_calendar_style(self) -> None:
        self.setStyleSheet(
            """
            QCalendarWidget#octumo_calendar {
                background-color: transparent;

                color: #0F172A;

                border: none;
            }

            QFrame#octumo_calendar_header {
                background-color: transparent;

                border: none;
            }

            QLabel#calendar_month_label {
                background-color: transparent;

                border: none;

                color: #17243A;

                font-size: 15px;
                font-weight: 700;
            }

            QToolButton#calendar_previous_button,
            QToolButton#calendar_next_button {
                background-color: transparent;

                border: none;
                border-radius: 10px;

                color: #17243A;

                font-size: 27px;
                font-weight: 400;

                padding: 0px;
            }

            QToolButton#calendar_previous_button:hover,
            QToolButton#calendar_next_button:hover {
                background-color: #F1F5F9;
            }

            QToolButton#calendar_previous_button:pressed,
            QToolButton#calendar_next_button:pressed {
                background-color: #E2E8F0;
            }

            /*
             * Weekday header.
             */

            QCalendarWidget QTableView {
                background-color: transparent;

                border: none;
                outline: none;

                color: #64748B;

                font-size: 12px;
                font-weight: 600;
            }

            /*
             * Calendar day area.
             */

            QCalendarWidget QAbstractItemView {
                background-color: transparent;

                border: none;
                outline: none;

                selection-background-color: transparent;
                selection-color: #FFFFFF;

                font-size: 13px;
            }

            QCalendarWidget QTableView::item {
                background-color: transparent;

                border: none;

                padding: 5px;
                margin: 1px;
            }

            QCalendarWidget QTableView::item:selected {
                background-color: transparent;

                border: none;
            }

            QCalendarWidget QTableView::item:selected:hover {
                background-color: transparent;

                border: none;
            }
            """
        )


class OctumoCalendarPopup(QFrame):
    """
    Custom Octumo calendar popup.

    The background and border are painted manually with
    antialiasing. This gives smooth rounded corners on macOS
    without using QRegion masks.
    """

    CORNER_RADIUS = 16

    def __init__(
        self,
        calendar: OctumoCalendar,
        parent=None,
    ) -> None:
        super().__init__(
            parent,
            Qt.WindowType.Popup,
        )

        self.setObjectName(
            "octumo_calendar_popup"
        )

        # Transparent window background.
        #
        # IMPORTANT:
        # We paint the opaque white rounded surface
        # ourselves in paintEvent().
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            True,
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_NoSystemBackground,
            True,
        )

        self._calendar = calendar

        self._layout = QHBoxLayout(
            self
        )

        self._layout.setContentsMargins(
            1,
            1,
            1,
            1,
        )

        self._layout.setSpacing(
            0,
        )

        self._layout.addWidget(
            self._calendar
        )

    def paintEvent(
        self,
        event,
    ) -> None:
        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing,
            True,
        )

        painter.setRenderHint(
            QPainter.RenderHint.TextAntialiasing,
            True,
        )

        rect = self.rect().adjusted(
            0,
            0,
            -1,
            -1,
        )

        path = QPainterPath()

        path.addRoundedRect(
            rect,
            self.CORNER_RADIUS,
            self.CORNER_RADIUS,
        )

        # -------------------------------------------------
        # White background
        # -------------------------------------------------

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QColor("#FFFFFF")
        )

        painter.drawPath(
            path
        )

        # -------------------------------------------------
        # Subtle border
        # -------------------------------------------------

        border_path = QPainterPath()

        border_rect = rect.adjusted(
            0.5,
            0.5,
            -0.5,
            -0.5,
        )

        border_path.addRoundedRect(
            border_rect,
            self.CORNER_RADIUS,
            self.CORNER_RADIUS,
        )

        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.setPen(
            QPen(
                QColor("#CBD5E1"),
                1.0,
            )
        )

        painter.drawPath(
            border_path
        )

        painter.end()


class OctumoDateEdit(QDateEdit):
    """
    Modern Octumo date picker.

    - Visible dark chevron
    - No native spin buttons
    - Clicking the field opens the calendar
    - Clicking the chevron opens the calendar
    - Date can be selected with mouse
    - Date can still be typed with keyboard
    - Smooth rounded calendar popup
    """

    def __init__(
        self,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName(
            "octumo_date_edit"
        )

        self.setFixedHeight(
            42
        )

        # -------------------------------------------------
        # Remove native QDateEdit controls.
        # -------------------------------------------------

        self.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.NoButtons
        )

        self.setCalendarPopup(
            False
        )

        self.setDisplayFormat(
            "dd.MM.yyyy"
        )

        self.setDate(
            QDate.currentDate()
        )

        # -------------------------------------------------
        # Keyboard editing.
        # -------------------------------------------------

        self.setKeyboardTracking(
            False
        )

        self.lineEdit().setReadOnly(
            False
        )

        self.lineEdit().setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        # -------------------------------------------------
        # Custom calendar.
        # -------------------------------------------------

        self._calendar = OctumoCalendar()

        # -------------------------------------------------
        # Custom popup.
        # -------------------------------------------------

        self._popup = OctumoCalendarPopup(
            self._calendar
        )

        self._calendar.clicked.connect(
            self._on_calendar_date_selected
        )

        # -------------------------------------------------
        # Calendar button.
        # -------------------------------------------------

        self._create_calendar_button()

        self._apply_date_edit_style()

        self.lineEdit().installEventFilter(
            self
        )

    def _create_calendar_button(self) -> None:
        """
        Creates the single visible calendar chevron.
        """

        self.calendar_button = QToolButton(
            self
        )

        self.calendar_button.setObjectName(
            "octumo_calendar_button"
        )

        self.calendar_button.setText(
            "▼"
        )

        self.calendar_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.calendar_button.setFixedSize(
            34,
            34,
        )

        self.calendar_button.clicked.connect(
            self._toggle_calendar
        )

        self.calendar_button.setStyleSheet(
            """
            QToolButton#octumo_calendar_button {
                background-color: transparent;

                border: none;

                color: #17243A;

                font-size: 13px;
                font-weight: 700;

                padding: 0px;
            }

            QToolButton#octumo_calendar_button:hover {
                background-color: #F1F5F9;

                border-radius: 9px;

                color: #0F172A;
            }

            QToolButton#octumo_calendar_button:pressed {
                background-color: #E2E8F0;

                border-radius: 9px;
            }
            """
        )

        self._position_calendar_button()

    def _position_calendar_button(self) -> None:
        if not hasattr(
            self,
            "calendar_button",
        ):
            return

        button_width = 34
        button_height = 34

        x = (
            self.width()
            - button_width
            - 6
        )

        y = (
            self.height()
            - button_height
        ) // 2

        self.calendar_button.setGeometry(
            x,
            y,
            button_width,
            button_height,
        )

    def resizeEvent(
        self,
        event,
    ) -> None:
        super().resizeEvent(
            event
        )

        self._position_calendar_button()

    def eventFilter(
        self,
        watched,
        event,
    ):
        if (
            watched is self.lineEdit()
            and event.type()
            == QEvent.Type.MouseButtonRelease
            and event.button()
            == Qt.MouseButton.LeftButton
        ):
            self._toggle_calendar()

        return super().eventFilter(
            watched,
            event,
        )

    def _toggle_calendar(self) -> None:
        if self._popup.isVisible():
            self._popup.hide()
        else:
            self._show_calendar()

    def _show_calendar(self) -> None:
        current_date = self.date()

        # Select current date.
        self._calendar.setSelectedDate(
            current_date
        )

        # Open on current month.
        self._calendar.setCurrentPage(
            current_date.year(),
            current_date.month(),
        )

        # Calculate popup size.
        self._popup.adjustSize()

        # Position below the date field.
        global_position = self.mapToGlobal(
            QPoint(
                0,
                self.height() + 6,
            )
        )

        self._popup.move(
            global_position
        )

        self._popup.show()

        self._calendar.setFocus()

    def _on_calendar_date_selected(
        self,
        date: QDate,
    ) -> None:
        self.setDate(
            date
        )

        self._popup.hide()

        self.setFocus()

    def _apply_date_edit_style(self) -> None:
        self.setStyleSheet(
            """
            QDateEdit#octumo_date_edit {
                background-color: #FFFFFF;

                color: #0F172A;

                border: 1px solid #CBD5E1;
                border-radius: 9px;

                padding-left: 12px;
                padding-right: 42px;

                font-size: 14px;
            }

            QDateEdit#octumo_date_edit:hover {
                border-color: #94A3B8;
            }

            QDateEdit#octumo_date_edit:focus {
                border-color: #64748B;

                background-color: #FFFFFF;
            }

            /*
             * Completely remove native Qt controls.
             */

            QDateEdit#octumo_date_edit::drop-down {
                width: 0px;

                border: none;

                background: transparent;
            }

            QDateEdit#octumo_date_edit::down-arrow {
                image: none;

                width: 0px;
                height: 0px;
            }

            QLineEdit {
                background-color: transparent;

                border: none;

                color: #0F172A;

                selection-background-color: #DCE5F0;
                selection-color: #0F172A;
            }
            """
        )