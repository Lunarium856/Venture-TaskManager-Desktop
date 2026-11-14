import SettingsHandler, Themes, AnimationHandler, DummyList
from ProjectClasses import Project, Task, Subtask, Tag, Status, Weight
from CustomWidgets import HoverButton, RoundedScrollBar, SmoothGradientWidget, EditIconButton, DeleteIconButton, ArchiveIconButton, get_resolved_icon_path, tint_pixmap, animate_progress_bar
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys, json, os, time, datetime, calendar, re, sqlite3

dir_script = os.path.dirname(os.path.abspath(__file__))       # client/core
client_dir = os.path.dirname(dir_script)                      # client
data_dir = os.path.join(client_dir, "data")

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

projects_json_path = os.path.join(data_dir, "projects.json")

def load_projects_from_json():
    """Loads projects from projects.json"""
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
                
                raw_status = item.get("status", "NOT_STARTED")
                try:
                    proj_status = Status[raw_status]
                except KeyError:
                    proj_status = Status.NOT_STARTED

                tasks = []
                for tk in item.get("tasks", []):
                    if isinstance(tk, dict):
                        subtasks_data = []
                        for sub in tk.get("subtasks", []):
                            if isinstance(sub, dict):
                                sub_weight = sub.get("weight", "MEDIUM_PRIORITY")
                                if isinstance(sub_weight, int):
                                    try:
                                        sub_weight = Weight(sub_weight)
                                    except ValueError:
                                        sub_weight = Weight.MEDIUM_PRIORITY
                                elif isinstance(sub_weight, str):
                                    try:
                                        sub_weight = Weight[sub_weight]
                                    except KeyError:
                                        sub_weight = Weight.MEDIUM_PRIORITY

                                subtasks_data.append(Subtask(
                                    parentID=sub.get("parentID", tk.get("taskID", item["projectID"])),
                                    subtaskID=sub.get("subtaskID", int(time.time())),
                                    name=sub.get("name", ""),
                                    desc=sub.get("desc", ""),
                                    tags=sub.get("tags", []),
                                    weight=sub_weight,
                                    status=sub.get("status", False)
                                ))
                            else:
                                subtasks_data.append(sub)

                        t_obj = Task(
                            parentID=tk.get("parentID", item["projectID"]),
                            taskID=tk.get("taskID", int(time.time())),
                            name=tk.get("name", ""),
                            desc=tk.get("desc", ""),
                            weight=tk.get("weight", Weight.MEDIUM_PRIORITY),
                            status=tk.get("status", False),
                            tags=tk.get("tags", []),
                            subtasks=subtasks_data,
                            progress=tk.get("progress", 0.0),
                            deadline=tk.get("deadline", "No Deadline")
                        )
                        tasks.append(t_obj)
                    else:
                        tasks.append(tk)

                proj = Project(
                    projectID=item["projectID"],
                    name=item["name"],
                    desc=item["desc"],
                    time_create=item["time_create"],
                    time_elapsed=item.get("time_elapsed", "0d 0h 0m"),
                    last_update=item["last_update"],
                    tasks=tasks,
                    tags=tags,
                    icon=item["icon"],
                    progress=item["progress"],
                    deadline=item["deadline"],
                    status=proj_status
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
        
        tasks_data = []
        for tk in proj.tasks:
            if isinstance(tk, Task):
                weight_val = tk.weight.name if isinstance(tk.weight, Weight) else str(tk.weight)
                
                subtasks_data = []
                for sub in tk.subtasks:
                    if isinstance(sub, Subtask):
                        sub_weight_val = sub.weight.name if isinstance(sub.weight, Weight) else str(sub.weight)
                        subtasks_data.append({
                            "parentID": sub.parentID,
                            "subtaskID": sub.subtaskID,
                            "name": sub.name,
                            "desc": sub.desc,
                            "tags": sub.tags,
                            "weight": sub_weight_val,
                            "status": sub.status
                        })
                    elif isinstance(sub, dict):
                        subtasks_data.append(sub)

                tasks_data.append({
                    "parentID": tk.parentID,
                    "taskID": tk.taskID,
                    "name": tk.name,
                    "desc": tk.desc,
                    "weight": weight_val,
                    "status": tk.status,
                    "tags": tk.tags,
                    "subtasks": subtasks_data,
                    "progress": tk.progress,
                    "deadline": getattr(tk, "deadline", "No Deadline")
                })
            else:
                tasks_data.append(tk)

        raw_data.append({
            "projectID": proj.projectID,
            "name": proj.name,
            "desc": proj.desc,
            "time_create": proj.time_create,
            "time_elapsed": getattr(proj, "time_elapsed", "0d 0h 0m"),
            "last_update": proj.last_update,
            "tasks": tasks_data,
            "tags": tags_data,
            "icon": proj.icon,
            "progress": proj.progress,
            "deadline": proj.deadline,
            "status": proj.status.name if isinstance(proj.status, Status) else "NOT_STARTED",
            "is_archived": getattr(proj, "is_archived", False)
        })
    
    try:
        with open(projects_json_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=4)
    except IOError as e:
        print(f"Error saving projects: {e}")

def parse_deadline_to_readable(deadline_str):
    """Converts ISO or legacy deadline strings into a readable format like 'Feb 15 2027'."""
    if not deadline_str or deadline_str == "No Deadline":
        return "No Deadline"
    try:
        dt = datetime.date.fromisoformat(deadline_str)
        return dt.strftime("%b %d %Y")
    except ValueError:
        pass
    try:
        dt = datetime.datetime.strptime(deadline_str, "%b %d %Y").date()
        return dt.strftime("%b %d %Y")
    except ValueError:
        pass
    try:
        parts = deadline_str.split('/')
        if len(parts) == 3:
            dt = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
            return dt.strftime("%b %d %Y")
    except Exception:
        pass
    return deadline_str


class CreateProjectOverlay(QWidget):
    """Modal overlay for creating projects"""
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

        self.backdrop = QWidget(self)
        self.backdrop.setGeometry(self.rect())
        self.backdrop.setStyleSheet("background-color: rgba(0, 0, 0, 128);")

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

        # Name Field
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

        # Deadline Field
        deadlineLayout = QHBoxLayout()
        deadlineLabel = QLabel("DEADLINE")
        deadlineLabel.setFont(label_font)
        deadlineLabel.setFixedWidth(130)
        deadlineLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")

        deadlineWidget = QWidget()
        deadlineWidget.setStyleSheet("background: transparent; border: none;")
        deadlineComboLayout = QHBoxLayout(deadlineWidget)
        deadlineComboLayout.setContentsMargins(0, 0, 0, 0)
        deadlineComboLayout.setSpacing(10)

        dropdownStyle = (
            f"QComboBox {{"
            f"    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_bg_widgets.hex1}, stop:0.8 {self.theme.core_bg_widgets.hex2});"
            f"    color: {self.theme.core_widgets_gentext}; outline: none;"
            f"    border: 3px solid {self.theme.core_widgets_border}; border-radius: 10px; padding: 5px 10px;"
            f"}}"
            f"QComboBox::drop-down {{"
            f"    subcontrol-origin: padding;"
            f"    subcontrol-position: top right;"
            f"    width: 28px;"
            f"    border-left: 2px solid {self.theme.core_widgets_border};"
            f"    border-top-right-radius: 7px;"
            f"    border-bottom-right-radius: 7px;"
            f"    background: transparent;"
            f"}}"
            f"QComboBox::down-arrow {{"
            f"    image: none;"
            f"    border-left: 5px solid transparent;"
            f"    border-right: 5px solid transparent;"
            f"    border-top: 6px solid {self.theme.core_widgets_gentext};"
            f"    margin-right: 2px;"
            f"}}"
            f"QComboBox QAbstractItemView {{"
            f"    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_bg_widgets.hex1}, stop:0.8 {self.theme.core_bg_widgets.hex2});"
            f"    color: {self.theme.core_widgets_gentext};"
            f"    border: 3px solid {self.theme.core_widgets_border};"
            f"    border-radius: 10px;"
            f"    selection-background-color: {self.theme.core_pos_bg.hex1};"
            f"    selection-color: {self.theme.core_widgets_btntext};"
            f"    outline: none;"
            f"    padding: 4px;"
            f"}}"
            f"QComboBox QAbstractItemView QScrollBar:vertical {{"
            f"    background: {getattr(self.theme, 'scroll_track', '#1a1a1a')};"
            f"    width: 10px;"
            f"    margin: 4px 2px 4px 2px;"
            f"    border-radius: 5px;"
            f"    border: 1px solid {getattr(self.theme, 'scroll_border', '#333333')};"
            f"}}"
            f"QComboBox QAbstractItemView QScrollBar::handle:vertical {{"
            f"    background: {getattr(self.theme, 'scroll_handle', '#4a4a4a')};"
            f"    border-radius: 4px;"
            f"    min-height: 20px;"
            f"}}"
            f"QComboBox QAbstractItemView QScrollBar::handle:vertical:hover {{"
            f"    background: {getattr(self.theme, 'scroll_handle_hover', '#6a6a6a')};"
            f"}}"
            f"QComboBox QAbstractItemView QScrollBar::add-line:vertical, "
            f"QComboBox QAbstractItemView QScrollBar::sub-line:vertical {{"
            f"    height: 0px;"
            f"    background: none;"
            f"}}"
        )

        self.monthDropdown = QComboBox()
        self.monthDropdown.addItems(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        self.monthDropdown.setFont(label_font)
        self.monthDropdown.setStyleSheet(dropdownStyle)

        self.dayDropdown = QComboBox()
        self.dayDropdown.setFont(label_font)
        self.dayDropdown.setStyleSheet(dropdownStyle)

        self.yearDropdown = QComboBox()
        current_year = datetime.date.today().year
        years = [str(y) for y in range(current_year, current_year + 11)]
        self.yearDropdown.addItems(years)
        self.yearDropdown.setFont(label_font)
        self.yearDropdown.setStyleSheet(dropdownStyle)

        deadlineComboLayout.addWidget(self.monthDropdown, 2)
        deadlineComboLayout.addWidget(self.dayDropdown, 1)
        deadlineComboLayout.addWidget(self.yearDropdown, 2)

        deadlineLayout.addWidget(deadlineLabel, alignment=Qt.AlignmentFlag.AlignTop)
        deadlineLayout.addWidget(deadlineWidget, 1)
        dialogLayout.addLayout(deadlineLayout)

        self.monthDropdown.currentIndexChanged.connect(self.updateDaysInMonth)
        self.yearDropdown.currentIndexChanged.connect(self.updateDaysInMonth)
        self.updateDaysInMonth()

        # Description Field
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
            f"border: 3px solid {self.theme.core_widgets_border}; border-radius: 10px; padding: 5px; font-size: 12px; color: {self.theme.core_widgets_gentext};"
        )
        descLayout.addWidget(descLabel, alignment=Qt.AlignmentFlag.AlignTop)
        descLayout.addWidget(self.descInput)
        dialogLayout.addLayout(descLayout)

        iconLayout = QHBoxLayout()
        iconLabel = QLabel("ICON")
        iconLabel.setFont(label_font)
        iconLabel.setFixedWidth(130)
        iconLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")
        self.iconInput = QComboBox()
        self.iconInput.addItems([
            "Shirt",
            "Shoes",
            "Phone"
        ])
        self.iconInput.setFont(label_font)
        self.iconInput.setStyleSheet(dropdownStyle)
        iconLayout.addWidget(iconLabel)
        iconLayout.addWidget(self.iconInput)
        dialogLayout.addLayout(iconLayout)
        dialogLayout.addStretch()

        # Action Buttons
        bottomBtnLayout = QHBoxLayout()
        bottomBtnLayout.setSpacing(20)

        self.btnCreate = HoverButton("CREATE", parent=self.dialogBox, animator=self.animator)
        self.btnCreate.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.btnCreate.setFixedHeight(40)
        self.btnCreate.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_pos_bg.hex1}, stop:0.8 {self.theme.core_pos_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_pos_border}; border-radius: 18px;"
        )
        self.btnCreate.setHoverData(["border"], [self.theme.core_pos_border], [self.theme.core_pos_border_hover])
        self.btnCreate.clicked.connect(self.acceptOverlay)

        self.btnCancel = HoverButton("CANCEL", parent=self.dialogBox, animator=self.animator)
        self.btnCancel.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.btnCancel.setFixedHeight(40)
        self.btnCancel.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_neg_bg.hex1}, stop:0.8 {self.theme.core_neg_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_neg_border}; border-radius: 18px;"
        )
        self.btnCancel.setHoverData(["border"], [self.theme.core_neg_border], [self.theme.core_neg_border_hover])
        self.btnCancel.clicked.connect(self.rejectOverlay)

        bottomBtnLayout.addWidget(self.btnCreate)
        bottomBtnLayout.addWidget(self.btnCancel)
        dialogLayout.addLayout(bottomBtnLayout)

        self.show()
        self.fadeInAnim = self.animator.createAnimation(self, "opacity", 0.0, 1.0, duration=300)
        if self.fadeInAnim:
            self.fadeInAnim.start()

    def updateDaysInMonth(self):
        """Sanitizes day options based on selected month and year (including leap years)."""
        try:
            month_idx = self.monthDropdown.currentIndex() + 1
            year = int(self.yearDropdown.currentText())
            _, num_days = calendar.monthrange(year, month_idx)
            
            current_day = self.dayDropdown.currentText()
            self.dayDropdown.blockSignals(True)
            self.dayDropdown.clear()
            day_items = [str(d) for d in range(1, num_days + 1)]
            self.dayDropdown.addItems(day_items)
            
            if current_day in day_items:
                self.dayDropdown.setCurrentText(current_day)
            else:
                self.dayDropdown.setCurrentIndex(min(len(day_items) - 1, int(current_day) - 1 if current_day.isdigit() else 0))
            self.dayDropdown.blockSignals(False)
        except Exception:
            pass

    def set_initial_date(self, deadline_str):
        """Sets combo boxes based on an existing deadline string."""
        if not deadline_str:
            return
        dt = None
        try:
            dt = datetime.date.fromisoformat(deadline_str)
        except ValueError:
            pass
        if not dt:
            try:
                dt = datetime.datetime.strptime(deadline_str, "%b %d %Y").date()
            except ValueError:
                pass
        if not dt:
            try:
                parts = deadline_str.split('/')
                if len(parts) == 3:
                    dt = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
            except Exception:
                pass

        if dt:
            month_abbr = dt.strftime("%b")
            day_str = str(dt.day)
            year_str = str(dt.year)

            idx = self.monthDropdown.findText(month_abbr)
            if idx >= 0:
                self.monthDropdown.setCurrentIndex(idx)
            idx = self.yearDropdown.findText(year_str)
            if idx >= 0:
                self.yearDropdown.setCurrentIndex(idx)
            
            self.updateDaysInMonth()
            
            idx = self.dayDropdown.findText(day_str)
            if idx >= 0:
                self.dayDropdown.setCurrentIndex(idx)

    def get_deadline_values(self):
        """Converts dropdown values into readable string, ISO format, and date object."""
        month_str = self.monthDropdown.currentText()
        day_str = self.dayDropdown.currentText()
        year_str = self.yearDropdown.currentText()
        
        month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, 
                     "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
        month_num = month_map.get(month_str, 1)
        day_num = int(day_str) if day_str.isdigit() else 1
        year_num = int(year_str) if year_str.isdigit() else datetime.date.today().year

        try:
            dt_obj = datetime.date(year_num, month_num, day_num)
            readable_deadline = dt_obj.strftime("%b %d %Y")
            iso_deadline = dt_obj.isoformat()
        except ValueError:
            dt_obj = datetime.date.today()
            readable_deadline = dt_obj.strftime("%b %d %Y")
            iso_deadline = dt_obj.isoformat()

        return readable_deadline, iso_deadline, dt_obj

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
        readable_deadline, iso_deadline, dt_obj = self.get_deadline_values()

        if dt_obj < datetime.date.today():
            QMessageBox.warning(self, "Invalid Deadline", "The deadline cannot be set to a date before the current date.")
            return

        deadline = iso_deadline
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


class EditProjectOverlay(CreateProjectOverlay):
    """Modal for editing project name, deadline, and description"""
    def __init__(self, parent=None, animator=None, activeFont=None, project_instance=None, on_save_callback=None, controller=None):
        self.project_instance = project_instance
        self.on_save_callback = on_save_callback
        super().__init__(parent=parent, animator=animator, activeFont=activeFont, on_create_callback=None, controller=controller)
        
        if self.project_instance:
            self.nameInput.setText(self.project_instance.name)
            self.descInput.setPlainText(self.project_instance.desc)
            if hasattr(self.project_instance, 'deadline') and self.project_instance.deadline:
                self.set_initial_date(self.project_instance.deadline)
        self.btnCreate.setText("SAVE")

    def acceptOverlay(self):
        if self.is_submitting:
            return
        name = self.nameInput.text().strip()
        readable_deadline, iso_deadline, dt_obj = self.get_deadline_values()

        if dt_obj < datetime.date.today():
            QMessageBox.warning(self, "Invalid Deadline", "The deadline cannot be set to a date before the current date.")
            return

        deadline = iso_deadline
        desc = self.descInput.toPlainText().strip()
        if name and self.on_save_callback:
            self.is_submitting = True
            self.on_save_callback(name, deadline, desc)
            QTimer.singleShot(250, lambda: setattr(self, 'is_submitting', False))
        self.closeOverlay()


class CreateTaskOverlay(QWidget):
    """Modal overlay for creating a new task with name, priority, and dropdown deadline fields"""
    def __init__(self, parent=None, animator=None, activeFont=None, title="CREATE TASK", on_create_callback=None, controller=None):
        super().__init__(parent)
        self.animator = animator
        self.activeFont = activeFont if activeFont else "Arial"
        self.on_create_callback = on_create_callback
        self.controller = controller
        self.theme = controller.current_theme if controller and hasattr(controller, 'current_theme') else Themes.THEME_DEFAULT

        self.is_submitting = False
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(0.0)

        if self.parent():
            self.setGeometry(self.parent().rect())
            self.parent().installEventFilter(self)

        self.backdrop = QWidget(self)
        self.backdrop.setGeometry(self.rect())
        self.backdrop.setStyleSheet("background-color: rgba(0, 0, 0, 128);")

        self.dialogBox = QWidget(self)
        self.dialogBox.setFixedSize(560, 400)
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

        # Modal Title
        titleLabel = QLabel(title)
        titleLabel.setFont(QFont(self.activeFont, 16, QFont.Weight.Bold))
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titleLabel.setStyleSheet(f"color: {self.theme.core_pos_bg.hex2}; border: none; background: transparent;")
        dialogLayout.addWidget(titleLabel)

        # Name Field
        nameLayout = QHBoxLayout()
        nameLabel = QLabel("TASK NAME")
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

        # Deadline Field
        deadlineLayout = QHBoxLayout()
        deadlineLabel = QLabel("DEADLINE")
        deadlineLabel.setFont(label_font)
        deadlineLabel.setFixedWidth(130)
        deadlineLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")

        deadlineWidget = QWidget()
        deadlineWidget.setStyleSheet("background: transparent; border: none;")
        deadlineComboLayout = QHBoxLayout(deadlineWidget)
        deadlineComboLayout.setContentsMargins(0, 0, 0, 0)
        deadlineComboLayout.setSpacing(10)

        dropdownStyle = (
            f"QComboBox {{"
            f"    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_bg_widgets.hex1}, stop:0.8 {self.theme.core_bg_widgets.hex2});"
            f"    color: {self.theme.core_widgets_gentext}; outline: none;"
            f"    border: 3px solid {self.theme.core_widgets_border}; border-radius: 10px; padding: 5px 10px;"
            f"}}"
            f"QComboBox::drop-down {{"
            f"    subcontrol-origin: padding;"
            f"    subcontrol-position: top right;"
            f"    width: 28px;"
            f"    border-left: 2px solid {self.theme.core_widgets_border};"
            f"    border-top-right-radius: 7px;"
            f"    border-bottom-right-radius: 7px;"
            f"    background: transparent;"
            f"}}"
            f"QComboBox::down-arrow {{"
            f"    image: none;"
            f"    border-left: 5px solid transparent;"
            f"    border-right: 5px solid transparent;"
            f"    border-top: 6px solid {self.theme.core_widgets_gentext};"
            f"    margin-right: 2px;"
            f"}}"
            f"QComboBox QAbstractItemView {{"
            f"    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_bg_widgets.hex1}, stop:0.8 {self.theme.core_bg_widgets.hex2});"
            f"    color: {self.theme.core_widgets_gentext};"
            f"    border: 3px solid {self.theme.core_widgets_border};"
            f"    border-radius: 10px;"
            f"    selection-background-color: {self.theme.core_pos_bg.hex1};"
            f"    selection-color: {self.theme.core_widgets_btntext};"
            f"    outline: none;"
            f"    padding: 4px;"
            f"}}"
            f"QComboBox QAbstractItemView QScrollBar:vertical {{"
            f"    background: {getattr(self.theme, 'scroll_track', '#1a1a1a')};"
            f"    width: 10px;"
            f"    margin: 4px 2px 4px 2px;"
            f"    border-radius: 5px;"
            f"    border: 1px solid {getattr(self.theme, 'scroll_border', '#333333')};"
            f"}}"
            f"QComboBox QAbstractItemView QScrollBar::handle:vertical {{"
            f"    background: {getattr(self.theme, 'scroll_handle', '#4a4a4a')};"
            f"    border-radius: 4px;"
            f"    min-height: 20px;"
            f"}}"
            f"QComboBox QAbstractItemView QScrollBar::handle:vertical:hover {{"
            f"    background: {getattr(self.theme, 'scroll_handle_hover', '#6a6a6a')};"
            f"}}"
            f"QComboBox QAbstractItemView QScrollBar::add-line:vertical, "
            f"QComboBox QAbstractItemView QScrollBar::sub-line:vertical {{"
            f"    height: 0px;"
            f"    background: none;"
            f"}}"
        )

        self.monthDropdown = QComboBox()
        self.monthDropdown.addItems(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        self.monthDropdown.setFont(label_font)
        self.monthDropdown.setStyleSheet(dropdownStyle)

        self.dayDropdown = QComboBox()
        self.dayDropdown.setFont(label_font)
        self.dayDropdown.setStyleSheet(dropdownStyle)

        self.yearDropdown = QComboBox()
        current_year = datetime.date.today().year
        years = [str(y) for y in range(current_year, current_year + 11)]
        self.yearDropdown.addItems(years)
        self.yearDropdown.setFont(label_font)
        self.yearDropdown.setStyleSheet(dropdownStyle)

        deadlineComboLayout.addWidget(self.monthDropdown, 2)
        deadlineComboLayout.addWidget(self.dayDropdown, 1)
        deadlineComboLayout.addWidget(self.yearDropdown, 2)

        deadlineLayout.addWidget(deadlineLabel, alignment=Qt.AlignmentFlag.AlignTop)
        deadlineLayout.addWidget(deadlineWidget, 1)
        dialogLayout.addLayout(deadlineLayout)

        self.monthDropdown.currentIndexChanged.connect(self.updateDaysInMonth)
        self.yearDropdown.currentIndexChanged.connect(self.updateDaysInMonth)
        self.updateDaysInMonth()

        # Priority Field
        weightLayout = QHBoxLayout()
        weightLabel = QLabel("PRIORITY")
        weightLabel.setFont(label_font)
        weightLabel.setFixedWidth(130)
        weightLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")
        self.weightInput = QComboBox()
        self.weightInput.addItems(["LOW", "MEDIUM", "HIGH"])
        self.weightInput.setFont(label_font)
        self.weightInput.setStyleSheet(dropdownStyle)
        weightLayout.addWidget(weightLabel)
        weightLayout.addWidget(self.weightInput)
        dialogLayout.addLayout(weightLayout)
        dialogLayout.addStretch()

        # Action Buttons
        bottomBtnLayout = QHBoxLayout()
        bottomBtnLayout.setSpacing(20)
        
        self.btnCreate = HoverButton("CREATE", parent=self.dialogBox, animator=self.animator)
        self.btnCreate.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.btnCreate.setFixedHeight(40)
        self.btnCreate.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_pos_bg.hex1}, stop:0.8 {self.theme.core_pos_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_pos_border}; border-radius: 18px;"
        )
        self.btnCreate.setHoverData(["border"], [self.theme.core_pos_border], [self.theme.core_pos_border_hover])
        self.btnCreate.clicked.connect(self.acceptOverlay)

        self.btnCancel = HoverButton("CANCEL", parent=self.dialogBox, animator=self.animator)
        self.btnCancel.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.btnCancel.setFixedHeight(40)
        self.btnCancel.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_neg_bg.hex1}, stop:0.8 {self.theme.core_neg_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_neg_border}; border-radius: 18px;"
        )
        self.btnCancel.setHoverData(["border"], [self.theme.core_neg_border], [self.theme.core_neg_border_hover])
        self.btnCancel.clicked.connect(self.rejectOverlay)

        bottomBtnLayout.addWidget(self.btnCreate)
        bottomBtnLayout.addWidget(self.btnCancel)
        dialogLayout.addLayout(bottomBtnLayout)

        self.show()
        self.fadeInAnim = self.animator.createAnimation(self, "opacity", 0.0, 1.0, duration=300)
        if self.fadeInAnim:
            self.fadeInAnim.start()

    def updateDaysInMonth(self):
        try:
            month_idx = self.monthDropdown.currentIndex() + 1
            year = int(self.yearDropdown.currentText())
            _, num_days = calendar.monthrange(year, month_idx)
            
            current_day = self.dayDropdown.currentText()
            self.dayDropdown.blockSignals(True)
            self.dayDropdown.clear()
            day_items = [str(d) for d in range(1, num_days + 1)]
            self.dayDropdown.addItems(day_items)
            
            if current_day in day_items:
                self.dayDropdown.setCurrentText(current_day)
            else:
                self.dayDropdown.setCurrentIndex(min(len(day_items) - 1, int(current_day) - 1 if current_day.isdigit() else 0))
            self.dayDropdown.blockSignals(False)
        except Exception:
            pass

    def set_initial_date(self, deadline_str):
        if not deadline_str or deadline_str == "No Deadline":
            return
        dt = None
        try:
            dt = datetime.date.fromisoformat(deadline_str)
        except ValueError:
            pass
        if not dt:
            try:
                dt = datetime.datetime.strptime(deadline_str, "%b %d %Y").date()
            except ValueError:
                pass
        if not dt:
            try:
                parts = deadline_str.split('/')
                if len(parts) == 3:
                    dt = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
            except Exception:
                pass

        if dt:
            month_abbr = dt.strftime("%b")
            day_str = str(dt.day)
            year_str = str(dt.year)

            idx = self.monthDropdown.findText(month_abbr)
            if idx >= 0:
                self.monthDropdown.setCurrentIndex(idx)
            idx = self.yearDropdown.findText(year_str)
            if idx >= 0:
                self.yearDropdown.setCurrentIndex(idx)
            
            self.updateDaysInMonth()
            
            idx = self.dayDropdown.findText(day_str)
            if idx >= 0:
                self.dayDropdown.setCurrentIndex(idx)

    def get_deadline_values(self):
        month_str = self.monthDropdown.currentText()
        day_str = self.dayDropdown.currentText()
        year_str = self.yearDropdown.currentText()
        
        month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, 
                     "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
        month_num = month_map.get(month_str, 1)
        day_num = int(day_str) if day_str.isdigit() else 1
        year_num = int(year_str) if year_str.isdigit() else datetime.date.today().year

        try:
            dt_obj = datetime.date(year_num, month_num, day_num)
            readable_deadline = dt_obj.strftime("%b %d %Y")
            iso_deadline = dt_obj.isoformat()
        except ValueError:
            dt_obj = datetime.date.today()
            readable_deadline = dt_obj.strftime("%b %d %Y")
            iso_deadline = dt_obj.isoformat()

        return readable_deadline, iso_deadline, dt_obj

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
        readable_deadline, iso_deadline, dt_obj = self.get_deadline_values()

        if dt_obj < datetime.date.today():
            QMessageBox.warning(self, "Invalid Deadline", "The deadline cannot be set to a date before the current date.")
            return

        deadline = iso_deadline
        weight_str = self.weightInput.currentText()
        try:
            weight = Weight[weight_str]
        except KeyError:
            weight = Weight.MEDIUM_PRIORITY

        if name and self.on_create_callback:
            self.is_submitting = True
            self.on_create_callback(name, deadline, weight)
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


class EditTaskOverlay(CreateTaskOverlay):
    """Modal for editing task name, deadline, and priority"""
    def __init__(self, parent=None, animator=None, activeFont=None, title="EDIT TASK", task_instance=None, on_save_callback=None, controller=None):
        self.task_instance = task_instance
        self.on_save_callback = on_save_callback
        super().__init__(parent=parent, animator=animator, activeFont=activeFont, title=title, on_create_callback=None, controller=controller)
        
        if self.task_instance:
            self.nameInput.setText(self.task_instance.name)
            if hasattr(self.task_instance, 'deadline') and self.task_instance.deadline:
                self.set_initial_date(self.task_instance.deadline)
            if hasattr(self.task_instance, 'weight') and isinstance(self.task_instance.weight, Weight):
                index = self.weightInput.findText(self.task_instance.weight.name)
                if index >= 0:
                    self.weightInput.setCurrentIndex(index)
        self.btnCreate.setText("SAVE")

    def acceptOverlay(self):
        if self.is_submitting:
            return
        name = self.nameInput.text().strip()
        readable_deadline, iso_deadline, dt_obj = self.get_deadline_values()

        if dt_obj < datetime.date.today():
            QMessageBox.warning(self, "Invalid Deadline", "The deadline cannot be set to a date before the current date.")
            return

        deadline = iso_deadline
        weight_str = self.weightInput.currentText()
        try:
            weight = Weight[weight_str]
        except KeyError:
            weight = Weight.MEDIUM_PRIORITY

        if name and self.on_save_callback:
            self.is_submitting = True
            self.on_save_callback(name, deadline, weight)
            QTimer.singleShot(250, lambda: setattr(self, 'is_submitting', False))
        self.closeOverlay()


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

        self.backdrop = QWidget(self)
        self.backdrop.setGeometry(self.rect())
        self.backdrop.setStyleSheet("background-color: rgba(0, 0, 0, 128);")

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

        titleLabel = QLabel(title)
        titleLabel.setFont(label_font)
        titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titleLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")
        dialogLayout.addWidget(titleLabel)

        msgLabel = QLabel(message)
        msgLabel.setFont(QFont(self.activeFont, 11, QFont.Weight.Normal))
        msgLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msgLabel.setWordWrap(True)
        msgLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")
        dialogLayout.addWidget(msgLabel, 1)

        bottomBtnLayout = QHBoxLayout()
        bottomBtnLayout.setSpacing(20)
        
        self.btnConfirm = HoverButton("CONFIRM", parent=self.dialogBox, animator=self.animator)
        self.btnConfirm.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.btnConfirm.setFixedHeight(40)
        self.btnConfirm.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_neg_bg.hex1}, stop:0.8 {self.theme.core_neg_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_neg_border}; border-radius: 18px;"
        )
        self.btnConfirm.setHoverData(["border"], [self.theme.core_neg_border], [self.theme.core_neg_border_hover])
        self.btnConfirm.clicked.connect(self.acceptOverlay)

        self.btnCancel = HoverButton("CANCEL", parent=self.dialogBox, animator=self.animator)
        self.btnCancel.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.btnCancel.setFixedHeight(40)
        self.btnCancel.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_neutral_bg.hex1}, stop:0.8 {self.theme.core_neutral_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_neutral_border}; border-radius: 18px;"
        )
        self.btnCancel.setHoverData(["border"], [self.theme.core_neutral_border], [self.theme.core_neutral_border_hover])
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
    """Detailed view for a specific project"""
    def __init__(self, controller, project):
        super().__init__()
        self.controller = controller
        self.project = project
        self.activeFont = self.controller.activeJetFamFont
        self.theme = self.controller.current_theme

        self.viewContainer = SmoothGradientWidget(
            self.theme.core_bg_main.hex1,
            self.theme.core_bg_main.hex2,
            border_colour="black",
            border_width=4,
            parent=self
        )

        self.isCompleted = True if self.project.status.value == 3 else False

        baseLayout = QVBoxLayout(self)
        baseLayout.setContentsMargins(0, 0, 0, 0)
        baseLayout.addWidget(self.viewContainer)
        
        pageLayout = QVBoxLayout(self.viewContainer)
        pageLayout.setContentsMargins(30, 30, 30, 30)
        pageLayout.setSpacing(20)

        headerWidget = QWidget()
        headerWidget.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {self.theme.core_tertiary_bg.hex1}, stop:1 {self.theme.core_tertiary_bg.hex2});"
            f"border: 3px solid {self.theme.core_widgets_border}; border-radius: 15px;"
        )
        headerLayout = QVBoxLayout(headerWidget)
        headerLayout.setContentsMargins(20, 20, 20, 20)

        headerDetailsLayout = QHBoxLayout()
        headerDetailsLayout.setSpacing(15)

        headerIcon = QLabel(headerWidget)
        icon_to_resolve = project.icon if project.icon else "icon_settings_anim.png"
        resolved_icon = get_resolved_icon_path(icon_to_resolve) if isinstance(icon_to_resolve, str) else ""
        
        if resolved_icon and os.path.exists(resolved_icon):
            pixmap = QPixmap(resolved_icon)
            if not pixmap.isNull():
                scaledPM = pixmap.scaled(QSize(64,64), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                tintedPM = tint_pixmap(scaledPM, QColor(self.theme.project_text))
                headerIcon.setPixmap(tintedPM)
        elif isinstance(self.project.icon, QIcon):
            pixmap = self.project.icon.pixmap(QSize(64,64))
            if not pixmap.isNull():
                tintedPM = tint_pixmap(pixmap, QColor(self.theme.project_text))
                headerIcon.setPixmap(tintedPM)
        headerIcon.setStyleSheet("background: transparent; border: none;")

        # Name, Description, & Deadline
        textColLayout = QVBoxLayout()
        textColLayout.setSpacing(8)
        
        self.titleLbl = QLabel(self.project.name)
        self.titleLbl.setFont(QFont(self.activeFont, 22, QFont.Weight.Bold))
        self.titleLbl.setStyleSheet(f"color: {self.theme.sidebar_activebtn}; border: none; background: transparent;")
        
        self.descLbl = QLabel(self.project.desc)
        self.descLbl.setFont(QFont(self.activeFont, 12, QFont.Weight.Light))
        self.descLbl.setWordWrap(True)
        self.descLbl.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")

        deadline_str = getattr(self.project, 'deadline', "No Deadline")
        readable_deadline = parse_deadline_to_readable(deadline_str)
        self.deadlineLabel = QLabel(f"Deadline: {readable_deadline}")
        self.deadlineLabel.setFont(QFont(self.activeFont, 10, QFont.Weight.Bold))
        self.deadlineLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; background: transparent; border: none;")
        
        textColLayout.addWidget(self.titleLbl)
        textColLayout.addWidget(self.descLbl)
        textColLayout.addWidget(self.deadlineLabel)
        headerDetailsLayout.addWidget(headerIcon)
        headerDetailsLayout.addLayout(textColLayout, 1)

        # Edit & Delete Buttons
        headerBtnLayout = QVBoxLayout()
        headerBtnLayout.setSpacing(8)

        btnEdit = EditIconButton(parent=headerWidget, animator=self.controller.animator)
        btnEdit.setFixedSize(36, 36)
        btnEdit.clicked.connect(self.editProjectPrompt)

        btnDelete = DeleteIconButton(parent=headerWidget, animator=self.controller.animator)
        btnDelete.setFixedSize(36, 36)
        btnDelete.clicked.connect(self.deleteProjectPrompt)

        btnArchive = ArchiveIconButton(parent=headerWidget, animator=self.controller.animator)
        btnArchive.setFixedSize(36, 36)
        btnArchive.clicked.connect(self.archiveProjectPrompt)

        headerBtnLayout.addWidget(btnEdit)
        headerBtnLayout.addWidget(btnArchive)
        headerBtnLayout.addWidget(btnDelete)
        headerDetailsLayout.addLayout(headerBtnLayout)
        headerLayout.addLayout(headerDetailsLayout)
        pageLayout.addWidget(headerWidget)

        # Progress Details
        progDetails = QHBoxLayout()
        progDetails.setSpacing(15)
        
        percentValue = int(getattr(self.project, 'progress', 0.0))
        self.headerPercentLabel = QLabel(f"{percentValue}%")
        self.headerPercentLabel.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.headerPercentLabel.setFixedWidth(64)
        self.headerPercentLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.headerPercentLabel.setStyleSheet(
            f"color: {self.theme.project_text if percentValue < 100 else self.theme.core_pos_bg.hex2};"
            "background: transparent; border: none;"
        )

        self.headerProgBar = QProgressBar()
        self.headerProgBar.setRange(0, 100)
        self.headerProgBar.setValue(0)
        animate_progress_bar(self.headerProgBar, percentValue, duration=400)
        self.headerProgBar.setTextVisible(False)
        self.headerProgBar.setFixedHeight(10)
        self.headerProgBar.setStyleSheet(
            "QProgressBar {"
            f"border: 2px solid {self.theme.core_widgets_border}; border-radius: 4px; background-color: {self.theme.core_widgets_border};"
            "}"
            "QProgressBar::chunk {"
            f"background: qlineargradient(x1:0, y:0.5, x2:1, y2:0.5, stop:0.2 {self.theme.project_progress.hex1}, stop:0.9 {self.theme.project_progress.hex2});"
            "   border-radius: 2px; }"
        )
        
        progDetails.addWidget(self.headerPercentLabel)
        progDetails.addWidget(self.headerProgBar)
        headerLayout.addLayout(progDetails)

        # Project Tasks Label & Button
        tasksHeaderRow = QHBoxLayout()
        tasksHeader = QLabel("PROJECT TASKS")
        tasksHeader.setFont(QFont(self.activeFont, 16, QFont.Weight.Bold))
        tasksHeader.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; background: transparent; border: none;")
        tasksHeaderRow.addWidget(tasksHeader)

        # New Task Button
        if not self.isCompleted:
            btn_newTask = HoverButton("ADD TASK", parent=self, animator=self.controller.animator)
            btn_newTask.setObjectName("createNewTask")
            btn_newTask.setFont(QFont(self.activeFont, 14, QFont.Weight.Bold))
            btn_newTask.setStyleSheet(
                f"color: {self.theme.core_widgets_btntext};"
                f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {self.theme.core_pos_bg.hex1}, stop:1 {self.theme.core_pos_bg.hex2});"
                f"border: 2px solid {self.theme.core_pos_border}; border-radius: 12px;"
                "padding: 6px;"
            )
            btn_newTask.setHoverData(["border"], [self.theme.core_pos_border], [self.theme.core_pos_border_hover])
            btn_newTask.clicked.connect(self.createNewTask)
            tasksHeaderRow.addWidget(btn_newTask)
        tasksHeaderRow.addStretch()
        pageLayout.addLayout(tasksHeaderRow)

        # Task List Container with custom styling & custom scrollbar inside darkened box
        tasksContainerWidget = QWidget(self)
        tasksContainerWidget.setStyleSheet(
            f"background-color: {self.theme.core_bg_lists if self.theme.core_bg_lists else 'rgba(10, 10, 10, 0.5)'};"
            f"border: none; border-radius: 20px;"
        )
        tasksContainerLayout = QHBoxLayout(tasksContainerWidget)
        tasksContainerLayout.setContentsMargins(8, 8, 8, 8)
        tasksContainerLayout.setSpacing(4)

        self.scroll = QScrollArea(tasksContainerWidget)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.contentWidget = QWidget()
        self.contentWidget.setStyleSheet("background: transparent; border: none;")
        self.contentLayout = QVBoxLayout(self.contentWidget)
        self.contentLayout.setSpacing(12)
        self.contentLayout.setContentsMargins(10, 10, 10, 10)

        self.populateTasksList()

        self.scroll.setWidget(self.contentWidget)
        
        v_bar = RoundedScrollBar(Qt.Orientation.Vertical, self.scroll, controller=self.controller)
        v_bar.setFixedWidth(16)
        self.scroll.setVerticalScrollBar(v_bar)

        tasksContainerLayout.addWidget(self.scroll)
        tasksContainerLayout.addWidget(v_bar)
        pageLayout.addWidget(tasksContainerWidget, 1)

        # Project Actions (Bottom Button Row)
        projectActionsContainer = QWidget(self)
        projectActionsContainer.setStyleSheet("background: transparent; border: none;")
        projectActionsLayout = QHBoxLayout(projectActionsContainer)
        pageLayout.addWidget(projectActionsContainer)

        # Project Action Buttons
        self.btnBack = HoverButton("BACK TO PROJECTS", parent=self, animator=self.controller.animator)
        self.btnBack.setObjectName("backToList")
        self.btnBack.setFont(QFont(self.activeFont, 14, QFont.Weight.Bold))
        self.btnBack.setFixedHeight(45)
        self.btnBack.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_pos_bg.hex1}, stop:1 {self.theme.core_pos_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext};"
            f"border: 3px solid {self.theme.core_pos_border}; border-radius: 18px;"
            f"outline: none;"
        )
        self.btnBack.setHoverData(["border"], [self.theme.core_neutral_border], [self.theme.core_neutral_border_hover])
        self.btnBack.clicked.connect(self.controller.returnToProjects)
        projectActionsLayout.addWidget(self.btnBack)

    def populateTasksList(self):
        """Fills the Tasks list with data pulled from projects.json"""
        while self.contentLayout.count():
            item = self.contentLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tasks_list = getattr(self.project, 'tasks', [])
        if not tasks_list:
            noTasksLbl = QLabel("Project completed, somehow with no tasks..." if self.isCompleted else "Click 'ADD TASK' to add a Task. \n Doing so will mark the project as 'In Progress'.")
            noTasksLbl.setFont(QFont(self.activeFont, 16, QFont.Weight.Bold))
            noTasksLbl.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; background: transparent; border: none;")
            noTasksLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.contentLayout.addStretch()
            self.contentLayout.addWidget(noTasksLbl)
            self.contentLayout.addStretch()
        else:
            for t in tasks_list:
                if isinstance(t, dict):
                    t_obj = Task(
                        parentID=t.get("parentID", self.project.projectID),
                        taskID=t.get("taskID", int(time.time())),
                        name=t.get("name", ""),
                        desc=t.get("desc", ""),
                        weight=t.get("weight", Weight.MEDIUM_PRIORITY),
                        status=t.get("status", False),
                        tags=t.get("tags", []),
                        subtasks=t.get("subtasks", []),
                        progress=t.get("progress", 0.0),
                        deadline=t.get("deadline", "No Deadline")
                    )
                else:
                    t_obj = t

                t_obj.controller_ref = self.controller
                t_obj.project_ref = self.project
                
                task_widget = t_obj.newDisplayWidget(self.contentWidget, on_update_callback=self.saveAndRefreshTasks)
                self.contentLayout.addWidget(task_widget)

    def createNewTask(self):
        self.controller.is_modal_active = True
        CreateTaskOverlay(
            parent=self.controller.stackedWidget,
            animator=self.controller.animator,
            activeFont=self.activeFont,
            title="CREATE NEW TASK",
            on_create_callback=self.onNewTaskCreated,
            controller=self.controller
        )

    def onNewTaskCreated(self, task_name, task_deadline, task_weight=Weight.MEDIUM_PRIORITY):
        new_task = Task(
            parentID=self.project.projectID,
            taskID=int(time.time()),
            name=task_name,
            desc="",
            weight=task_weight,
            status=False,
            tags=[],
            subtasks=[],
            progress=0.0,
            deadline=task_deadline if task_deadline else "No Deadline"
        )
        new_task.controller_ref = self.controller
        new_task.project_ref = self.project

        if not hasattr(self.project, 'tasks') or self.project.tasks is None:
            self.project.tasks = []
        self.project.tasks.append(new_task)

        self.saveAndRefreshTasks(refresh_list=True)

    def saveAndRefreshTasks(self, refresh_list=False):
        """Saves Tasks data to projects.json & refreshes UI to reflect changes"""
        # Recalculate progress
        for t in self.project.tasks:
            if hasattr(t, 'subtasks') and t.subtasks:
                t.recalculate_task_progress()
        self.project.recalculate_progress()

        # Update header progress bar and label
        new_progress_int = int(self.project.progress)
        if hasattr(self, 'headerProgBar') and self.headerProgBar:
            animate_progress_bar(self.headerProgBar, new_progress_int, duration=300)

        if hasattr(self, 'headerPercentLabel') and self.headerPercentLabel:
            self.headerPercentLabel.setText(f"{new_progress_int}%")
            target_col = self.theme.core_pos_bg.hex2 if new_progress_int >= 100 else self.theme.core_widgets_gentext
            if self.controller.animator and new_progress_int >= 100:
                txt_anim = self.controller.animator.createAnimation(
                    self.headerPercentLabel, "text", 
                    self.theme.core_widgets_gentext, 
                    self.theme.core_pos_bg.hex2, 
                    duration=300
                )
                if txt_anim:
                    txt_anim.start()
                    self._header_txt_anim = txt_anim
            self.headerPercentLabel.setStyleSheet(f"color: {target_col}; background: transparent; border: none;")

        all_projects = load_projects_from_json()
        for p in all_projects:
            if p.projectID == self.project.projectID:
                p.tasks = self.project.tasks
                p.progress = self.project.progress
                p.status = self.project.status
                break
        save_projects_to_json(all_projects)

        if refresh_list:
            self.populateTasksList()
        else:
            # Update existing task widgets in place
            for i in range(self.contentLayout.count()):
                item = self.contentLayout.itemAt(i)
                if item and item.widget():
                    w = item.widget()
                    if hasattr(w, 'update_subtask_progress_ui'):
                        w.update_subtask_progress_ui()

    def editProjectPrompt(self):
        self.controller.is_modal_active = True
        EditProjectOverlay(
            parent=self.controller.stackedWidget,
            animator=self.controller.animator,
            activeFont=self.activeFont,
            project_instance=self.project,
            on_save_callback=self.onProjectEdited,
            controller=self.controller
        )

    def onProjectEdited(self, name, deadline, desc):
        self.project.name = name
        self.project.deadline = deadline
        self.project.desc = desc
        self.project.last_update = datetime.datetime.now().isoformat()

        all_projects = load_projects_from_json()
        for p in all_projects:
            if p.projectID == self.project.projectID:
                p.name = name
                p.deadline = deadline
                p.desc = desc
                p.last_update = self.project.last_update
                break
        save_projects_to_json(all_projects)

        self.titleLbl.setText(name)
        self.descLbl.setText(desc)
        
        readable_deadline = parse_deadline_to_readable(deadline)
        self.deadlineLabel.setText(f"Deadline: {readable_deadline}")

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
    """Main Project Listing View"""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.settingsFunctions = self.controller.settingsFunctions
        self.animator = self.controller.animator
        self.activeJetFamFont = self.controller.activeJetFamFont
        self.theme = self.controller.current_theme
        
        self.saved_projects = [p for p in load_projects_from_json() if not getattr(p, 'is_archived', False)]

        self.viewContainer = SmoothGradientWidget(
            self.theme.core_bg_main.hex1,
            self.theme.core_bg_main.hex2,
            border_colour="black",
            border_width=4,
            parent=self
        )

        baseLayout = QVBoxLayout(self)
        baseLayout.setContentsMargins(0, 0, 0, 0)
        baseLayout.addWidget(self.viewContainer)

        self.mainContentLayout = QVBoxLayout(self.viewContainer)
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
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_pos_border}; outline: none; border-radius: 18px; text-align: center;"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_pos_bg.hex1}, stop:1 {self.theme.core_pos_bg.hex2});"
        )
        self.main_button_newProject.clicked.connect(self.createProject)
        self.main_button_newProject.setHoverData(["border"], [self.theme.core_pos_border], [self.theme.core_pos_border_hover])

        self.btnTags = HoverButton("TAGS", self, self.animator)
        self.btnTags.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btnTags.setFont(QFont(self.activeJetFamFont, 16, QFont.Weight.Bold))
        self.btnTags.setFixedHeight(45); self.btnTags.setFixedWidth(130)
        self.btnTags.setStyleSheet(
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_pos_border}; outline: none; border-radius: 18px; text-align: center;"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_pos_bg.hex1}, stop:1 {self.theme.core_pos_bg.hex2});"
        )
        self.btnTags.setHoverData(["border"], [self.theme.core_pos_border], [self.theme.core_pos_border_hover])

        self.btnArchived = HoverButton("ARCHIVED", self, self.animator)
        self.btnArchived.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btnArchived.setFont(QFont(self.activeJetFamFont, 16, QFont.Weight.Bold))
        self.btnArchived.setFixedHeight(45); self.btnArchived.setFixedWidth(160)
        self.btnArchived.setStyleSheet(
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_pos_border}; outline: none; border-radius: 18px; text-align: center;"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_pos_bg.hex1}, stop:1 {self.theme.core_pos_bg.hex2});"
        )
        self.btnArchived.setHoverData(["border"], [self.theme.core_pos_border], [self.theme.core_pos_border_hover])

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
                projectWidget = project.newDisplayWidget(self.scrollContentWidget)
                
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
        self.emptyProjectsAlert = QLabel("You currently have no projects.\nClick 'NEW PROJECT' above to start one", self)
        self.emptyProjectsAlert.setFont(QFont(self.activeJetFamFont, 16, QFont.Weight.Bold))
        self.emptyProjectsAlert.setStyleSheet(
            f"color: {self.theme.core_widgets_gentext}; text-align: center; border: none; background: transparent;"
        )
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
            icon="icon_settings_anim.png",
            progress=0.0,
            deadline=deadline if deadline else "No Deadline",
            status=Status.NOT_STARTED
        )
        new_proj.controller_ref = self.controller
        
        all_projects = load_projects_from_json()
        all_projects.append(new_proj)
        save_projects_to_json(all_projects)
        self.populateGrid()