import sys, os

# Adds subfolders to Python's search path so cross-folder imports work smoothly
current_dir = os.path.dirname(os.path.abspath(__file__))
client_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(client_dir, 'ui'))
sys.path.append(os.path.join(client_dir, 'widgets'))
sys.path.append(os.path.join(client_dir, 'core'))
sys.path.append(os.path.join(client_dir, 'data'))

import AnimationHandler, SettingsHandler, Menu_ProjectList, Menu_About, Menu_Archive, Menu_Calendar, Menu_Tags, Menu_Settings, Themes, DummyList
from ProjectClasses import Project, Task, Subtask, Tag
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import json, time, datetime, sqlite3, ctypes

class CustomStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.move_anim = QParallelAnimationGroup(self)

class MainController(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Venture")
        self.resize(1200, 800)
        self.screen = QApplication.primaryScreen()
        self.setMinimumWidth(self.screen.size().width() // 2)
        QCoreApplication.setOrganizationName("LunarStudios")
        QCoreApplication.setApplicationName("VentureApp")

        self.is_modal_active = False
        self.current_theme = Themes.THEME_DEFAULT

        self.font_Mag = None
        self.font_JetFam = None
        self.font_FAILSAFE = "Arial"

        folder_fonts = "fonts"
        folder_icons = "icons"
        dir_script = os.path.dirname(os.path.abspath(__file__))
        self.settingsFunctions = SettingsHandler.Settings(self)

        self.animator = AnimationHandler.Animator()

        filename_Mag = "Magnolia Script.otf"
        path_font_Mag = os.path.join(dir_script, folder_fonts, filename_Mag)

        self.icon_app = os.path.join(dir_script, folder_icons, "icon_app.png")
        self.icon_sidebar_main = os.path.join(dir_script, folder_icons, "icon_sidebar_main.png")
        self.icon_sidebar_settings = os.path.join(dir_script, folder_icons, "icon_sidebar_settings.png")
        self.icon_sidebar_calendar = os.path.join(dir_script, folder_icons, "icon_sidebar_calendar.png")
        self.icon_sidebar_tags = os.path.join(dir_script, folder_icons, "icon_sidebar_tags.png")
        self.icon_sidebar_archive = os.path.join(dir_script, folder_icons, "icon_sidebar_archive.png")
        self.icon_sidebar_about = os.path.join(dir_script, folder_icons, "icon_sidebar_about.png")

        self.iconList = [self.icon_sidebar_main, self.icon_sidebar_calendar, self.icon_sidebar_tags, 
                         self.icon_sidebar_archive, self.icon_sidebar_settings, self.icon_sidebar_about]

        if os.path.exists(path_font_Mag):
            fontID = QFontDatabase.addApplicationFont(path_font_Mag)
            if fontID != -1:
                font_families = QFontDatabase.applicationFontFamilies(fontID)
                if font_families: self.font_Mag = font_families[0]
        
        font_Jet_dir = os.path.join(dir_script, folder_fonts)
        if os.path.exists(font_Jet_dir):
            for filename in os.listdir(font_Jet_dir):
                if "JetBrainsMono-Regular" in filename and filename.endswith(".ttf"):
                    path_font_Jet = os.path.join(font_Jet_dir, filename)
                    fontID = QFontDatabase.addApplicationFont(path_font_Jet)
                    if fontID != -1:
                        font_families = QFontDatabase.applicationFontFamilies(fontID)
                        if font_families:
                            self.font_JetFam = font_families[0]
                            break
        
        self.activeMagFont = self.font_Mag if self.font_Mag else self.font_FAILSAFE
        self.activeJetFamFont = self.font_JetFam if self.font_JetFam else self.font_FAILSAFE

        self.masterWidget = QWidget(self)
        self.setCentralWidget(self.masterWidget)
        self.mainMenuLayout = QHBoxLayout(self.masterWidget)
        self.mainMenuLayout.setContentsMargins(0, 0, 0, 0)
        self.mainMenuLayout.setSpacing(0)

        self.stackedWidget = CustomStackedWidget()
        self.stackedWidget.setObjectName("mainContentStack")
        
        self.sidebarWidget = QWidget()
        self.sidebarLayout = QVBoxLayout(self.sidebarWidget)
        self.sidebarLayout.setContentsMargins(0, 30, 0, 50)
        self.sidebarLayout.setSpacing(20)
        self.sidebarWidget.setStyleSheet(
            "background-color: #1e1e1e;"
            "padding: 0px;"
            "border-left: 4px solid black;"
        )
        self.sidebarWidth = 280

        self.sidebarButtonLayout = QVBoxLayout()
        self.sidebarButtonLayout.setSpacing(15)

        self.label_appname = QLabel("Venture", self)
        self.label_appname.setFont(QFont(self.activeMagFont, 42))
        self.label_appname.setStyleSheet("color: white; border: none; background: transparent;")
        self.label_appname.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.sidebar_button_main = QPushButton(" Projects", self)
        self.sidebar_button_calendar = QPushButton(" Calendar", self)
        self.sidebar_button_tags = QPushButton(" Edit Tags", self)
        self.sidebar_button_archive = QPushButton(" Archive", self)
        self.sidebar_button_settings = QPushButton(" Settings", self)
        self.sidebar_button_about = QPushButton(" About", self)

        self.sidebarBtnList = [self.sidebar_button_main, self.sidebar_button_calendar, self.sidebar_button_tags, 
                               self.sidebar_button_archive, self.sidebar_button_settings, self.sidebar_button_about]

        self.mainMenuLayout.addWidget(self.stackedWidget, 1)
        self.mainMenuLayout.addWidget(self.sidebarWidget)

        self.sidebarLayout.addWidget(self.label_appname, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.sidebarLayout.addLayout(self.sidebarButtonLayout)
        self.sidebarWidget.setFixedWidth(self.sidebarWidth)

        self.activeButton = self.sidebar_button_main
        self.activeButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.activeButton.removeEventFilter(self)

        for icon, button in zip(self.iconList, self.sidebarBtnList):
            if os.path.exists(icon):
                try:
                    button.setIcon(QIcon(icon))
                    button.setIconSize(QSize(24, 24))
                    init_color = QColor("#00ffaa") if button == self.activeButton else QColor("#ffffff")
                    self.animator.createAnimation(button, "icon", QColor("#000000"), init_color, duration=1).start()
                except IndexError: pass

        for button in self.sidebarBtnList:
            button.setFont(QFont(self.activeJetFamFont, 14, QFont.Weight.Bold))
            button.setMinimumWidth(230)
            button.setMaximumWidth(260)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            button.setStyleSheet(
                "color: #cccccc;"
                "border: 2px solid #1e1e1e;"
                "outline: none;"
                "text-align: left;"
                "padding: 8px 12px;"
                "background: transparent;"
                "border-radius: 12px;"
            )
            self.sidebarButtonLayout.addWidget(button, alignment=Qt.AlignmentFlag.AlignHCenter)
            if button != self.activeButton:
                button.installEventFilter(self)

        self.sidebar_button_main.clicked.connect(self.goToProjects)
        self.sidebar_button_calendar.clicked.connect(self.goToCalendar)
        self.sidebar_button_tags.clicked.connect(self.goToTags)
        self.sidebar_button_archive.clicked.connect(self.goToArchive)
        self.sidebar_button_settings.clicked.connect(self.goToSettings)
        self.sidebar_button_about.clicked.connect(self.goToAbout)

        self.sidebarButtonLayout.addStretch()

        self.init_Pages()
        self.setBGColour()

        QTimer.singleShot(50, lambda: self.updateActiveBtn(self.activeButton, animate=False))

    def showEvent(self, event):
        super().showEvent(event)
        # Enable native Windows dark mode title bar / handle
        if sys.platform == "win32":
            try:
                hwnd = int(self.winId())
                value = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
            except Exception:
                pass

    def init_Pages(self):
        self.pages = {}
        self.page_project_list = Menu_ProjectList.ProjectListPage(self)
        self.stackedWidget.addWidget(self.page_project_list)
        self.pages["Projects"] = self.page_project_list
        
        self.page_calendar = Menu_Calendar.CalendarPage(self)
        self.stackedWidget.addWidget(self.page_calendar)
        self.pages["Calendar"] = self.page_calendar

        self.page_tags = Menu_Tags.TagsPage(self)
        self.stackedWidget.addWidget(self.page_tags)
        self.pages["Tags"] = self.page_tags

        self.page_archive = Menu_Archive.ArchivePage(self)
        self.stackedWidget.addWidget(self.page_archive)
        self.pages["Archive"] = self.page_archive

        self.page_settings = Menu_Settings.SettingsPage(self)
        self.stackedWidget.addWidget(self.page_settings)
        self.pages["Settings"] = self.page_settings

        self.page_about = Menu_About.AboutPage(self)
        self.stackedWidget.addWidget(self.page_about)
        self.pages["About"] = self.page_about

        self.stackedWidget.setCurrentWidget(self.page_project_list)

    def goToProjects(self):
        self.updateSidebar(self.sender())
        self.stackedWidget.setCurrentWidget(self.page_project_list)

    def goToCalendar(self):
        self.updateSidebar(self.sender())
        self.stackedWidget.setCurrentWidget(self.page_calendar)

    def goToTags(self):
        self.updateSidebar(self.sender())
        self.stackedWidget.setCurrentWidget(self.page_tags)

    def goToArchive(self):
        self.updateSidebar(self.sender())
        self.stackedWidget.setCurrentWidget(self.page_archive)

    def goToSettings(self):
        self.updateSidebar(self.sender())
        self.stackedWidget.setCurrentWidget(self.page_settings)

    def goToAbout(self):
        self.updateSidebar(self.sender())
        self.stackedWidget.setCurrentWidget(self.page_about)

    def openProjectDetail(self, project):
        detail_page = Menu_ProjectList.ProjectDetailPage(self, project)
        self.stackedWidget.addWidget(detail_page)
        self.stackedWidget.setCurrentWidget(detail_page)

    def returnToProjects(self):
        self.stackedWidget.setCurrentWidget(self.page_project_list)

    def updateSidebar(self, new_active_btn):
        if not new_active_btn or self.activeButton == new_active_btn:
            return
        
        old_btn = self.activeButton
        old_btn.clearFocus()
        self.activeButton = new_active_btn
        new_active_btn.clearFocus()
        
        for btn in self.sidebarBtnList:
            if btn != self.activeButton:
                btn.setStyleSheet("color: #cccccc; border: 2px solid #1e1e1e; outline: none; text-align: left; padding: 8px 12px; background: transparent; border-radius: 12px;")
                self.animator.createAnimation(btn, "icon", QColor("#00ffaa"), QColor("#ffffff"), duration=1).start()
                btn.installEventFilter(self)

        self.animator.animateOnHover(
            old_btn,
            ["text", "icon", "background", "border"],
            [QColor("#00ffaa"), QColor("#00ffaa"), QColor(44, 44, 44, 255), QColor("#444444")],
            [QColor("#cccccc"), QColor("#ffffff"), QColor(0, 0, 0, 0), QColor("#1e1e1e")],
            duration=200
        )
        old_btn.setStyleSheet("color: #cccccc; border: 2px solid #1e1e1e; outline: none; text-align: left; padding: 8px 12px; background: transparent; border-radius: 12px;")
        old_btn.installEventFilter(self)

        self.animator.animateOnHover(
            new_active_btn,
            ["text", "icon", "background", "border"],
            [QColor("#cccccc"), QColor("#ffffff"), QColor(0, 0, 0, 0), QColor("#1e1e1e")],
            [QColor("#00ffaa"), QColor("#00ffaa"), QColor(44, 44, 44, 255), QColor("#444444")],
            duration=200
        )
        new_active_btn.removeEventFilter(self)

    def updateActiveBtn(self, button, animate=True):
        button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        button.setStyleSheet("color: #00ffaa; background: #2c2c2c; border: 2px solid #444444; border-radius: 12px; outline: none; text-align: left; padding: 8px 12px;")
        self.animator.createAnimation(button, "icon", QColor("#ffffff"), QColor("#00ffaa"), duration=1).start()

    def eventFilter(self, obj: QObject, event):
        if self.is_modal_active:
            return True

        if isinstance(obj, QPushButton) and obj in self.sidebarBtnList and obj != self.activeButton:
            if event.type() == QEvent.Type.Enter:
                anim = self.animator.animateOnHover(
                    obj,
                    ["text", "icon", "background", "border"],
                    [QColor("#cccccc"), QColor("#ffffff"), QColor(0, 0, 0, 0), QColor("#1e1e1e")],
                    [QColor("#ffffff"), QColor("#ffffff"), QColor(37, 37, 37, 255), QColor("#333333")],
                    duration=200
                )
                anim.finished.connect(lambda: obj.setStyleSheet("color: #ffffff; border: 2px solid #333333; outline: none; text-align: left; padding: 8px 12px; background: rgba(37, 37, 37, 255); border-radius: 12px;"))
                return True
            elif event.type() == QEvent.Type.Leave:
                anim = self.animator.animateOnHover(
                    obj,
                    ["text", "icon", "background", "border"],
                    [QColor("#ffffff"), QColor("#ffffff"), QColor(37, 37, 37, 255), QColor("#333333")],
                    [QColor("#cccccc"), QColor("#ffffff"), QColor(0, 0, 0, 0), QColor("#1e1e1e")],
                    duration=200
                )
                anim.finished.connect(lambda: obj.setStyleSheet("color: #cccccc; border: 2px solid #1e1e1e; outline: none; text-align: left; padding: 8px 12px; background: transparent; border-radius: 12px;"))
                return True
        return super().eventFilter(obj, event)

    def setBGColour(self):
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QColor("#3e3e3e"))
        gradient.setColorAt(1.0, QColor("#1a1a1a"))
        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

def main():
    app = QApplication(sys.argv)
    window = MainController()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()