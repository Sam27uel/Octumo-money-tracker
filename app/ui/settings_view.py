from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.ui.edit_profile_modal import EditProfileModal


class SettingsView(QWidget):

    def __init__(
        self,
        parent=None,
    ) -> None:

        super().__init__(
            parent
        )

        self.user_name = "Samuel"

        self.build_ui()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self) -> None:

        layout = QVBoxLayout(
            self
        )

        # EXACTLY LIKE CATEGORIES VIEW
        layout.setContentsMargins(
            44,
            36,
            44,
            44,
        )

        layout.setSpacing(
            0
        )

        # =================================================
        # Header
        # =================================================

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
            "Settings"
        )

        title.setObjectName(
            "page_title"
        )

        subtitle = QLabel(
            "Manage your profile and application preferences."
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

        layout.addLayout(
            header_layout
        )

        # EXACTLY LIKE CATEGORIES VIEW
        layout.addSpacing(
            34
        )

        # =================================================
        # Scroll area
        # =================================================

        self.settings_scroll = QScrollArea()

        self.settings_scroll.setObjectName(
            "settings_scroll"
        )

        self.settings_scroll.setWidgetResizable(
            True
        )

        self.settings_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.settings_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.settings_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.settings_scroll.setWidget(
            self.create_settings_container()
        )

        layout.addWidget(
            self.settings_scroll,
            1,
        )

        # =================================================
        # Styling
        # =================================================

        self.setStyleSheet(
            """
            /* =================================================
               Page
               ================================================= */


            QLabel#page_title {
                color: #0F172A;
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#page_subtitle {
                color: #64748B;
                font-size: 15px;
            }

            /* =================================================
               Scroll area
               ================================================= */

            QScrollArea#settings_scroll {
                background-color: transparent;
                border: none;
            }

            QWidget#settings_scroll_content {
                background-color: transparent;
            }

            /* =================================================
               Section title
               ================================================= */

            QLabel#section_title {
                color: #64748B;
                font-size: 13px;
                font-weight: 700;
            }

            /* =================================================
               Cards
               ================================================= */

            QFrame#settings_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }

            /* =================================================
               Profile
               ================================================= */

            QLabel#profile_avatar {
                background-color: #0F172A;
                color: #FFFFFF;
                border-radius: 24px;
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#profile_name {
                color: #0F172A;
                font-size: 16px;
                font-weight: 600;
            }

            QLabel#profile_type {
                color: #64748B;
                font-size: 13px;
            }

            QPushButton#edit_profile_button {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                padding: 0 14px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton#edit_profile_button:hover {
                background-color: #F8FAFC;
                color: #0F172A;
                border-color: #94A3B8;
            }

            QPushButton#edit_profile_button:pressed {
                background-color: #F1F5F9;
            }

            /* =================================================
               Settings rows
               ================================================= */

            QLabel#setting_name {
                color: #0F172A;
                font-size: 14px;
                font-weight: 600;
            }

            QLabel#setting_value {
                color: #64748B;
                font-size: 13px;
            }

            QLabel#setting_arrow {
                color: #94A3B8;
                font-size: 24px;
                font-weight: 400;
            }

            /* =================================================
               Divider
               ================================================= */

            QFrame#settings_divider {
                background-color: #E2E8F0;
                border: none;
                min-height: 1px;
                max-height: 1px;
            }

            /* =================================================
               About
               ================================================= */

            QLabel#about_name {
                color: #0F172A;
                font-size: 15px;
                font-weight: 600;
            }

            QLabel#about_description {
                color: #64748B;
                font-size: 13px;
            }

            QLabel#about_version {
                color: #94A3B8;
                font-size: 13px;
                font-weight: 500;
            }

            /* =================================================
               Scrollbar
               ================================================= */

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

    # =====================================================
    # Settings container
    # =====================================================

    def create_settings_container(self) -> QWidget:

        container = QWidget()

        container.setObjectName(
            "settings_scroll_content"
        )

        self.settings_layout = QVBoxLayout(
            container
        )

        self.settings_layout.setContentsMargins(
            0,
            0,
            8,
            0,
        )

        self.settings_layout.setSpacing(
            0
        )

        self.settings_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        # =================================================
        # My Profile
        # =================================================

        profile_section = QLabel(
            "My Profile"
        )

        profile_section.setObjectName(
            "section_title"
        )

        self.settings_layout.addWidget(
            profile_section
        )

        self.settings_layout.addSpacing(
            10
        )

        self.settings_layout.addWidget(
            self.create_profile_card()
        )

        self.settings_layout.addSpacing(
            28
        )

        # =================================================
        # Preferences
        # =================================================

        preferences_section = QLabel(
            "Preferences"
        )

        preferences_section.setObjectName(
            "section_title"
        )

        self.settings_layout.addWidget(
            preferences_section
        )

        self.settings_layout.addSpacing(
            10
        )

        self.settings_layout.addWidget(
            self.create_preferences_card()
        )

        self.settings_layout.addSpacing(
            28
        )

        # =================================================
        # About
        # =================================================

        about_section = QLabel(
            "About"
        )

        about_section.setObjectName(
            "section_title"
        )

        self.settings_layout.addWidget(
            about_section
        )

        self.settings_layout.addSpacing(
            10
        )

        self.settings_layout.addWidget(
            self.create_about_card()
        )

        self.settings_layout.addStretch()

        return container

    # =====================================================
    # Profile card
    # =====================================================

    def create_profile_card(self) -> QFrame:

        card = QFrame()

        card.setObjectName(
            "settings_card"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            24,
            20,
            24,
            20,
        )

        layout.setSpacing(
            0
        )

        # -------------------------------------------------
        # Main profile row
        # -------------------------------------------------

        row = QHBoxLayout()

        row.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        row.setSpacing(
            14
        )

        # Avatar

        self.avatar = QLabel(
            self.get_initial()
        )

        self.avatar.setObjectName(
            "profile_avatar"
        )

        self.avatar.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.avatar.setFixedSize(
            48,
            48,
        )

        row.addWidget(
            self.avatar
        )

        # Name

        info_layout = QVBoxLayout()

        info_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        info_layout.setSpacing(
            3
        )

        self.profile_name = QLabel(
            self.user_name
        )

        self.profile_name.setObjectName(
            "profile_name"
        )

        profile_type = QLabel(
            "Personal account"
        )

        profile_type.setObjectName(
            "profile_type"
        )

        info_layout.addWidget(
            self.profile_name
        )

        info_layout.addWidget(
            profile_type
        )

        row.addLayout(
            info_layout
        )

        row.addStretch()

        # Edit button

        edit_button = QPushButton(
            "Edit profile"
        )

        edit_button.setObjectName(
            "edit_profile_button"
        )

        edit_button.setFixedHeight(
            38
        )

        edit_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        edit_button.clicked.connect(
            self.open_edit_profile
        )

        row.addWidget(
            edit_button
        )

        layout.addLayout(
            row
        )

        return card

    # =====================================================
    # Preferences card
    # =====================================================

    def create_preferences_card(self) -> QFrame:

        card = QFrame()

        card.setObjectName(
            "settings_card"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            24,
            4,
            24,
            4,
        )

        layout.setSpacing(
            0
        )

        layout.addLayout(
            self.create_setting_row(
                "Currency",
                "EUR (€)",
            )
        )

        layout.addWidget(
            self.create_divider()
        )

        layout.addLayout(
            self.create_setting_row(
                "Date format",
                "DD.MM.YYYY",
            )
        )

        layout.addWidget(
            self.create_divider()
        )

        layout.addLayout(
            self.create_setting_row(
                "First day of week",
                "Monday",
            )
        )

        return card

    # =====================================================
    # About card
    # =====================================================

    def create_about_card(self) -> QFrame:

        card = QFrame()

        card.setObjectName(
            "settings_card"
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            24,
            20,
            24,
            20,
        )

        layout.setSpacing(
            0
        )

        row = QHBoxLayout()

        row.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        info_layout = QVBoxLayout()

        info_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        info_layout.setSpacing(
            4
        )

        app_name = QLabel(
            "Octumo Money Tracker"
        )

        app_name.setObjectName(
            "about_name"
        )

        description = QLabel(
            "Personal finance management made simple."
        )

        description.setObjectName(
            "about_description"
        )

        info_layout.addWidget(
            app_name
        )

        info_layout.addWidget(
            description
        )

        row.addLayout(
            info_layout
        )

        row.addStretch()

        version = QLabel(
            "v1.0.0"
        )

        version.setObjectName(
            "about_version"
        )

        row.addWidget(
            version
        )

        layout.addLayout(
            row
        )

        return card

    # =====================================================
    # Setting row
    # =====================================================

    def create_setting_row(
        self,
        title: str,
        value: str,
    ) -> QHBoxLayout:

        row = QHBoxLayout()

        row.setContentsMargins(
            0,
            14,
            0,
            14,
        )

        row.setSpacing(
            0
        )

        info_layout = QVBoxLayout()

        info_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        info_layout.setSpacing(
            2
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "setting_name"
        )

        value_label = QLabel(
            value
        )

        value_label.setObjectName(
            "setting_value"
        )

        info_layout.addWidget(
            title_label
        )

        info_layout.addWidget(
            value_label
        )

        row.addLayout(
            info_layout
        )

        row.addStretch()

        arrow = QLabel(
            "›"
        )

        arrow.setObjectName(
            "setting_arrow"
        )

        row.addWidget(
            arrow
        )

        return row

    # =====================================================
    # Divider
    # =====================================================

    def create_divider(self) -> QFrame:

        divider = QFrame()

        divider.setFrameShape(
            QFrame.Shape.HLine
        )

        divider.setObjectName(
            "settings_divider"
        )

        return divider

    # =====================================================
    # Edit profile
    # =====================================================

    def open_edit_profile(self) -> None:

        from PySide6.QtWidgets import QApplication

        main_window = QApplication.activeWindow()

        modal = EditProfileModal(
            current_name=self.user_name,
            parent=main_window,
        )

        modal.cancelled.connect(
            lambda: self.close_profile_modal(
                modal
            )
        )

        main_window.show_modal(
            modal
        )

        # Store reference so we can access it
        self._edit_profile_modal = modal

    # =====================================================
    # Close profile modal
    # =====================================================

    def close_profile_modal(
        self,
        modal,
    ) -> None:

        from PySide6.QtWidgets import QApplication

        # If a valid name was entered,
        # update the Settings profile.

        if hasattr(
            modal,
            "current_name",
        ):

            if modal.current_name:

                self.user_name = (
                    modal.current_name
                )

                self.update_profile()

        main_window = QApplication.activeWindow()

        if (
            main_window is not None
            and main_window.modal_overlay is not None
        ):

            main_window.close_modal()

    # =====================================================
    # Update profile
    # =====================================================

    def update_profile(self) -> None:

        self.profile_name.setText(
            self.user_name
        )

        self.avatar.setText(
            self.get_initial()
        )

    # =====================================================
    # Initial
    # =====================================================

    def get_initial(self) -> str:

        if not self.user_name:
            return "S"

        return self.user_name[
            0
        ].upper()