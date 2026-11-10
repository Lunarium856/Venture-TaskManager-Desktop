import SettingsHandler, Themes, AnimationHandler, DummyList
from ProjectClasses import Project, Task, Subtask, Tag
from CustomWidgets import HoverButton, RoundedScrollBar
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys, json, os, time, datetime, re, sqlite3

# Data persistence setup moved from DummyList
dir_script = os.path.dirname(os.path.abspath(__file__))       # client/core
client_dir = os.path.dirname(dir_script)                      # client
data_dir = os.path.join(client_dir, "data")

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

projects_json_path = os.path.join(data_dir, "projects.json")

def load_projects_from_json():
    """Loads projects from projects.json, creating it with dummy seed data if missing."""
    if not os.path.exists(projects_json_path):
        initial_projects = DummyList.get_initial_dummy_projects()
        save_projects_to_json(initial_projects)
        return initial_projects
    
    try:
        with open(projects_json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            projects = []
            for item in raw_data:
                tags = [
                    Tag(
                        item["projectID"], 
                        t["tagID"], 
                        t["name"], 
                        t["desc"], 
                        t.get("textcolour", "#ffffff"),
                        t.get("bgcolour", t.get("colour", "#ff0000"))
                    ) 
                    for t in item.get("tags", [])
                ]
                proj = Project(
                    projectID=item["projectID"],
                    name=item["name"],
                    desc=item["desc"],
                    time_create=item["time_create"],
                    time_elapsed=item.get("time_elapsed", "0d 0h 0m"),
                    last_update=item["last_update"],
                    tasks=item.get("tasks", []),
                    tags=tags,
                    icon=item["icon"],
                    progress=item["progress"],
                    deadline=item["deadline"]
                )
                proj.is_archived = item.get("is_archived", False)
                projects.append(proj)
            return projects
    except (json.JSONDecodeError, IOError):
        return DummyList.get_initial_dummy_projects()

def save_projects_to_json(projects_list):
    """Saves the given project objects list to projects.json."""
    raw_data = []
    for proj in projects_list:
        tags_data = [
            {
                "tagID": t.tagID,
                "name": t.name,
                "desc": t.desc,
                "textcolour": getattr(t, "textcolour", "#ffffff"),
                "bgcolour": getattr(t, "bgcolour", "#ff0000")
            } for t in proj.tags
        ]
        raw_data.append({
            "projectID": proj.projectID,
            "name": proj.name,
            "desc": proj.desc,
            "time_create": proj.time_create,
            "time_elapsed": getattr(proj, "time_elapsed", "0d 0h 0m"),
            "last_update": proj.last_update,
            "tasks": proj.tasks,
            "tags": tags_data,
            "icon": proj.icon,
            "progress": proj.progress,
            "deadline": proj.deadline,
            "is_archived": getattr(proj, "is_archived", False)
        })
    
    try:
        with open(projects_json_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=4)
    except IOError as e:
        print(f"Error saving projects: {e}")


class CreateProjectOverlay(QWidget):
    """Modal overlay parented to stackedWidget with 50% opacity backdrop & resize/recentering event filter."""
    def __init__(self, parent=None, animator=None, activeFont=None, on_create_callback=None, controller=None):
        super().__init__(parent)
        self.animator = animator
        self.activeFont = activeFont if activeFont else "Arial"
        self.on_create_callback = on_create_callback
        self.controller = controller
        self.theme = controller.current_theme

        self.is_submitting = False
        
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(0.0)

        if self.parent():
            self.setGeometry(self.parent().rect())
            self.parent().installEventFilter(self)

        # BG Mask
        self.backdrop = QWidget(self)
        self.backdrop.setGeometry(self.rect())
        self.backdrop.setStyleSheet("background-color: rgba(0, 0, 0, 128);")

        # Main Dialog Box
        self.dialogBox = QWidget(self)
        self.dialogBox.setFixedSize(560, 420)
        self.updateDialogPosition()
        self.dialogBox.setStyleSheet(
            "QWidget {"
            f"    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.project_bg.hex1}, stop:1 {self.theme.project_bg.hex2});"
            f"    border: 4px solid {self.theme.project_border};"
            f"    border-radius: 20px;"
            "}"
        )

        dialogLayout = QVBoxLayout(self.dialogBox)
        dialogLayout.setContentsMargins(25, 25, 25, 25)
        dialogLayout.setSpacing(15)

        label_font = QFont(self.activeFont, 11, QFont.Weight.Bold)

        # Project Name Row
        nameLayout = QHBoxLayout()
        nameLabel = QLabel("PROJECT NAME")
        nameLabel.setFont(label_font)
        nameLabel.setFixedWidth(130)
        nameLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")
        self.nameInput = QLineEdit()
        self.nameInput.setFont(label_font)
        self.nameInput.setStyleSheet(
            f"background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_bg_widgets.hex1}, stop:0.8 {self.theme.core_bg_widgets.hex2});"
            f"border: 3px solid {self.theme.core_widgets_border};"
            f"border-radius: 10px; padding: 5px; font-size: 12px; color: {self.theme.core_widgets_gentext};"
        )
        nameLayout.addWidget(nameLabel)
        nameLayout.addWidget(self.nameInput)
        dialogLayout.addLayout(nameLayout)

        # Deadline Row
        deadlineLayout = QHBoxLayout()
        deadlineLabel = QLabel("DEADLINE")
        deadlineLabel.setFont(label_font)
        deadlineLabel.setFixedWidth(130)
        deadlineLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")
        self.deadlineInput = QDateEdit()
        self.deadlineInput.setDate(QDate.currentDate())
        self.deadlineInput.setCalendarPopup(True)
        self.deadlineInput.setFont(label_font)
        self.deadlineInput.setStyleSheet(
            f"QDateEdit {{"
            f"    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_bg_widgets.hex1}, stop:0.8 {self.theme.core_bg_widgets.hex2});"
            f"    border: 3px solid {self.theme.core_widgets_border};"
            f"    border-radius: 10px; padding: 5px; font-size: 12px; color: {self.theme.core_widgets_gentext};"
            f"}}"
            f"QDateEdit::drop-down {{"
            f"    subcontrol-origin: padding;"
            f"    subcontrol-position: top right;"
            f"    width: 30px;"
            f"    border-left: 3px solid {self.theme.core_widgets_border};"
            f"    border-top-right-radius: 7px;"
            f"    border-bottom-right-radius: 7px;"
            f"    background-color: {self.theme.scroll_track};"
            f"}}"
            f"QDateEdit::down-arrow {{"
            f"    width: 0px;"
            f"    height: 0px;"
            f"    border-left: 5px solid transparent;"
            f"    border-right: 5px solid transparent;"
            f"    border-top: 6px solid {self.theme.core_widgets_gentext};"
            f"    margin-right: 1px;"
            f"}}"
        )
        calendar = self.deadlineInput.calendarWidget()
        if calendar:
            calendar.setMinimumWidth(340)
            calendar.setMinimumHeight(260)
            calendar.setFont(QFont(self.activeFont, 11, QFont.Weight.Light))
            
            header_format = QTextCharFormat()
            header_format.setBackground(QColor(self.theme.core_bg_widgets.hex1))
            header_format.setForeground(QColor(self.theme.core_widgets_gentext))
            calendar.setHeaderTextFormat(header_format)

            calendar.setStyleSheet(
                # Outer popup container
                f"QCalendarWidget {{"
                f"    background-color: {self.theme.core_bg_widgets.hex2};"
                f"    border: 3px solid {self.theme.core_widgets_border};"
                f"    border-radius: 12px;"
                f"    selection-background-color: {self.theme.sidebar_activebtn};"
                f"    selection-color: black;"
                f"}}"
                
                # Top NavBar
                f"QCalendarWidget QWidget#qt_calendar_navigationbar {{"
                f"    background-color: {self.theme.core_bg_widgets.hex1};"
                f"    border-top-left-radius: 9px;"
                f"    border-top-right-radius: 9px;"
                f"    border-bottom: 1px solid {self.theme.core_widgets_border};"
                f"    padding: 4px;"
                f"    margin: 4px 4px 0px 4px;"
                f"}}"
                f"QCalendarWidget QToolButton {{"
                f"    color: {self.theme.core_widgets_gentext};"
                f"    background-color: {self.theme.scroll_track};"
                f"    border: 1px solid {self.theme.core_widgets_border};"
                f"    border-radius: 5px;"
                f"    margin: 3px;"
                f"    padding: 3px;"
                f"}}"
                f"QCalendarWidget QToolButton:hover {{"
                f"    background-color: {self.theme.sidebar_activebtn};"
                f"    color: black;"
                f"}}"
                
                # Dropdown menu for month/year selectors
                f"QCalendarWidget QMenu {{"
                f"    background-color: {self.theme.core_bg_widgets.hex2};"
                f"    color: {self.theme.core_widgets_gentext};"
                f"    border: 1px solid {self.theme.core_widgets_border};"
                f"}}"
                f"QCalendarWidget QMenu::item:selected {{"
                f"    background-color: {self.theme.sidebar_activebtn};"
                f"    color: black;"
                f"}}"
                
                # Month Grid Table View
                f"QCalendarWidget QTableView {{"
                f"    background-color: {self.theme.core_bg_widgets.hex1};"
                f"    color: {self.theme.core_widgets_gentext};"
                f"    border: none;"
                f"    outline: none;"
                f"    margin: 4px;"
                f"    border-bottom-left-radius: 9px;"
                f"    border-bottom-right-radius: 9px;"
                f"}}"
            )
        deadlineLayout.addWidget(deadlineLabel, alignment=Qt.AlignmentFlag.AlignTop)
        deadlineLayout.addWidget(self.deadlineInput)
        dialogLayout.addLayout(deadlineLayout)

        # Description Row
        descLayout = QHBoxLayout()
        descLabel = QLabel("DESCRIPTION")
        descLabel.setFont(label_font)
        descLabel.setFixedWidth(130)
        descLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")
        self.descInput = QTextEdit()
        self.descInput.setFont(label_font)
        self.descInput.setFixedHeight(75)
        self.descInput.setStyleSheet(
            f"background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_bg_widgets.hex1}, stop:0.8 {self.theme.core_bg_widgets.hex2});"
            f"border: 3px solid {self.theme.core_widgets_border}; " 
            f"border-radius: 10px; padding: 5px; font-size: 12px; color: {self.theme.core_widgets_gentext};"
        )
        descLayout.addWidget(descLabel, alignment=Qt.AlignmentFlag.AlignTop)
        descLayout.addWidget(self.descInput)
        dialogLayout.addLayout(descLayout)

        midLayout = QHBoxLayout()
        midLayout.setSpacing(20)
        dialogLayout.addLayout(midLayout)

        bottomBtnLayout = QHBoxLayout()
        bottomBtnLayout.setSpacing(20)
        
        self.btnCreate = QPushButton("CREATE")
        self.btnCreate.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.btnCreate.setFixedHeight(40)
        self.btnCreate.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_positivebutton_bg.hex1}, stop:0.8 {self.theme.core_positivebutton_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_positivebutton_border}; border-radius: 18px;"
        )
        self.btnCreate.clicked.connect(self.acceptOverlay)

        self.btnCancel = QPushButton("CANCEL")
        self.btnCancel.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.btnCancel.setFixedHeight(40)
        self.btnCancel.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_negativebutton_bg.hex1}, stop:0.8 {self.theme.core_negativebutton_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_negativebutton_border}; border-radius: 18px;"
        )
        self.btnCancel.clicked.connect(self.rejectOverlay)

        bottomBtnLayout.addWidget(self.btnCreate)
        bottomBtnLayout.addWidget(self.btnCancel)
        dialogLayout.addLayout(bottomBtnLayout)

        self.show()
        self.fadeInAnim = self.animator.createAnimation(self, "opacity", 0.0, 1.0, duration=300)
        if self.fadeInAnim:
            self.fadeInAnim.start()

    def updateDialogPosition(self):
        parent_rect = self.parent().rect() if self.parent() else self.rect()
        box_x = (parent_rect.width() - self.dialogBox.width()) // 2
        box_y = (parent_rect.height() - self.dialogBox.height()) // 2
        self.dialogBox.move(box_x, box_y)

    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == QEvent.Type.Resize:
            self.setGeometry(self.parent().rect())
            self.backdrop.setGeometry(self.rect())
            self.updateDialogPosition()
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.backdrop.setGeometry(self.rect())
        self.updateDialogPosition()

    def acceptOverlay(self):
        if self.is_submitting:
            return
        
        name = self.nameInput.text().strip()
        deadline = self.deadlineInput.text().strip()
        desc = self.descInput.toPlainText().strip()
        if name and self.on_create_callback:
            self.is_submitting = True
            self.on_create_callback(name, deadline, desc)
            QTimer.singleShot(250, lambda: setattr(self, 'is_submitting', False))
        self.closeOverlay()

    def rejectOverlay(self):
        self.closeOverlay()

    def closeOverlay(self):
        if self.parent():
            self.parent().removeEventFilter(self)
        self.fadeOutAnim = self.animator.createAnimation(self, "opacity", 1.0, 0.0, duration=300)
        if self.fadeOutAnim:
            self.fadeOutAnim.finished.connect(self.deleteLater)
            self.fadeOutAnim.start()
        else:
            self.deleteLater()
        if self.controller:
            self.controller.is_modal_active = False


class ConfirmActionOverlay(QWidget):
    """Reusable modal overlay for action confirmations"""
    def __init__(self, parent=None, animator=None, activeFont=None, title="CONFIRMATION", message="", on_confirm=None, controller=None):
        super().__init__(parent)
        self.animator = animator
        self.activeFont = activeFont if activeFont else "Arial"
        self.on_confirm = on_confirm
        self.controller = controller
        self.theme = controller.current_theme if controller and hasattr(controller, 'current_theme') else Themes.THEME_DEFAULT

        self.is_submitting = False
        
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(0.0)

        if self.parent():
            self.setGeometry(self.parent().rect())
            self.parent().installEventFilter(self)

        # BG Mask
        self.backdrop = QWidget(self)
        self.backdrop.setGeometry(self.rect())
        self.backdrop.setStyleSheet("background-color: rgba(0, 0, 0, 128);")

        # Main Dialog Box
        self.dialogBox = QWidget(self)
        self.dialogBox.setFixedSize(500, 260)
        self.updateDialogPosition()
        self.dialogBox.setStyleSheet(
            "QWidget {"
            f"    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.project_bg.hex1}, stop:1 {self.theme.project_bg.hex2});"
            f"    border: 4px solid {self.theme.project_border};"
            f"    border-radius: 20px;"
            "}"
        )

        dialogLayout = QVBoxLayout(self.dialogBox)
        dialogLayout.setContentsMargins(25, 25, 25, 25)
        dialogLayout.setSpacing(15)

        label_font = QFont(self.activeFont, 13, QFont.Weight.Bold)

        # Title Label
        titleLabel = QLabel(title)
        titleLabel.setFont(label_font)
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titleLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")
        dialogLayout.addWidget(titleLabel)

        # Message Label
        msgLabel = QLabel(message)
        msgLabel.setFont(QFont(self.activeFont, 11, QFont.Weight.Normal))
        msgLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msgLabel.setWordWrap(True)
        msgLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")
        dialogLayout.addWidget(msgLabel, 1)

        # Buttons Layout
        bottomBtnLayout = QHBoxLayout()
        bottomBtnLayout.setSpacing(20)
        
        self.btnConfirm = QPushButton("CONFIRM")
        self.btnConfirm.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.btnConfirm.setFixedHeight(40)
        self.btnConfirm.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_negativebutton_bg.hex1}, stop:0.8 {self.theme.core_negativebutton_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_negativebutton_border}; border-radius: 18px;"
        )
        self.btnConfirm.clicked.connect(self.acceptOverlay)

        self.btnCancel = QPushButton("CANCEL")
        self.btnCancel.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.btnCancel.setFixedHeight(40)
        self.btnCancel.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_neutralbutton_bg.hex1}, stop:0.8 {self.theme.core_neutralbutton_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_neutralbutton_border}; border-radius: 18px;"
        )
        self.btnCancel.clicked.connect(self.rejectOverlay)

        bottomBtnLayout.addWidget(self.btnConfirm)
        bottomBtnLayout.addWidget(self.btnCancel)
        dialogLayout.addLayout(bottomBtnLayout)

        self.show()
        self.fadeInAnim = self.animator.createAnimation(self, "opacity", 0.0, 1.0, duration=300)
        if self.fadeInAnim:
            self.fadeInAnim.start()

    def updateDialogPosition(self):
        parent_rect = self.parent().rect() if self.parent() else self.rect()
        box_x = (parent_rect.width() - self.dialogBox.width()) // 2
        box_y = (parent_rect.height() - self.dialogBox.height()) // 2
        self.dialogBox.move(box_x, box_y)

    def eventFilter(self, obj, event):
        if obj == self.parent() and event.type() == QEvent.Type.Resize:
            self.setGeometry(self.parent().rect())
            self.backdrop.setGeometry(self.rect())
            self.updateDialogPosition()
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.backdrop.setGeometry(self.rect())
        self.updateDialogPosition()

    def acceptOverlay(self):
        if self.is_submitting:
            return
        self.is_submitting = True
        if self.on_confirm:
            self.on_confirm()
        self.closeOverlay()

    def rejectOverlay(self):
        self.closeOverlay()

    def closeOverlay(self):
        if self.parent():
            self.parent().removeEventFilter(self)
        self.fadeOutAnim = self.animator.createAnimation(self, "opacity", 1.0, 0.0, duration=300)
        if self.fadeOutAnim:
            self.fadeOutAnim.finished.connect(self.deleteLater)
            self.fadeOutAnim.start()
        else:
            self.deleteLater()
        if self.controller:
            self.controller.is_modal_active = False


class ProjectDetailPage(QWidget):
    def __init__(self, controller, project):
        super().__init__()
        self.controller = controller
        self.project = project
        self.activeFont = self.controller.activeJetFamFont
        self.theme = self.controller.current_theme

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        headerWidget = QWidget()
        headerWidget.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {self.theme.core_bg_widgets.hex1}, stop:1 {self.theme.core_bg_widgets.hex2});"
            f"border: 3px solid {self.theme.core_widgets_border}; border-radius: 15px;"
        )
        hLayout = QVBoxLayout(headerWidget)
        hLayout.setContentsMargins(20, 20, 20, 20)
        
        titleLbl = QLabel(self.project.name)
        titleLbl.setFont(QFont(self.activeFont, 22, QFont.Weight.Bold))
        titleLbl.setStyleSheet(
            f"color: {self.theme.sidebar_activebtn};"
            "border: none; background: transparent;"
        )
        
        descLbl = QLabel(self.project.desc)
        descLbl.setFont(QFont(self.activeFont, 12, QFont.Weight.Light))
        descLbl.setWordWrap(True)
        descLbl.setStyleSheet(
            f"color: {self.theme.core_widgets_gentext};"
            "border: none; background: transparent;")
        
        hLayout.addWidget(titleLbl)
        hLayout.addWidget(descLbl)
        layout.addWidget(headerWidget)

        tasksHeader = QLabel("TASKS & SUBTASKS")
        tasksHeader.setFont(QFont(self.activeFont, 16, QFont.Weight.Bold))
        tasksHeader.setStyleSheet(f"color: {self.theme.core_widgets_gentext};")
        layout.addWidget(tasksHeader)

        btnContainer = QWidget(self)
        btnContainerLayout = QHBoxLayout(btnContainer)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        contentW = QWidget()
        contentW.setStyleSheet("background: transparent;")
        tLayout = QVBoxLayout(contentW)
        tLayout.setSpacing(12)

        sample_tasks = [
            {"name": "Task 1: Core Architecture", "subs": ["Setup Database Schema", "Configure API Endpoints", "Test Auth Flow"]},
            {"name": "Task 2: UI Styling & Polish", "subs": ["Implement Retro Borders", "Adjust Gradient Stops", "Hook up Hover Animations"]}
        ]

        for t in sample_tasks:
            taskBox = QWidget()
            taskBox.setStyleSheet(
                f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {self.theme.project_bg.hex1}, stop:1 {self.theme.project_bg.hex2});"
                f"border: 3px solid {self.theme.project_border}; border-radius: 15px;"
            )
            tbLayout = QVBoxLayout(taskBox)
            tbLayout.setContentsMargins(15, 12, 15, 12)
            
            tName = QLabel(t["name"])
            tName.setFont(QFont(self.activeFont, 14, QFont.Weight.Bold))
            tName.setStyleSheet("color: #ffa500; border: none; background: transparent;")
            tbLayout.addWidget(tName)

            for sub in t["subs"]:
                subBox = QWidget()
                subBox.setStyleSheet("background: rgba(30,30,30,0.7); border: 2px solid #555; border-radius: 8px;")
                sbLayout = QHBoxLayout(subBox)
                sbLayout.setContentsMargins(10, 8, 10, 8)
                
                sLbl = QLabel(f"• {sub}")
                sLbl.setFont(QFont(self.activeFont, 11, QFont.Weight.Normal))
                sLbl.setStyleSheet("color: white; border: none; background: transparent;")
                sbLayout.addWidget(sLbl)
                tbLayout.addWidget(subBox)

            tLayout.addWidget(taskBox)

        tLayout.addStretch()
        scroll.setWidget(contentW)
        layout.addWidget(scroll, 1)
        layout.addWidget(btnContainer)

        # Action Buttons
        self.btnBack = QPushButton("BACK TO PROJECTS")
        self.btnBack.setObjectName("backToList")
        self.btnBack.setFont(QFont(self.activeFont, 14, QFont.Weight.Bold))
        self.btnBack.setFixedHeight(45)
        self.btnBack.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_neutralbutton_bg.hex1}, stop:1 {self.theme.core_neutralbutton_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_neutralbutton_border}; border-radius: 18px;"
        )
        self.btnBack.clicked.connect(self.controller.returnToProjects)

        self.btnArchive = QPushButton("ARCHIVE PROJECT")
        self.btnArchive.setObjectName("archiveProject")
        self.btnArchive.setFont(QFont(self.activeFont, 14, QFont.Weight.Bold))
        self.btnArchive.setFixedHeight(45)
        self.btnArchive.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_neutralbutton_bg.hex1}, stop:1 {self.theme.core_neutralbutton_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_neutralbutton_border}; border-radius: 18px;"
        )
        self.btnArchive.clicked.connect(self.archiveProjectPrompt)

        self.btnDelete = QPushButton("DELETE PROJECT")
        self.btnDelete.setObjectName("deleteProject")
        self.btnDelete.setFont(QFont(self.activeFont, 14, QFont.Weight.Bold))
        self.btnDelete.setFixedHeight(45)
        self.btnDelete.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_negativebutton_bg.hex1}, stop:1 {self.theme.core_negativebutton_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_negativebutton_border}; border-radius: 18px;"
        )
        self.btnDelete.clicked.connect(self.deleteProjectPrompt)

        btnContainerLayout.addWidget(self.btnBack)
        btnContainerLayout.addWidget(self.btnArchive)
        btnContainerLayout.addWidget(self.btnDelete)

    def archiveProjectPrompt(self):
        self.controller.is_modal_active = True
        ConfirmActionOverlay(
            parent=self.controller.stackedWidget,
            animator=self.controller.animator,
            activeFont=self.activeFont,
            title="ARCHIVE PROJECT",
            message=f"Are you sure you want to archive '{self.project.name}'?\nIt will be hidden from your active project list.",
            on_confirm=self.performArchive,
            controller=self.controller
        )

    def performArchive(self):
        proj_id = self.project.projectID
        all_projects = load_projects_from_json()
        for p in all_projects:
            if p.projectID == proj_id:
                p.is_archived = True
                break
        save_projects_to_json(all_projects)
        self.controller.returnToProjects()

    def deleteProjectPrompt(self):
        self.controller.is_modal_active = True
        ConfirmActionOverlay(
            parent=self.controller.stackedWidget,
            animator=self.controller.animator,
            activeFont=self.activeFont,
            title="DELETE PROJECT",
            message=f"Are you sure you want to delete '{self.project.name}'?\nThis action cannot be undone.",
            on_confirm=self.performDelete,
            controller=self.controller
        )

    def performDelete(self):
        proj_id = self.project.projectID
        all_projects = load_projects_from_json()
        all_projects = [p for p in all_projects if p.projectID != proj_id]
        save_projects_to_json(all_projects)
        self.controller.returnToProjects()


class ProjectListPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.settingsFunctions = self.controller.settingsFunctions
        self.animator = self.controller.animator
        self.activeJetFamFont = self.controller.activeJetFamFont
        self.theme = self.controller.current_theme
        
        self.saved_projects = [p for p in load_projects_from_json() if not getattr(p, 'is_archived', False)]

        self.mainContentLayout = QVBoxLayout(self)
        self.mainContentLayout.setObjectName("mainContentLayout")
        self.mainContentLayout.setContentsMargins(10, 15, 10, 10)
        self.mainContentLayout.setSpacing(12)

        self.topActionBarLayout = QHBoxLayout()
        self.topActionBarLayout.setSpacing(15)

        self.main_button_newProject = HoverButton("NEW PROJECT", self, self.animator)
        self.main_button_newProject.setObjectName("actionButton")
        self.main_button_newProject.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.main_button_newProject.setFont(QFont(self.activeJetFamFont, 16, QFont.Weight.Bold))
        self.main_button_newProject.setFixedHeight(45)
        self.main_button_newProject.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.main_button_newProject.setStyleSheet(
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_positivebutton_border}; outline: none; border-radius: 18px; text-align: center;"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_positivebutton_bg.hex1}, stop:1 {self.theme.core_positivebutton_bg.hex2});"
        )
        self.main_button_newProject.clicked.connect(self.createProject)
        self.main_button_newProject.setHoverData(["border"], [self.theme.core_positivebutton_border], [self.theme.core_positivebutton_border_hover])

        self.btnTags = HoverButton("TAGS", self, self.animator)
        self.btnTags.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btnTags.setFont(QFont(self.activeJetFamFont, 16, QFont.Weight.Bold))
        self.btnTags.setFixedHeight(45); self.btnTags.setFixedWidth(130)
        self.btnTags.setStyleSheet(
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_positivebutton_border}; outline: none; border-radius: 18px; text-align: center;"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_positivebutton_bg.hex1}, stop:1 {self.theme.core_positivebutton_bg.hex2});"
        )
        self.btnTags.setHoverData(["border"], [self.theme.core_positivebutton_border], [self.theme.core_positivebutton_border_hover])

        self.btnArchived = HoverButton("ARCHIVED", self, self.animator)
        self.btnArchived.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btnArchived.setFont(QFont(self.activeJetFamFont, 16, QFont.Weight.Bold))
        self.btnArchived.setFixedHeight(45); self.btnArchived.setFixedWidth(160)
        self.btnArchived.setStyleSheet(
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_positivebutton_border}; outline: none; border-radius: 18px; text-align: center;"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_positivebutton_bg.hex1}, stop:1 {self.theme.core_positivebutton_bg.hex2});"
        )
        self.btnArchived.setHoverData(["border"], [self.theme.core_positivebutton_border], [self.theme.core_positivebutton_border_hover])

        self.topActionBarLayout.addWidget(self.main_button_newProject)
        self.topActionBarLayout.addWidget(self.btnTags)
        self.topActionBarLayout.addWidget(self.btnArchived)

        self.gridContainerWidget = QWidget(self)
        self.gridContainerWidget.setStyleSheet(
            f"background-color: {self.theme.core_bg_lists if self.theme.core_bg_lists else 'rgba(10, 10, 10, 0.5)'};"
            f"border: none; border-radius: 20px;"
        )
        
        gridContainerLayout = QVBoxLayout(self.gridContainerWidget)
        gridContainerLayout.setContentsMargins(8, 8, 8, 8)

        self.scrollArea = QScrollArea(self.gridContainerWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setStyleSheet("background: transparent; border: none;")
        
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        v_bar = RoundedScrollBar(Qt.Orientation.Vertical, self.scrollArea, controller=self.controller)
        v_bar.setFixedWidth(16)
        h_bar = RoundedScrollBar(Qt.Orientation.Horizontal, self.scrollArea, controller=self.controller)
        h_bar.setFixedHeight(16)
        
        self.scrollArea.setVerticalScrollBar(v_bar)
        self.scrollArea.setHorizontalScrollBar(h_bar)
        
        self.scrollContentWidget = QWidget()
        self.scrollContentWidget.setStyleSheet("background: transparent; border: none;")
        self.projectsGrid = QGridLayout(self.scrollContentWidget)
        self.projectsGrid.setSpacing(15)
        self.scrollContentWidget.setLayout(self.projectsGrid)
        self.projectsGrid.setContentsMargins(10, 10, 10, 10)

        self.scrollArea.setWidget(self.scrollContentWidget)
        gridContainerLayout.addWidget(self.scrollArea)

        bottomBarLayout = QHBoxLayout()
        bottomBarLayout.setContentsMargins(5, 0, 5, 0)

        self.searchBar = QLineEdit(self)
        self.searchBar.setPlaceholderText("🔍 SEARCH...")
        self.searchBar.setFont(QFont(self.activeJetFamFont, 10, QFont.Weight.Bold))
        self.searchBar.setFixedHeight(35); self.searchBar.setFixedWidth(280)
        self.searchBar.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {self.theme.core_bg_side.hex1}, stop:1 {self.theme.core_bg_side.hex2});"
            f"color: {self.theme.core_widgets_gentext};"
            f"border: 2px solid {self.theme.core_widgets_border};"
            f"border-radius: 12px; padding-left: 10px;"
        )

        bottomBarLayout.addWidget(self.searchBar)
        bottomBarLayout.addStretch()

        self.mainContentLayout.addLayout(self.topActionBarLayout)
        self.mainContentLayout.addWidget(self.gridContainerWidget, 1)
        self.mainContentLayout.addLayout(bottomBarLayout)

        self.populateGrid()

    def showEvent(self, event):
        """Automatically re-updates/repopulates the grid whenever returning to the Project List page."""
        super().showEvent(event)
        self.populateGrid()

    def populateGrid(self):
        while self.projectsGrid.count():
            item = self.projectsGrid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        all_projects = load_projects_from_json()
        for p in all_projects:
            p.update_elapsed_time()
        save_projects_to_json(all_projects)
        self.saved_projects = [p for p in all_projects if not getattr(p, 'is_archived', False)]

        max_cols = 4
        for i in range(max_cols):
            self.projectsGrid.setColumnStretch(i, 1)

        if self.saved_projects:
            row, col = 0, 0
            for project in self.saved_projects:
                project.controller_ref = self.controller
                projectWidget = project.newDisplayWidget(
                    self.scrollContentWidget,
                    JBMLight=QFont(self.activeJetFamFont, 10, QFont.Weight.Light),
                    JBMBold=QFont(self.activeJetFamFont, 14, QFont.Weight.Bold)
                )
                
                projectWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                projectWidget.setMinimumWidth(260)
                projectWidget.setMaximumWidth(16777215)
                
                if hasattr(projectWidget, 'contentWidget'):
                    projectWidget.contentWidget.installEventFilter(self)

                self.projectsGrid.addWidget(projectWidget, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

            if col > 0:
                for c in range(col, max_cols):
                    dummy = QWidget()
                    dummy.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
                    dummy.setStyleSheet("background: transparent; border: none;")
                    self.projectsGrid.addWidget(dummy, row, c)
        else:
            self.emptyProjectsList()

    def eventFilter(self, obj: QObject, event):
        if self.controller.is_modal_active:
            return True

        if isinstance(obj, QWidget) and obj.objectName() == "projectContentWidget":
            proj_inst = getattr(obj, 'project_instance', None)
            if proj_inst:
                theme = self.controller.current_theme if (self.controller and hasattr(self.controller, 'current_theme')) else Themes.THEME_DEFAULT
                b_col = getattr(proj_inst, 'bordercol', QColor(f"{theme.project_border}")).name()
                hl_col = getattr(proj_inst, 'borderHLcol', QColor(f"{theme.project_border_hover}")).name()
                if event.type() == QEvent.Type.Enter:
                    self.animator.animateOnHover(obj, ["border"], [b_col], [hl_col])
                    return True
                elif event.type() == QEvent.Type.Leave:
                    self.animator.animateOnHover(obj, ["border"], [hl_col], [b_col])
                    return True
        return super().eventFilter(obj, event)

    def emptyProjectsList(self):
        self.emptyProjectsAlert = QLabel("You currently have no projects.\nClick 'NEW PROJECT' above to start one!", self)
        self.emptyProjectsAlert.setFont(QFont(self.activeJetFamFont, 16, QFont.Weight.Light))
        self.emptyProjectsAlert.setStyleSheet(
            f"color: {self.theme.core_widgets_gentext}; "
            f"text-align: center; "
            f"border: none; background: transparent;")
        self.emptyProjectsAlert.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.projectsGrid.addWidget(self.emptyProjectsAlert, 0, 0)

    def createProject(self):
        self.controller.is_modal_active = True
        CreateProjectOverlay(
            parent=self.controller.stackedWidget,
            animator=self.animator,
            activeFont=self.activeJetFamFont,
            on_create_callback=self.onNewProjectCreated,
            controller=self.controller
        )

    def onNewProjectCreated(self, name, deadline, desc):
        create_dt = datetime.datetime.now()
        current_dt = datetime.datetime.now()
        diff = current_dt - create_dt
        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds % 3600) // 60
        time_elapsed_str = f"{days}d {hours}h {minutes}m"

        new_proj = Project(
            projectID=int(time.time()),
            name=name,
            desc=desc if desc else "No description provided.",
            time_create=create_dt.isoformat(),
            time_elapsed=time_elapsed_str,
            last_update=datetime.datetime.now().isoformat(),
            tasks=[],
            tags=[],
            icon="",
            progress=0.0,
            deadline=deadline if deadline else "No Deadline"
        )
        new_proj.controller_ref = self.controller
        
        all_projects = load_projects_from_json()
        all_projects.append(new_proj)
        save_projects_to_json(all_projects)
        self.populateGrid()