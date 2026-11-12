import Themes
from CustomWidgets import ProjectCardWidget, TaskCardWidget, get_resolved_icon_path, tint_pixmap
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import os, enum, datetime

class Status(enum.Enum):
    NOT_STARTED = 1
    IN_PROGRESS = 2
    FINISHED = 3

class Project:
    def __init__(self, projectID: int, name: str, desc: str, time_create: str, time_elapsed: str, last_update: str, tasks: list, tags: list[QObject], icon, progress: float, deadline, status=Status.NOT_STARTED):
        self.maxLenName = 25
        self.maxLenDesc = 218
        
        self.projectID = projectID
        self.name = name
        self.desc = desc
        self.display_name = name if len(name) < self.maxLenName else name[:self.maxLenName] + "..."
        self.display_desc = desc if len(desc) < self.maxLenDesc else desc[:self.maxLenDesc] + "..."

        if not time_create or "d" in time_create:
            self.time_create = datetime.datetime.now().isoformat()
        else:
            self.time_create = time_create

        self.time_elapsed = time_elapsed
        self.last_update = last_update
        self.tasks = tasks if tasks is not None else []
        self.tags = tags if tags is not None else []
        self.icon = icon if icon else ""
        self.progress = progress
        self.deadline = deadline

        if isinstance(status, Status):
            self.status = status
        elif isinstance(status, str):
            try:
                self.status = Status[status]
            except KeyError:
                self.status = Status.NOT_STARTED
        else:
            self.status = Status.NOT_STARTED
            
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

    def newDisplayWidget(self, parent: QObject=None):
        return ProjectCardWidget(self, parent)

    def projectClicked(self):
        if self.controller_ref:
            self.controller_ref.openProjectDetail(self)

class Task:
    def __init__(self, parentID: int, taskID: int, name: str, desc: str, weight: float, status: bool, tags: list, subtasks: list, progress: float, deadline: str = "No Deadline"):
        self.parentID = parentID
        self.taskID = taskID
        self.name = name
        self.desc = desc
        self.weight = weight 
        self.status = status
        self.tags = tags if tags is not None else []
        self.subtasks = subtasks if subtasks is not None else []
        self.progress = progress
        self.deadline = deadline if deadline else "No Deadline"
        self.controller_ref = None
        self.project_ref = None

    def newDisplayWidget(self, parent: QObject=None, on_update_callback=None):
        return TaskCardWidget(self, parent, on_update_callback)

class Subtask:
    def __init__(self, parentID: int, subtaskID: int, name: str, desc: str, tags: list, weight: int, status=False):
        self.parentID = parentID
        self.subtaskID = subtaskID
        self.name = name
        self.desc = desc
        self.tags = tags if tags is not None else []
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
            f"background-color: {getattr(self, 'bgcolour', '#ff0000')};"
            "padding: 5px 10px;"
        )
        return tagWidget