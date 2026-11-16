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

class Weight(enum.Enum):
    LOW_PRIORITY = 1
    MEDIUM_PRIORITY = 2
    HIGH_PRIORITY = 3

class Project:
    def __init__(self, projectID: int, name: str, desc: str, time_create: str, time_elapsed: str, last_update: str, tasks: list, tags: list[QObject], icon, progress: float, deadline, status=Status.NOT_STARTED, time_start: str = ""):
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
        self.time_start = time_start
        self.last_update = last_update
        self.tasks = tasks if tasks is not None else []
        self.tags = tags if tags is not None else []
        self.icon = icon if icon else ""
        self.progress = progress
        self.deadline = deadline
        self.controller_ref = None

        if isinstance(status, Status):
            self.status = status
        elif isinstance(status, str):
            try:
                self.status = Status[status]
            except KeyError:
                self.status = Status.NOT_STARTED
        else:
            self.status = Status.NOT_STARTED

    def update_elapsed_time(self):
        """Calculates current elapsed time from time_start only when in progress, '#d #h #m' format"""
        if self.status != Status.IN_PROGRESS:
            if self.status == Status.NOT_STARTED:
                self.time_elapsed = "0d 0h 0m"
                return
            elif self.status == Status.FINISHED:
                if not self.time_start:
                    self.time_elapsed = "0d 0h 0m"
                return

        if not self.time_start: # Fallback for projects that dont have a time_start
            self.time_start = datetime.datetime.now().isoformat()
            return

        try:
            start_dt = datetime.datetime.fromisoformat(self.time_start)
            current_dt = datetime.datetime.now()
            diff = current_dt - start_dt
            
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
        """Creates a new ProjectCardWidget."""
        return ProjectCardWidget(self, parent)

    def recalculate_progress(self):
        """Calculates project progress based on task weights and completion rules."""
        # Check if tasks exist
        tasks = getattr(self, 'tasks', [])
        if not tasks:
            self.progress = 0.0
            self.status = Status.NOT_STARTED
            return

        # Calculate
        total_weight_units = 0.0
        completed_weight_units = 0.0

        for t in tasks:
            t_weight = t.weight.value if hasattr(t.weight, 'value') else int(t.weight)
            total_weight_units += t_weight

            subtasks = getattr(t, 'subtasks', [])
            if subtasks:
                sub_total_w = sum((sub.weight.value if hasattr(sub.weight, 'value') else int(sub.weight)) for sub in subtasks)
                sub_done_w = sum((sub.weight.value if hasattr(sub.weight, 'value') else int(sub.weight)) for sub in subtasks if getattr(sub, 'status', False))
                
                sub_ratio = (sub_done_w / sub_total_w) if sub_total_w > 0 else 0.0
                task_normalized_contribution = sub_ratio * 3.0
                
                t.progress = sub_ratio * 100.0
                t.status = (sub_ratio >= 1.0)
                
                completed_weight_units += (task_normalized_contribution / 3.0) * t_weight
            else:
                is_done = bool(getattr(t, 'status', False))
                t.progress = 100.0 if is_done else 0.0
                if is_done:
                    completed_weight_units += t_weight

        if total_weight_units > 0:
            self.progress = min(100.0, max(0.0, (completed_weight_units / total_weight_units) * 100.0))
        else:
            self.progress = 0.0

        # Update project status based on progress
        if self.progress >= 100.0:
            self.status = Status.FINISHED
        elif self.progress > 0.0:
            self.status = Status.IN_PROGRESS
        else:
            any_started = any(bool(getattr(t, 'status', False)) or float(getattr(t, 'progress', 0.0)) > 0.0 for t in tasks)
            self.status = Status.IN_PROGRESS if any_started else Status.NOT_STARTED

        # Record start timestamp when status changes to "In Progress" for the first time
        if self.status == Status.IN_PROGRESS and not self.time_start:
            self.time_start = datetime.datetime.now().isoformat()

    def projectClicked(self):
        if self.controller_ref:
            self.controller_ref.openProjectDetail(self)

class Task:
    def __init__(self, parentID: int, taskID: int, name: str, desc: str, weight, status: bool, tags: list, subtasks: list, progress: float, deadline: str = "No Deadline"):
        self.parentID = parentID
        self.taskID = taskID
        self.name = name
        self.desc = desc
        
        if isinstance(weight, Weight):
            self.weight = weight
        elif isinstance(weight, str):
            try:
                self.weight = Weight[weight]
            except KeyError:
                self.weight = Weight.MEDIUM_PRIORITY
        else:
            self.weight = Weight.MEDIUM_PRIORITY

        self.status = status
        self.tags = tags if tags is not None else []
        
        parsed_subtasks = []
        for sub in (subtasks if subtasks is not None else []):
            if isinstance(sub, dict):
                parsed_subtasks.append(Subtask(
                    parentID=sub.get("parentID", taskID),
                    subtaskID=sub.get("subtaskID", int(datetime.datetime.now().timestamp())),
                    name=sub.get("name", ""),
                    desc=sub.get("desc", ""),
                    tags=sub.get("tags", []),
                    weight=sub.get("weight", Weight.MEDIUM_PRIORITY),
                    status=sub.get("status", False)
                ))
            elif isinstance(sub, Subtask):
                parsed_subtasks.append(sub)
        self.subtasks = parsed_subtasks

        self.progress = progress
        self.deadline = deadline if deadline else "No Deadline"
        self.controller_ref = None
        self.project_ref = None

    def newDisplayWidget(self, parent: QObject=None, on_update_callback=None):
        widget = TaskCardWidget(self, parent, on_update_callback)
        self.widget_ref = widget
        return widget

    def recalculate_task_progress(self):
        subtasks = getattr(self, 'subtasks', [])
        if not subtasks:
            return

        sub_total_w = sum((sub.weight.value if hasattr(sub.weight, 'value') else int(sub.weight)) for sub in subtasks)
        sub_done_w = sum((sub.weight.value if hasattr(sub.weight, 'value') else int(sub.weight)) for sub in subtasks if getattr(sub, 'status', False))

        sub_ratio = (sub_done_w / sub_total_w) if sub_total_w > 0 else 0.0
        self.progress = sub_ratio * 100.0
        self.status = (sub_ratio >= 1.0)
        
        if hasattr(self, 'widget_ref') and self.widget_ref:
            if hasattr(self.widget_ref, 'update_status_visuals'):
                self.widget_ref.update_status_visuals(self.status)

class Subtask:
    def __init__(self, parentID: int, subtaskID: int, name: str, desc: str, tags: list, weight, status=False):
        self.parentID = parentID
        self.subtaskID = subtaskID
        self.name = name
        self.desc = desc
        self.tags = tags if tags is not None else []
        
        if isinstance(weight, Weight):
            self.weight = weight
        elif isinstance(weight, str):
            try:
                self.weight = Weight[weight]
            except KeyError:
                self.weight = Weight.MEDIUM_PRIORITY
        elif isinstance(weight, int):
            try:
                self.weight = Weight(weight)
            except ValueError:
                self.weight = Weight.MEDIUM_PRIORITY
        else:
            self.weight = Weight.MEDIUM_PRIORITY

        self.status = status
        self.controller_ref = None

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