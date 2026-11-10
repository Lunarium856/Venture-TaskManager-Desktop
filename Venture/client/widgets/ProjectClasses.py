import Themes
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import os, enum, datetime

def get_resolved_icon_path(icon_str: str) -> str:
    """Resolves an icon path dynamically, supporting built-in assets in icons/core and custom user files"""
    if not icon_str:
        return ""
    
    # Use directly if absolute path is valid
    if os.path.exists(icon_str):
        return icon_str
    
    # resolve relative to root assets/icons/core folder if above doesnt work
    dir_script = os.path.dirname(os.path.abspath(__file__))       # client/widgets
    client_dir = os.path.dirname(dir_script)                      # client
    root_dir = os.path.dirname(client_dir)                        # Venture root
    
    base_name = os.path.basename(icon_str)
    
    # Check assets/icons/core/
    core_path = os.path.join(root_dir, "assets", "icons", "core", base_name)
    if os.path.exists(core_path):
        return core_path
        
    # Fallback to assets/icons/
    legacy_path = os.path.join(root_dir, "assets", "icons", base_name)
    if os.path.exists(legacy_path):
        return legacy_path
        
    return ""

def tint_pixmap(pixmap: QPixmap, color: QColor) -> QPixmap:
    """Tints a QPixmap with a given QColor using SourceIn composition mode"""
    if pixmap.isNull():
        return pixmap
    result = QPixmap(pixmap.size())
    result.fill(Qt.GlobalColor.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(result.rect(), color)
    painter.end()
    return result

class Project:
    def __init__(self, projectID: int, name: str, desc: str, time_create: str, time_elapsed: str, last_update: str, tasks: list, tags: list[QObject], icon, progress: float, deadline):
        maxLenName = 25
        maxLenDesc = 80
        
        self.projectID = projectID
        self.name = name
        self.desc = desc
        self.display_name = name if len(name) < maxLenName else name[:maxLenName] + "..."
        self.display_desc = desc if len(desc) < maxLenDesc else desc[:maxLenDesc] + "..."
        self.time_create = time_create
        self.time_elapsed = time_elapsed
        self.last_update = last_update
        self.tasks = tasks
        self.tags = tags if tags is not None else []
        self.icon = icon if icon else get_resolved_icon_path("icon_settings_anim.png")
        self.progress = progress
        self.deadline = deadline
        self.status = Status.IN_PROGRESS
        self.controller_ref = None

    def update_elapsed_time(self):
        """Calculates current elapsed time from time_create to now, '#d #h #m' format"""
        if not self.time_create:
            self.time_create = datetime.datetime.now().isoformat()
        try:
            create_dt = datetime.datetime.fromisoformat(self.time_create)
            current_dt = datetime.datetime.now()
            diff = current_dt - create_dt
            
            if diff.total_seconds() < 0:
                self.time_elapsed = "0d 0h 0m"
                return

            days = diff.days
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            self.time_elapsed = f"{days}d {hours}h {minutes}m"
        except (ValueError, TypeError):
            self.time_elapsed = "0d 0h 0m"

    def newDisplayWidget(self, parent: QObject=None, JBMLight: QFont=None, JBMBold:QFont=None):
        displayJBMLight = JBMLight if JBMLight else QFont("Arial", 10, QFont.Weight.Light)
        displayJBMBold = JBMBold if JBMBold else QFont("Arial", 14, QFont.Weight.Bold)
        theme = self.controller_ref.current_theme if (self.controller_ref and hasattr(self.controller_ref, 'current_theme')) else Themes.THEME_DEFAULT

        # bgcol1 = QColor(f"{theme.project_bg.hex1}")
        # bgcol2 = QColor(f"{theme.project_bg.hex2}")
        # textcol = QColor(f"{theme.project_text}")
        
        # self.bordercol = QColor(f"{theme.project_border}")
        # self.borderHLcol = QColor(f"{theme.project_border_hover}")

        # progBarcol1 = QColor(f"{theme.project_progress.hex1}")
        # progBarcol2 = QColor(f"{theme.project_progress.hex2}")

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
              f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {theme.project_bg.hex1}, stop:0.8 {theme.project_bg.hex2});"
              f"border: 3px solid {theme.project_border};"
              "border-radius: 15px;"
            "}"
        )

        topHeaderLayout = QHBoxLayout()
        topHeaderLayout.setSpacing(8)

        iconLabel = QLabel("", projectContentWidget)
        resolved_icon = get_resolved_icon_path(self.icon)
        if resolved_icon:
            pixmap = QPixmap(resolved_icon)
            scaledPM = pixmap.scaled(QSize(32, 32), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            tintedPM = tint_pixmap(scaledPM, QColor(theme.project_text))
            iconLabel.setPixmap(tintedPM)
        elif isinstance(self.icon, QIcon):
            pixmap = self.icon.pixmap(QSize(32, 32))
            tintedPM = tint_pixmap(pixmap, QColor(theme.project_text))
            iconLabel.setPixmap(tintedPM)
        iconLabel.setStyleSheet("background: transparent; border: none;")

        nameLabel = QLabel(self.display_name, projectContentWidget)
        nameLabel.setFont(displayJBMBold)
        nameLabel.setStyleSheet(f"color: {theme.project_text}; background: transparent; border: none;")

        topHeaderLayout.addWidget(iconLabel)
        topHeaderLayout.addWidget(nameLabel, 1)

        descLabel = QLabel(self.display_desc, projectContentWidget)
        descLabel.setFont(displayJBMLight)
        descLabel.setWordWrap(True)
        descLabel.setStyleSheet(f"color: {theme.project_text}; background: transparent; border: none;")

        # Status row, contains status badge & elapsed time
        statusRowWidget = QWidget(projectWidget)
        if self.status.value == 1:
            statusRowColour = [QColor(theme.core_negativebutton_bg.hex1), QColor(theme.core_negativebutton_bg.hex2)]
        elif self.status.value == 2:
            statusRowColour = [QColor(theme.core_positivebutton_bg.hex1), QColor(theme.core_positivebutton_bg.hex2)]
        else:
            statusRowColour = [QColor(theme.core_bg_side.hex1), QColor(theme.core_bg_side.hex2)]
        statusRowWidget.setStyleSheet(
            f"background-color: rgba({statusRowColour[0].red()},{statusRowColour[0].green()},{statusRowColour[0].blue()},0.25);"
            f"border: none; border-radius: 8px; padding: 0px;"
        )
        
        statusBadge = QLabel(self.status.name, statusRowWidget)
        statusBadge.setFont(displayJBMBold)
        statusBadge.setStyleSheet(
            f"color: {theme.core_widgets_gentext};"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0.2 {statusRowColour[0].name()}, stop:0.9 {statusRowColour[1].name()});"
            f"border: 2px solid {theme.core_widgets_border};"
            f"border-radius: 8px; padding: 2px;"
        )
        
        elapsed_time_label = QLabel(self.time_elapsed, statusRowWidget)
        elapsed_time_label.setFont(displayJBMBold)
        elapsed_time_label.setStyleSheet(f"color: {theme.project_text}; background: transparent; border: none; padding: 2px;")

        statusRowLayout = QHBoxLayout(statusRowWidget)
        statusRowLayout.setContentsMargins(0, 0, 0, 0)
        statusRowLayout.setSpacing(6)
        statusRowLayout.addWidget(statusBadge)
        statusRowLayout.addStretch()
        statusRowLayout.addWidget(elapsed_time_label)

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
            "QProgressBar {"
                f"border: 2px solid {theme.core_widgets_border}; border-radius: 5px; background-color: {theme.core_widgets_border};"
                "}"
            "QProgressBar::chunk { "
                f"background: qlineargradient(x1:0, y:0.5, x2:1, y2:0.5, stop:0.2 {theme.project_progress.hex1}, stop:0.9 {theme.project_progress.hex2});"
            "   border-radius: 3px; }"
        )

        progValue = QLabel(f"{int(progBar.value())}%", projectContentWidget)
        progValue.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        progValue.setStyleSheet(f"color: {theme.project_text}; background: transparent; border: none;")

        progBarLayout.addWidget(progBar, 1)
        progBarLayout.addWidget(progValue)

        projectContentLayout.addLayout(topHeaderLayout)
        projectContentLayout.addWidget(descLabel)
        projectContentLayout.addStretch()
        projectContentLayout.addWidget(statusRowWidget)
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
    def __init__(self, parentID: int, tagID: int, name: str, desc: str, textcolour, bgcolour):
        self.parentID = parentID
        self.tagID = tagID
        self.name = name
        self.desc = desc
        self.textcolour = textcolour
        self.bgcolour = bgcolour

    def newDisplayWidget(self, parent: QObject=None, parentWidget: QWidget=None):
        theme = self.controller_ref.current_theme if (self.controller_ref and hasattr(self.controller_ref, 'current_theme')) else Themes.THEME_DEFAULT
        tagWidget = QWidget(parentWidget)
        tagWidget.setStyleSheet(
            f"border: 3px solid {theme.core_widgets_border};"
            "border-radius: 10px;"
            f"color: {theme.core_widgets_gentext};"
            f"background-color: {self.colour};"
            "padding: 5px 10px;"
        )
        return tagWidget

class Status(enum.Enum):
    NOT_STARTED = 1
    IN_PROGRESS = 2
    FINISHED = 3