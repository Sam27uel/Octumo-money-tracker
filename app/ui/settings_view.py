from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QWidget,
)

from app.services.backup_service import (
    export_database,
    restore_database,
)

from app.services.user_settings_service import (
    get_date_format,
    get_first_day_of_week,
    get_user_name,
    update_date_format,
    update_first_day_of_week,
    update_user_name,
)

from app.ui.edit_profile_modal import EditProfileModal
from app.ui.modal import Modal
from app.ui.setting_row import SettingRow
from app.ui.settings_option_modal import SettingsOptionModal


# =========================================================
# Settings Action Row
# =========================================================


class SettingsActionRow(QWidget):

    clicked = Signal()

    def __init__(
        self,
        title: str,
        description: str,
        parent=None,
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            "settings_action_row"
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            14,
            11,
            14,
            11,
        )

        layout.setSpacing(
            0
        )

        text_layout = QVBoxLayout()

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text_layout.setSpacing(
            3
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "data_row_title"
        )

        description_label = QLabel(
            description
        )

        description_label.setObjectName(
            "data_row_description"
        )

        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            description_label
        )

        layout.addLayout(
            text_layout
        )

        layout.addStretch()

        arrow = QLabel(
            "›"
        )

        arrow.setObjectName(
            "setting_arrow"
        )

        arrow.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        arrow.setFixedWidth(
            28
        )

        layout.addWidget(
            arrow
        )

    def mousePressEvent(
        self,
        event,
    ) -> None:

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self.clicked.emit()

        super().mousePressEvent(
            event
        )


# =========================================================
# Backup Action Card
# =========================================================


class BackupActionCard(QFrame):

    clicked = Signal()

    def __init__(
        self,
        title: str,
        description: str,
        primary: bool = False,
        parent=None,
    ) -> None:

        super().__init__(parent)

        self.setObjectName(
            "backup_action_card"
        )

        self.primary = primary

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        self.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.setFixedHeight(
            62
        )

        layout = QHBoxLayout(
            self
        )

        layout.setContentsMargins(
            16,
            0,
            16,
            0,
        )

        layout.setSpacing(
            12
        )

        text_layout = QVBoxLayout()

        text_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        text_layout.setSpacing(
            2
        )

        title_label = QLabel(
            title
        )

        title_label.setObjectName(
            "backup_action_title"
        )

        description_label = QLabel(
            description
        )

        description_label.setObjectName(
            "backup_action_description"
        )

        text_layout.addWidget(
            title_label
        )

        text_layout.addWidget(
            description_label
        )

        layout.addLayout(
            text_layout
        )

        layout.addStretch()

        arrow = QLabel(
            "›"
        )

        arrow.setObjectName(
            "backup_action_arrow"
        )

        arrow.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        arrow.setFixedWidth(
            24
        )

        layout.addWidget(
            arrow
        )

        self.update_style()

    def update_style(
        self,
    ) -> None:

        if self.primary:

            self.setStyleSheet(
                """
                QFrame#backup_action_card {
                    background-color: #F8FAFC;
                    border: 1px solid #CBD5E1;
                    border-radius: 10px;
                }

                QFrame#backup_action_card:hover {
                    background-color: #F1F5F9;
                    border-color: #94A3B8;
                }

                QLabel#backup_action_title {
                    background-color: transparent;
                    color: #0F172A;
                    font-size: 14px;
                    font-weight: 700;
                }

                QLabel#backup_action_description {
                    background-color: transparent;
                    color: #64748B;
                    font-size: 12px;
                }

                QLabel#backup_action_arrow {
                    background-color: transparent;
                    color: #64748B;
                    font-size: 24px;
                }
                """
            )

        else:

            self.setStyleSheet(
                """
                QFrame#backup_action_card {
                    background-color: #FFFFFF;
                    border: 1px solid #E2E8F0;
                    border-radius: 10px;
                }

                QFrame#backup_action_card:hover {
                    background-color: #F8FAFC;
                    border-color: #CBD5E1;
                }

                QLabel#backup_action_title {
                    background-color: transparent;
                    color: #0F172A;
                    font-size: 14px;
                    font-weight: 600;
                }

                QLabel#backup_action_description {
                    background-color: transparent;
                    color: #64748B;
                    font-size: 12px;
                }

                QLabel#backup_action_arrow {
                    background-color: transparent;
                    color: #94A3B8;
                    font-size: 24px;
                }
                """
            )

    def mousePressEvent(
        self,
        event,
    ) -> None:

        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self.clicked.emit()

        super().mousePressEvent(
            event
        )


# =========================================================
# Backup & Restore Modal
# =========================================================


class BackupRestoreModal(Modal):

    create_backup_requested = Signal()
    restore_requested = Signal()

    def __init__(
        self,
        parent=None,
    ) -> None:

        super().__init__(
            title="Backup & restore",
            subtitle=(
                "Protect your Octumo data or restore "
                "an existing backup."
            ),
            primary_text="Close",
            cancel_text="Cancel",
            parent=parent,
        )

        self.primary_button.hide()

        actions_container = QWidget()

        actions_layout = QVBoxLayout(
            actions_container
        )

        actions_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        actions_layout.setSpacing(
            10
        )

        create_card = BackupActionCard(
            title="Create backup",
            description=(
                "Save a complete copy of your Octumo data."
            ),
            primary=True,
        )

        create_card.clicked.connect(
            self.request_create_backup
        )

        actions_layout.addWidget(
            create_card
        )

        restore_card = BackupActionCard(
            title="Restore backup",
            description=(
                "Replace your current data with a backup."
            ),
            primary=False,
        )

        restore_card.clicked.connect(
            self.request_restore
        )

        actions_layout.addWidget(
            restore_card
        )

        self.add_content(
            actions_container
        )

    def request_create_backup(
        self,
    ) -> None:

        self.create_backup_requested.emit()

    def request_restore(
        self,
    ) -> None:

        self.restore_requested.emit()


# =========================================================
# Settings View
# =========================================================


class SettingsView(QWidget):

    def __init__(
        self,
        parent=None,
    ) -> None:

        super().__init__(
            parent
        )

        self.setObjectName(
            "settings_view"
        )

        self.user_name = get_user_name()

        self.date_format = get_date_format()

        self.first_day_of_week = (
            get_first_day_of_week()
        )

        self.build_ui()

        self.setStyleSheet(
            """
            /* =================================================
               MAIN
               ================================================= */

            QWidget#settings_view {
                background-color: #F8FAFC;
            }

            QWidget#settings_scroll_content {
                background-color: #F8FAFC;
            }


            /* =================================================
               HEADER
               ================================================= */

            QLabel#page_title {
                background-color: transparent;
                color: #0F172A;
                font-size: 28px;
                font-weight: 700;
            }

            QLabel#page_subtitle {
                background-color: transparent;
                color: #64748B;
                font-size: 15px;
            }


            /* =================================================
               SECTION TITLES
               ================================================= */

            QLabel#settings_section_title {
                background-color: transparent;
                color: #64748B;
                font-size: 13px;
                font-weight: 700;
            }


            /* =================================================
               OUTER SETTINGS BUBBLES
               ================================================= */

            QFrame#settings_card {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 12px;
            }


            /* =================================================
               PROFILE
               ================================================= */

            QLabel#profile_avatar {
                background-color: #EFF6FF;
                color: #17243A;
                border: none;
                border-radius: 28px;
                font-size: 22px;
                font-weight: 700;
            }

            QLabel#profile_name {
                background-color: transparent;
                color: #0F172A;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#profile_type {
                background-color: transparent;
                color: #64748B;
                font-size: 14px;
            }


            /* =================================================
               EDIT PROFILE BUTTON
               ================================================= */

            QPushButton#edit_profile_button {
                background-color: #FFFFFF;
                color: #334155;
                border: 1px solid #CBD5E1;
                border-radius: 9px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 16px;
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
               NESTED SETTING BUBBLES
               ================================================= */

            QWidget#setting_row {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }

            QWidget#setting_row:hover {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
            }

            /* Currency - no hover effect */

            QWidget#currency_setting_row {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }

            QWidget#currency_setting_row:hover {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }

            QLabel#setting_name {
                background-color: transparent;
                color: #0F172A;
                font-size: 15px;
                font-weight: 600;
            }

            QLabel#setting_value {
                background-color: transparent;
                color: #64748B;
                font-size: 14px;
            }

            QLabel#setting_arrow {
                background-color: transparent;
                color: #94A3B8;
                font-size: 27px;
                font-weight: 400;
            }


            /* =================================================
               DATA ACTION BUBBLES
               ================================================= */

            QWidget#settings_action_row {
                background-color: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 10px;
            }

            QWidget#settings_action_row:hover {
                background-color: #F1F5F9;
                border: 1px solid #CBD5E1;
                border-radius: 10px;
            }

            QLabel#data_row_title {
                background-color: transparent;
                color: #0F172A;
                font-size: 15px;
                font-weight: 600;
            }

            QLabel#data_row_description {
                background-color: transparent;
                color: #64748B;
                font-size: 14px;
            }


            /* =================================================
               ABOUT
               ================================================= */

            QLabel#about_title {
                background-color: transparent;
                color: #0F172A;
                font-size: 16px;
                font-weight: 700;
            }

            QLabel#about_version {
                background-color: transparent;
                color: #64748B;
                font-size: 14px;
            }

            QLabel#about_description {
                background-color: transparent;
                color: #64748B;
                font-size: 14px;
            }


            /* =================================================
               SCROLLBAR
               ================================================= */

            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0;
                border: none;
            }

            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 4px;
                min-height: 40px;
            }

            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
                border: none;
                background: transparent;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        )

    # =====================================================
    # Build UI
    # =====================================================

    def build_ui(
        self,
    ) -> None:

        layout = QVBoxLayout(
            self
        )

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
            "Manage your profile, preferences and data."
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

        layout.addSpacing(
            28
        )

        # =================================================
        # Scroll
        # =================================================

        scroll = QScrollArea()

        scroll.setObjectName(
            "settings_scroll"
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

        scroll.viewport().setObjectName(
            "settings_scroll_viewport"
        )

        scroll.viewport().setStyleSheet(
            """
            QWidget#settings_scroll_viewport {
                background-color: #F8FAFC;
                border: none;
            }
            """
        )

        # =================================================
        # Content
        # =================================================

        content = QWidget()

        content.setObjectName(
            "settings_scroll_content"
        )

        content_layout = QVBoxLayout(
            content
        )

        content_layout.setContentsMargins(
            0,
            0,
            8,
            0,
        )

        content_layout.setSpacing(
            0
        )

        # =================================================
        # MY PROFILE
        # =================================================

        content_layout.addWidget(
            self.section_title(
                "MY PROFILE"
            )
        )

        content_layout.addSpacing(
            8
        )

        profile_card = QFrame()

        profile_card.setObjectName(
            "settings_card"
        )

        profile_card.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        profile_layout = QHBoxLayout(
            profile_card
        )

        profile_layout.setContentsMargins(
            28,
            18,
            28,
            18,
        )

        profile_layout.setSpacing(
            18
        )

        self.profile_avatar = QLabel(
            self.get_avatar_letter()
        )

        self.profile_avatar.setObjectName(
            "profile_avatar"
        )

        self.profile_avatar.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.profile_avatar.setFixedSize(
            56,
            56,
        )

        profile_layout.addWidget(
            self.profile_avatar
        )

        profile_info = QVBoxLayout()

        profile_info.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        profile_info.setSpacing(
            3
        )

        self.profile_name_label = QLabel(
            self.user_name
        )

        self.profile_name_label.setObjectName(
            "profile_name"
        )

        profile_type = QLabel(
            "Personal account"
        )

        profile_type.setObjectName(
            "profile_type"
        )

        profile_info.addStretch()

        profile_info.addWidget(
            self.profile_name_label
        )

        profile_info.addWidget(
            profile_type
        )

        profile_info.addStretch()

        profile_layout.addLayout(
            profile_info
        )

        profile_layout.addStretch()

        edit_button = QPushButton(
            "Edit profile"
        )

        edit_button.setObjectName(
            "edit_profile_button"
        )

        edit_button.setFixedHeight(
            42
        )

        edit_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        edit_button.clicked.connect(
            self.open_edit_profile
        )

        profile_layout.addWidget(
            edit_button
        )

        content_layout.addWidget(
            profile_card
        )

        content_layout.addSpacing(
            22
        )

        # =================================================
        # PREFERENCES
        # =================================================

        content_layout.addWidget(
            self.section_title(
                "PREFERENCES"
            )
        )

        content_layout.addSpacing(
            8
        )

        preferences_card = QFrame()

        preferences_card.setObjectName(
            "settings_card"
        )

        preferences_card.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        preferences_layout = QVBoxLayout(
            preferences_card
        )

        preferences_layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        preferences_layout.setSpacing(
            8
        )

        # Currency

        currency_row = SettingRow(
            title="Currency",
            value="EUR (€)",
            clickable=False,
        )

        currency_row.setObjectName(
            "currency_setting_row"
        )

        currency_row.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        preferences_layout.addWidget(
            currency_row
        )

        # Date format

        self.date_format_row = SettingRow(
            title="Date format",
            value=self.date_format,
            clickable=True,
        )

        self.date_format_row.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        self.date_format_row.clicked.connect(
            self.open_date_format
        )

        preferences_layout.addWidget(
            self.date_format_row
        )

        # First day

        self.first_day_row = SettingRow(
            title="First day of week",
            value=self.first_day_of_week,
            clickable=True,
        )

        self.first_day_row.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        self.first_day_row.clicked.connect(
            self.open_first_day_of_week
        )

        preferences_layout.addWidget(
            self.first_day_row
        )

        content_layout.addWidget(
            preferences_card
        )

        content_layout.addSpacing(
            22
        )

        # =================================================
        # DATA & PRIVACY
        # =================================================

        content_layout.addWidget(
            self.section_title(
                "DATA & PRIVACY"
            )
        )

        content_layout.addSpacing(
            8
        )

        data_card = QFrame()

        data_card.setObjectName(
            "settings_card"
        )

        data_card.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        data_layout = QVBoxLayout(
            data_card
        )

        data_layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        data_layout.setSpacing(
            8
        )

        export_row = SettingsActionRow(
            title="Export data",
            description="Export your financial data",
        )

        export_row.clicked.connect(
            self.export_data
        )

        data_layout.addWidget(
            export_row
        )

        backup_row = SettingsActionRow(
            title="Backup & restore",
            description="Create a backup or restore your data",
        )

        backup_row.clicked.connect(
            self.backup_and_restore
        )

        data_layout.addWidget(
            backup_row
        )

        content_layout.addWidget(
            data_card
        )

        content_layout.addSpacing(
            22
        )

        # =================================================
        # ABOUT
        # =================================================

        content_layout.addWidget(
            self.section_title(
                "ABOUT"
            )
        )

        content_layout.addSpacing(
            8
        )

        about_card = QFrame()

        about_card.setObjectName(
            "settings_card"
        )

        about_card.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True,
        )

        about_layout = QVBoxLayout(
            about_card
        )

        about_layout.setContentsMargins(
            28,
            20,
            28,
            20,
        )

        about_layout.setSpacing(
            4
        )

        about_title = QLabel(
            "Octumo Money Tracker"
        )

        about_title.setObjectName(
            "about_title"
        )

        about_version = QLabel(
            "Version 1.0.0"
        )

        about_version.setObjectName(
            "about_version"
        )

        about_description = QLabel(
            "Personal finance management made simple."
        )

        about_description.setObjectName(
            "about_description"
        )

        about_layout.addWidget(
            about_title
        )

        about_layout.addWidget(
            about_version
        )

        about_layout.addSpacing(
            6
        )

        about_layout.addWidget(
            about_description
        )

        content_layout.addWidget(
            about_card
        )

        content_layout.addSpacing(
            26
        )

        content_layout.addStretch()

        scroll.setWidget(
            content
        )

        layout.addWidget(
            scroll
        )

    # =====================================================
    # Section title
    # =====================================================

    def section_title(
        self,
        text: str,
    ) -> QLabel:

        label = QLabel(
            text
        )

        label.setObjectName(
            "settings_section_title"
        )

        return label

    # =====================================================
    # Avatar
    # =====================================================

    def get_avatar_letter(
        self,
    ) -> str:

        name = self.user_name.strip()

        if not name:
            return "U"

        return name[0].upper()

    # =====================================================
    # Edit profile
    # =====================================================

    def open_edit_profile(
        self,
    ) -> None:

        modal = EditProfileModal(
            current_name=self.user_name,
            parent=self,
        )

        modal.submitted.connect(
            lambda:
            self.save_profile(modal)
        )

        modal.cancelled.connect(
            self.close_current_modal
        )

        self.window().show_modal(
            modal
        )

    def save_profile(
        self,
        modal: EditProfileModal,
    ) -> None:

        name = (
            modal.name_input
            .text()
            .strip()
        )

        if not name:

            modal.name_input.setFocus()

            return

        try:

            update_user_name(
                name
            )

            self.user_name = name

            self.profile_name_label.setText(
                name
            )

            self.profile_avatar.setText(
                self.get_avatar_letter()
            )

            self.window().close_modal()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "Could not update profile:\n\n"
                    f"{error}"
                ),
            )

    # =====================================================
    # Date format
    # =====================================================

    def open_date_format(
        self,
    ) -> None:

        modal = SettingsOptionModal(
            title="Date format",
            subtitle=(
                "Choose how dates are displayed "
                "throughout Octumo."
            ),
            options=[
                "DD.MM.YYYY",
                "DD/MM/YYYY",
                "YYYY-MM-DD",
            ],
            current_value=self.date_format,
            parent=self,
        )

        modal.submitted.connect(
            lambda:
            self.save_date_format(modal)
        )

        modal.cancelled.connect(
            self.close_current_modal
        )

        self.window().show_modal(
            modal
        )

    def save_date_format(
        self,
        modal: SettingsOptionModal,
    ) -> None:

        selected = modal.selected_value

        if not selected:
            return

        try:

            update_date_format(
                selected
            )

            self.date_format = selected

            self.date_format_row.set_value(
                selected
            )

            self.window().close_modal()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "Could not update date format:\n\n"
                    f"{error}"
                ),
            )

    # =====================================================
    # First day of week
    # =====================================================

    def open_first_day_of_week(
        self,
    ) -> None:

        modal = SettingsOptionModal(
            title="First day of week",
            subtitle=(
                "Choose which day starts the week "
                "throughout Octumo."
            ),
            options=[
                "Monday",
                "Sunday",
            ],
            current_value=self.first_day_of_week,
            parent=self,
        )

        modal.submitted.connect(
            lambda:
            self.save_first_day_of_week(modal)
        )

        modal.cancelled.connect(
            self.close_current_modal
        )

        self.window().show_modal(
            modal
        )

    def save_first_day_of_week(
        self,
        modal: SettingsOptionModal,
    ) -> None:

        selected = modal.selected_value

        if not selected:
            return

        try:

            update_first_day_of_week(
                selected
            )

            self.first_day_of_week = selected

            self.first_day_row.set_value(
                selected
            )

            self.window().close_modal()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error",
                (
                    "Could not update first day "
                    "of week:\n\n"
                    f"{error}"
                ),
            )

    # =====================================================
    # Close modal
    # =====================================================

    def close_current_modal(
        self,
    ) -> None:

        self.window().close_modal()

    # =====================================================
    # Backup & restore
    # =====================================================

    def backup_and_restore(
        self,
    ) -> None:

        modal = BackupRestoreModal(
            parent=self
        )

        modal.create_backup_requested.connect(
            lambda:
            self.start_create_backup(modal)
        )

        modal.restore_requested.connect(
            lambda:
            self.start_restore_backup(modal)
        )

        modal.cancelled.connect(
            self.close_current_modal
        )

        self.window().show_modal(
            modal
        )

    # =====================================================
    # Start create backup
    # =====================================================

    def start_create_backup(
        self,
        modal: BackupRestoreModal,
    ) -> None:

        self.window().close_modal()

        self.create_backup()

    # =====================================================
    # Start restore
    # =====================================================

    def start_restore_backup(
        self,
        modal: BackupRestoreModal,
    ) -> None:

        self.window().close_modal()

        self.restore_backup()

    # =====================================================
    # Create backup
    # =====================================================

    def create_backup(
        self,
    ) -> None:

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Create Octumo backup",
            "octumo-backup.json",
            "Octumo Backup (*.json)",
        )

        if not file_path:
            return

        try:

            export_database(
                file_path
            )

            QMessageBox.information(
                self,
                "Backup complete",
                (
                    "Your Octumo backup has been "
                    "created successfully."
                ),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Backup failed",
                (
                    "Could not create backup:\n\n"
                    f"{error}"
                ),
            )

    # =====================================================
    # Restore backup
    # =====================================================

    def restore_backup(
        self,
    ) -> None:

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Restore Octumo backup",
            "",
            "Octumo Backup (*.json)",
        )

        if not file_path:
            return

        answer = QMessageBox.warning(
            self,
            "Restore backup",
            (
                "Restoring this backup will replace "
                "your current Octumo data.\n\n"
                "This action cannot be undone.\n\n"
                "Do you want to continue?"
            ),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
            ),
            QMessageBox.StandardButton.No,
        )

        if (
            answer
            != QMessageBox.StandardButton.Yes
        ):
            return

        try:

            restore_database(
                file_path
            )

            self.user_name = get_user_name()

            self.date_format = (
                get_date_format()
            )

            self.first_day_of_week = (
                get_first_day_of_week()
            )

            self.refresh_settings_ui()

            QMessageBox.information(
                self,
                "Restore complete",
                (
                    "Your Octumo backup has been "
                    "restored successfully."
                ),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Restore failed",
                (
                    "Could not restore the backup:\n\n"
                    f"{error}"
                ),
            )

    # =====================================================
    # Export
    # =====================================================

    def export_data(
        self,
    ) -> None:

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Octumo data",
            "octumo-export.json",
            "Octumo Backup (*.json)",
        )

        if not file_path:
            return

        try:

            export_database(
                file_path
            )

            QMessageBox.information(
                self,
                "Export complete",
                (
                    "Your Octumo data has been "
                    "successfully exported."
                ),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Export failed",
                (
                    "Could not export your data:\n\n"
                    f"{error}"
                ),
            )

    # =====================================================
    # Refresh Settings UI
    # =====================================================

    def refresh_settings_ui(
        self,
    ) -> None:

        self.profile_name_label.setText(
            self.user_name
        )

        self.profile_avatar.setText(
            self.get_avatar_letter()
        )

        self.date_format_row.set_value(
            self.date_format
        )

        self.first_day_row.set_value(
            self.first_day_of_week
        )