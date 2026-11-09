import Themes
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import os

class Project:
    def __init__(self, projectID: int, name: str, desc: str, time_create: str, last_update: str, tasks, tags: list[QObject], icon: QIcon, progress: float, deadline):
        self.dir_script = os.path.dirname(os.path.abspath(__file__))
        settings_path = os.path.join(self.dir_script, "settings.ini")
        self.settings = QSettings(settings_path, QSettings.Format.IniFormat)
        
        maxLenName = 25
        maxLenDesc = 80
        
        self.projectID = projectID
        self.name = name
        self.desc = desc
        self.display_name = name if len(name) < maxLenName else name[:maxLenName] + "..."
        self.display_desc = desc if len(desc) < maxLenDesc else desc[:maxLenDesc] + "..."
        self.time_create = time_create
        self.last_update = last_update
        self.tasks = tasks
        self.tags = tags if tags is not None else []
        self.icon = icon
        self.progress = progress
        self.deadline = deadline
        self.controller_ref = None

    def newDisplayWidget(self, parent: QObject=None, JBMLight: QFont=None, JBMBold:QFont=None):
        FOLDER_ICONS = "icons"

        displayJBMLight = JBMLight if JBMLight else QFont("Arial", 10, QFont.Weight.Light)
        displayJBMBold = JBMBold if JBMBold else QFont("Arial", 14, QFont.Weight.Bold)

        theme = self.controller_ref.current_theme if (self.controller_ref and hasattr(self.controller_ref, 'current_theme')) else Themes.THEME_DEFAULT

        bgcol1 = QColor(f"{theme.project_bg.hex1}")
        bgcol2 = QColor(f"{theme.project_bg.hex2}")
        textcol = QColor(f"{theme.project_text}")
        
        # Border colors for hover animation
        self.bordercol = QColor(f"{theme.project_border}")
        self.borderHLcol = QColor(f"{theme.project_border_hover}")

        progBarcol1 = QColor(f"{theme.project_progress.hex1}")
        progBarcol2 = QColor(f"{theme.project_progress.hex2}")

        projectWidget = QWidget(parent)
        projectWidget.setObjectName("projectWidget")
        projectWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        projectWidget.setMinimumWidth(260)
        projectWidget.setMaximumWidth(16777215)
        
        widgetLayout = QVBoxLayout(projectWidget)
        widgetLayout.setContentsMargins(0, 0, 0, 0)

        projectContentWidget = QWidget(projectWidget)
        projectContentWidget.setObjectName("projectContentWidget")
        projectContentWidget.project_instance = self
        projectContentWidget.setMinimumHeight(250)
        projectContentWidget.setCursor(Qt.CursorShape.PointingHandCursor)
        projectContentWidget.mousePressEvent = lambda event: self.projectClicked()

        widgetLayout.addWidget(projectContentWidget)

        projectContentLayout = QVBoxLayout(projectContentWidget) 
        projectContentLayout.setContentsMargins(12, 12, 12, 12)
        projectContentLayout.setSpacing(6)
        
        projectContentWidget.setStyleSheet(
            "QWidget#projectContentWidget {"
              f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {bgcol1.name()}, stop:0.8 {bgcol2.name()});"
              f"border: 3px solid {self.bordercol.name()};"
              "border-radius: 15px;"
            "}"
        )

        topHeaderLayout = QHBoxLayout()
        topHeaderLayout.setSpacing(8)

        iconLabel = QLabel("", projectContentWidget)
        if isinstance(self.icon, str) and os.path.exists(self.icon):
            pixmap = QPixmap(self.icon)
            scaledPM = pixmap.scaled(QSize(32, 32), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            iconLabel.setPixmap(scaledPM)
        elif isinstance(self.icon, QIcon):
            iconLabel.setPixmap(self.icon.pixmap(QSize(32, 32)))
        iconLabel.setStyleSheet("background: transparent; border: none;")

        nameLabel = QLabel(self.display_name, projectContentWidget)
        nameLabel.setFont(displayJBMBold)
        nameLabel.setStyleSheet(f"color: {textcol.name()}; background: transparent; border: none;")

        topHeaderLayout.addWidget(iconLabel)
        topHeaderLayout.addWidget(nameLabel, 1)

        descLabel = QLabel(self.display_desc, projectContentWidget)
        descLabel.setFont(displayJBMLight)
        descLabel.setWordWrap(True)
        descLabel.setStyleSheet(f"color: {textcol.name()}; background: transparent; border: none;")

        statusRowLayout = QHBoxLayout()
        statusBadge = QLabel(" In Progress ", projectContentWidget)
        statusBadge.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        statusBadge.setStyleSheet("color: white; background-color: #5c3566; border: 2px solid black; border-radius: 8px; padding: 2px;")
        
        timeLabel = QLabel("3d 5h 2m", projectContentWidget)
        timeLabel.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        timeLabel.setStyleSheet(f"color: {textcol.name()}; background: transparent; border: none;")

        statusRowLayout.addWidget(statusBadge)
        statusRowLayout.addStretch()
        statusRowLayout.addWidget(timeLabel)

        progBarLayout = QHBoxLayout()
        progBar = QProgressBar(projectContentWidget)
        progBar.setRange(0, 100)
        try:
            safe_progress = int(self.progress)
        except (ValueError, TypeError):
            safe_progress = 0
        progBar.setValue(safe_progress)
        progBar.setTextVisible(False)
        progBar.setFixedHeight(10)
        progBar.setStyleSheet(
            "QProgressBar { border: 2px solid black; border-radius: 5px; background-color: black; }"
            "QProgressBar::chunk { "
                f"background: qlineargradient(x1:0, y:0.5, x2:1, y2:0.5, stop:0.2 {progBarcol1.name()}, stop:0.9 {progBarcol2.name()});"
            "   border-radius: 3px; }"
        )

        progValue = QLabel(f"{int(progBar.value())}%", projectContentWidget)
        progValue.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        progValue.setStyleSheet(f"color: {textcol.name()}; background: transparent; border: none;")

        progBarLayout.addWidget(progBar, 1)
        progBarLayout.addWidget(progValue)

        projectContentLayout.addLayout(topHeaderLayout)
        projectContentLayout.addWidget(descLabel)
        projectContentLayout.addLayout(statusRowLayout)
        projectContentLayout.addLayout(progBarLayout)

        projectWidget.contentWidget = projectContentWidget
        return projectWidget

    def projectClicked(self):
        if self.controller_ref:
            self.controller_ref.openProjectDetail(self)

class Task:
    def __init__(self, parentID: int, taskID: int, name: str, desc: str, weight: float, status: bool, tags: list, subtasks: list, progress: float):
        self.parentID = parentID
        self.taskID = taskID
        self.name = name
        self.desc = desc
        self.weight = weight 
        self.status = status
        self.tags = tags
        self.subtasks = subtasks
        self.progress = progress

class Subtask:
    def __init__(self, parentID: int, subtaskID: int, name: str, desc: str, tags: list, weight: int, status=False):
        self.parentID = parentID
        self.subtaskID = subtaskID
        self.name = name
        self.desc = desc
        self.tags = tags
        self.weight = weight
        self.status = status

class Tag:
    def __init__(self, parentID: int, tagID: int, name: str, desc: str, colour):
        self.parentID = parentID
        self.tagID = tagID
        self.name = name
        self.desc = desc
        self.colour = colour

    def newDisplayWidget(self, parent: QObject=None, parentWidget: QWidget=None):
        tagWidget = QWidget(parentWidget)
        tagWidget.setStyleSheet(
            "border: 3px solid black;"
            "border-radius: 10px;"
            "color: white;"
            f"background-color: {self.colour};"
            "padding: 5px 10px;"
        )
        return tagWidget