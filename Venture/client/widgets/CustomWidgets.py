from PyQt6.QtWidgets import QFrame, QWidget, QPushButton, QStyleOptionButton, QScrollBar, QStyleOptionSlider, QStyle, QStackedWidget, QSizePolicy, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QProgressBar, QCheckBox
from PyQt6.QtCore import QEvent, Qt, QVariantAnimation, QParallelAnimationGroup, QPropertyAnimation, QRect, QEasingCurve, QSize, QObject, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap, QFont, QIcon, QLinearGradient, QPainterPath
import Themes
import os, time, datetime, re

def get_resolved_icon_path(icon_str: str) -> str:
    """Resolves an icon path dynamically, supporting built-in assets in icons/core and custom user files"""
    if not icon_str:
        return ""
    
    if os.path.exists(icon_str):
        return icon_str
    
    dir_script = os.path.dirname(os.path.abspath(__file__))       # client/widgets
    client_dir = os.path.dirname(dir_script)                      # client
    root_dir = os.path.dirname(client_dir)                        # Venture root
    
    base_name = os.path.basename(icon_str)
    
    core_path = os.path.join(root_dir, "assets", "icons", "core", base_name)
    if os.path.exists(core_path):
        return core_path
        
    legacy_path = os.path.join(root_dir, "assets", "icons", base_name)
    if os.path.exists(legacy_path):
        return legacy_path
        
    return ""

def tint_pixmap(pixmap: QPixmap, colour: QColor) -> QPixmap:
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
    painter.fillRect(result.rect(), colour)
    painter.end()
    return result

def get_checkmark_icon(size=16, color=QColor("#ffffff")):
    """Generates a clean checkmark icon dynamically for checkbox states."""
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(color, 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen)
    path = QPainterPath()
    path.moveTo(size * 0.25, size * 0.55)
    path.lineTo(size * 0.45, size * 0.75)
    path.lineTo(size * 0.75, size * 0.3)
    painter.drawPath(path)
    painter.end()
    return QIcon(pm)

def animate_progress_bar(prog_bar, target_value, duration=300):
    """Smoothly animates a QProgressBar from its current value to a target value."""
    if not prog_bar:
        return
    if hasattr(prog_bar, '_anim') and prog_bar._anim:
        prog_bar._anim.stop()
    
    anim = QPropertyAnimation(prog_bar, b"value", prog_bar)
    anim.setDuration(duration)
    anim.setStartValue(prog_bar.value())
    anim.setEndValue(target_value)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    anim.start()
    prog_bar._anim = anim

def parse_deadline_to_readable(deadline_str):
    """Converts ISO deadline strings into a human-readable format (e.g. 'Feb 15 2027')."""
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

class ProjectCardWidget(QWidget):
    """Custom widget for Project Cards"""
    def __init__(self, project_instance, parent=None):
        super().__init__(parent)
        self.project_instance = project_instance
        self.base_max_len_name = getattr(project_instance, 'maxLenName', 25)
        self.base_max_len_desc = getattr(project_instance, 'maxLenDesc', 218)
        self.max_observed_width_name = None
        self.max_observed_width_desc = None
        self.nameLabel = None
        self.descLabel = None
        
        self.setObjectName("projectWidget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(300)
        self.setMaximumWidth(16777215)
        
        self.setup_ui()

    def setup_ui(self):
        """Creates the Project Card's UI elements"""
        activeFont = self.project_instance.controller_ref.activeJetFamFont if (self.project_instance.controller_ref and hasattr(self.project_instance.controller_ref, 'activeJetFamFont')) else "Arial"
        theme = self.project_instance.controller_ref.current_theme if (self.project_instance.controller_ref and hasattr(self.project_instance.controller_ref, 'current_theme')) else Themes.THEME_DEFAULT

        widgetLayout = QVBoxLayout(self)
        widgetLayout.setContentsMargins(0, 0, 0, 0)

        projectContentWidget = QWidget(self)
        projectContentWidget.setObjectName("projectContentWidget")
        projectContentWidget.project_instance = self.project_instance
        projectContentWidget.setMinimumHeight(250)
        projectContentWidget.setCursor(Qt.CursorShape.PointingHandCursor)
        projectContentWidget.mousePressEvent = lambda event: self.project_instance.projectClicked()

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
        resolved_icon = get_resolved_icon_path(self.project_instance.icon if self.project_instance.icon else get_resolved_icon_path("icon_settings_anim.png"))
        if resolved_icon:
            pixmap = QPixmap(resolved_icon)
            scaledPM = pixmap.scaled(QSize(32, 32), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            tintedPM = tint_pixmap(scaledPM, QColor(theme.project_text))
            iconLabel.setPixmap(tintedPM)
        elif isinstance(self.project_instance.icon, QIcon):
            pixmap = self.project_instance.icon.pixmap(QSize(32, 32))
            tintedPM = tint_pixmap(pixmap, QColor(theme.project_text))
            iconLabel.setPixmap(tintedPM)
        iconLabel.setStyleSheet("background: transparent; border: none;")

        self.nameLabel = QLabel(self.project_instance.display_name, projectContentWidget)
        self.nameLabel.setFont(QFont(activeFont, 14, QFont.Weight.Bold))
        self.nameLabel.setStyleSheet(f"color: {theme.project_text}; background: transparent; border: none;")

        self.descLabel = QLabel(self.project_instance.display_desc, projectContentWidget)
        self.descLabel.setFont(QFont(activeFont, 10))
        self.descLabel.setWordWrap(True)
        self.descLabel.setStyleSheet(f"color: {theme.project_text}; background: transparent; border: none;")

        topHeaderLayout.addWidget(iconLabel)
        topHeaderLayout.addWidget(self.nameLabel, 1)

        # Status row, contains status badge & elapsed time
        statusRowWidget = QWidget(self)
        if self.project_instance.status.value == 1:
            statusRowColour = [QColor(theme.core_neg_bg.hex1), QColor(theme.core_neg_bg.hex2)]
        elif self.project_instance.status.value == 2:
            statusRowColour = [QColor(theme.core_pos_bg.hex1), QColor(theme.core_pos_bg.hex2)]
        else:
            statusRowColour = [QColor(theme.core_tertiary_bg.hex1), QColor(theme.core_tertiary_bg.hex2)]
        statusRowWidget.setStyleSheet(
            f"background-color: rgba({statusRowColour[0].red()},{statusRowColour[0].green()},{statusRowColour[0].blue()},0.25);"
            f"border: none; border-radius: 8px; padding: 0px;"
        )
        
        statusBadge = QLabel(self.project_instance.status.name.replace("_", " "), statusRowWidget)
        statusBadge.setFont(QFont(activeFont, 10, QFont.Weight.Bold))
        statusBadge.setStyleSheet(
            f"color: {theme.core_widgets_gentext};"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0.2 {statusRowColour[0].name()}, stop:0.9 {statusRowColour[1].name()});"
            f"border: 2px solid {theme.core_widgets_border};"
            f"border-radius: 8px; padding: 2px;"
        )
        
        elapsed_time_label = QLabel(self.project_instance.time_elapsed, statusRowWidget)
        elapsed_time_label.setFont(QFont(activeFont, 10, QFont.Weight.Bold))
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
            safe_progress = int(self.project_instance.progress)
        except (ValueError, TypeError):
            safe_progress = 0
        progBar.setValue(0)
        animate_progress_bar(progBar, safe_progress, duration=400)
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
        progValue.setFont(QFont(activeFont, 12, QFont.Weight.Bold))
        progValue.setStyleSheet(f"color: {theme.project_text if progBar.value() < 100 else theme.core_pos_bg.hex2}; background: transparent; border: none;")

        progBarLayout.addWidget(progBar, 1)
        progBarLayout.addWidget(progValue)

        projectContentLayout.addLayout(topHeaderLayout)
        projectContentLayout.addWidget(self.descLabel)
        projectContentLayout.addStretch()
        projectContentLayout.addWidget(statusRowWidget)
        projectContentLayout.addLayout(progBarLayout)

        self.contentWidget = projectContentWidget

    def resizeEvent(self, event):
        super().resizeEvent(event)
        current_width = self.width()
        if current_width <= 0:
            return

        baseline_width = 500 # base card width
        diff = max(0, baseline_width - current_width)
        
        steps = diff // 20
        new_len_name = max(4, self.base_max_len_name - steps)       
        new_len_desc = max(4, self.base_max_len_desc - steps*10)    
        
        name = self.project_instance.name
        desc = self.project_instance.desc
        new_displayname = name if len(name) <= new_len_name else name[:new_len_name] + "..."
        new_displaydesc = desc if len(desc) <= new_len_desc else desc[:new_len_desc] + "..."
        
        if self.project_instance.display_name != new_displayname or self.project_instance.maxLenName != new_len_name:
            self.project_instance.display_name = new_displayname
            self.project_instance.maxLenName = new_len_name
            if self.nameLabel:
                self.nameLabel.setText(new_displayname)

        if self.project_instance.display_desc != new_displaydesc or self.project_instance.maxLenDesc != new_len_desc:
            self.project_instance.display_desc = new_displaydesc
            self.project_instance.maxLenDesc = new_len_desc
            if self.descLabel:
                self.descLabel.setText(new_displaydesc)


class TaskCardWidget(QFrame):
    """Custom widget for Task Cards"""
    def __init__(self, task_instance, parent=None, on_update_callback=None):
        super().__init__(parent)
        self.task_instance = task_instance
        self.on_update_callback = on_update_callback
        self.task_instance._last_animated_status = bool(self.task_instance.status)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setup_ui()

    def update_status_visuals(self, new_status):
        """Triggers the background and text transition animation for task checkboxes."""
        current_status = getattr(self.task_instance, '_last_animated_status', None)
        if current_status == new_status:
            return
        self.task_instance._last_animated_status = new_status

        state_val = Qt.CheckState.Checked.value if new_status else Qt.CheckState.Unchecked.value
        self.onCheckboxChanged(state_val)

    def update_subtask_progress_ui(self):
        """Updates subtask progress bar and percentage label in place."""
        val = int(getattr(self.task_instance, 'progress', 0.0))
        if hasattr(self, 'sub_progBar') and self.sub_progBar:
            animate_progress_bar(self.sub_progBar, val, duration=300)
        if hasattr(self, 'sub_percentLabel') and self.sub_percentLabel:
            self.sub_percentLabel.setText(f"{val}%")

    def setup_ui(self):
        controller = getattr(self.task_instance, 'controller_ref', None)
        activeFont = controller.activeJetFamFont if controller and hasattr(controller, 'activeJetFamFont') else "Arial"
        theme = controller.current_theme if controller and hasattr(controller, 'current_theme') else Themes.THEME_DEFAULT
        self.animator = getattr(controller, 'animator', None)

        completed = bool(self.task_instance.status)

        bg1 = theme.core_pos_bg.hex1 if completed else theme.core_tertiary_bg.hex1
        bg2 = theme.core_pos_bg.hex2 if completed else theme.core_tertiary_bg.hex2
        border_col = theme.core_pos_border if completed else theme.core_neutral_border

        self.setMinimumWidth(0)
        self.setObjectName("TaskCard")
        self.setStyleSheet(
            f"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {bg1}, stop:1 {bg2});"
            f"    border: 3px solid {border_col};"
            f"    border-radius: 15px;"
        )
        self.installEventFilter(self)

        # Main layout of the TaskCard frame
        contentContainer = QVBoxLayout(self)
        contentContainer.setContentsMargins(12, 10, 12, 10)
        contentContainer.setSpacing(8)

        self.taskContentWidget = QWidget(self)
        self.taskContentWidget.setObjectName("taskContentWidget")
        self.taskContentWidget.setStyleSheet("background: transparent; border: none;")
        
        layout = QHBoxLayout(self.taskContentWidget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Section with Name, Priority, & Deadline
        taskDetails = QVBoxLayout()
        taskDetails.setSpacing(6)

        self.nameLabel = QLabel(f"{self.task_instance.name}")
        self.nameLabel.setFont(QFont(activeFont, 16, QFont.Weight.Bold))
        self.nameLabel.setWordWrap(True)
        self.nameLabel.setStyleSheet(f"color: {theme.sidebar_activebtn if not completed else theme.core_widgets_gentext}; border: none; background: transparent;")

        weight = getattr(self.task_instance, "weight", None)
        weight_str = weight.name.replace("_", " ").title() if hasattr(weight, "name") else str(weight)
        self.weightLabel = QLabel(weight_str)
        self.weightLabel.setFont(QFont(activeFont, 9, QFont.Weight.Light))
        self.weightLabel.setStyleSheet(f"color: {theme.core_widgets_gentext}; border: none; background: transparent;")

        deadline_str = getattr(self.task_instance, 'deadline', "No Deadline")
        readable_deadline = parse_deadline_to_readable(deadline_str)
        self.deadlineLabel = QLabel(f"Deadline: {readable_deadline}", self.taskContentWidget)
        self.deadlineLabel.setFont(QFont(activeFont, 10, QFont.Weight.Bold))
        self.deadlineLabel.setStyleSheet(f"color: {theme.core_widgets_gentext}; background: transparent; border: none;")

        taskDetails.addWidget(self.nameLabel)
        taskDetails.addWidget(self.weightLabel)
        taskDetails.addWidget(self.deadlineLabel)

        has_subtasks = bool(self.task_instance.subtasks)
        has_subtasks = bool(self.task_instance.subtasks)
        if not has_subtasks:
            self.checkbox = CustomCheckBox("", self.taskContentWidget, checkmark_color=theme.project_text)
            self.checkbox.setChecked(bool(self.task_instance.status))
            self.checkbox.setFont(QFont(activeFont, 14, QFont.Weight.Bold))
            self.checkbox.stateChanged.connect(self.onCheckboxChanged)
            
            chk_border = theme.core_pos_border if completed else theme.core_neutral_border
            chk_border_hover = theme.core_pos_border_hover
            
            self.checkbox.setStyleSheet(
                f"QCheckBox {{"
                f"    color: {theme.project_text};"
                f"    background: transparent;"
                f"    border: none; outline: none;"
                f"}}"
                f"QCheckBox::indicator {{"
                f"    width: 32px; height: 32px;"
                f"    background: {theme.core_neutral_bg.hex1};"
                f"    border: 2px solid {chk_border}; border-radius: 12px;"
                f"    outline: none;"
                f"}}"
                f"QCheckBox::indicator:hover {{"
                f"    border: 2px solid {chk_border_hover};"
                f"    outline: none;"
                f"}}"
                f"QCheckBox::indicator:checked {{"
                f"    background: {theme.core_pos_border};"
                f"    border: 2px solid {theme.core_pos_border};"
                f"    outline: none;"
                f"}}"
            )
            self.checkbox.installEventFilter(self)
            layout.addWidget(self.checkbox)
        else:
            progDetails = QHBoxLayout()
            progBar = QProgressBar()
            progBar.setRange(0, 100)
            initial_prog = int(getattr(self.task_instance, 'progress', 0.0))
            progBar.setValue(0)
            animate_progress_bar(progBar, initial_prog, duration=300)
            progBar.setTextVisible(False)
            progBar.setFixedHeight(10)
            progBar.setStyleSheet(
                "QProgressBar {"
                f"border: 2px solid {theme.core_widgets_border}; border-radius: 4px; background-color: {theme.core_widgets_border};"
                "}"
                "QProgressBar::chunk { "
                f"background: qlineargradient(x1:0, y:0.5, x2:1, y2:0.5, stop:0.2 {theme.project_progress.hex1}, stop:0.9 {theme.project_progress.hex2});"
                "   border-radius: 2px; }"
            )
            
            percentVal = int(getattr(self.task_instance, 'progress', 0.0))
            percentLabel = QLabel(f"{percentVal}%", self.taskContentWidget)
            percentLabel.setFont(QFont(activeFont, 12, QFont.Weight.Bold))
            percentLabel.setStyleSheet(f"color: {theme.project_text}; background: transparent; border: none;")

            progDetails.addWidget(percentLabel)
            progDetails.addWidget(progBar)
            taskDetails.addLayout(progDetails)

            # Store references for in-place UI updates
            self.sub_progBar = progBar
            self.sub_percentLabel = percentLabel
        layout.addLayout(taskDetails, 3)

        actionBtns = QGridLayout()
        actionBtns.setContentsMargins(0, 8, 0, 8)
        
        btnPlus = HoverButton("+", parent=self.taskContentWidget, animator=self.animator)
        btnPlus.setFixedSize(32, 32)
        btnPlus.setFont(QFont(activeFont, 12, QFont.Weight.Bold))
        btnPlus.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {theme.core_pos_bg.hex1}, stop:0.8 {theme.core_pos_bg.hex2});"
            f"color: {theme.core_widgets_btntext};"
            f"border: 2px solid {theme.core_pos_border}; border-radius: 8px;"
            f"outline: none;"
        )
        btnPlus.setHoverData(["border"], [theme.core_pos_border], [theme.core_pos_border_hover])
        btnPlus.clicked.connect(self.createSubtaskPrompt)

        btnEdit = EditIconButton(parent=self.taskContentWidget, animator=self.animator)
        btnEdit.clicked.connect(self.editTaskPrompt)

        btnDelete = DeleteIconButton(parent=self.taskContentWidget, animator=self.animator, fixed_width=70)
        btnDelete.clicked.connect(self.deleteTaskPrompt)

        actionBtns.addWidget(btnPlus, 0, 0)
        actionBtns.addWidget(btnEdit, 0, 1)
        actionBtns.addWidget(btnDelete, 1, 0, 1, 2)
        layout.addLayout(actionBtns)

        contentContainer.addWidget(self.taskContentWidget)

        if has_subtasks:
            for sub in self.task_instance.subtasks:
                sub.controller_ref = controller
                subtaskCard = SubtaskCardWidget(sub, self, on_update_callback=self.on_update_callback)
                contentContainer.addWidget(subtaskCard)
    

    def onCheckboxChanged(self, state):
        new_status = (state == Qt.CheckState.Checked.value or state == 2)
        self.task_instance.status = new_status

        controller = getattr(self.task_instance, 'controller_ref', None)
        theme = controller.current_theme if controller and hasattr(controller, 'current_theme') else Themes.THEME_DEFAULT

        start_bg1 = theme.core_tertiary_bg.hex1 if new_status else theme.core_pos_bg.hex1
        end_bg1 = theme.core_pos_bg.hex1 if new_status else theme.core_tertiary_bg.hex1

        start_bg2 = theme.core_tertiary_bg.hex2 if new_status else theme.core_pos_bg.hex2
        end_bg2 = theme.core_pos_bg.hex2 if new_status else theme.core_tertiary_bg.hex2
        
        start_text = theme.sidebar_activebtn if new_status else theme.core_widgets_gentext
        end_text = theme.core_widgets_gentext if new_status else theme.sidebar_activebtn

        self._anim_col1 = QColor(start_bg1)
        self._anim_col2 = QColor(start_bg2)

        def update_task_gradient():
            try:
                c1 = self._anim_col1.name() if isinstance(self._anim_col1, QColor) else str(self._anim_col1)
                c2 = self._anim_col2.name() if isinstance(self._anim_col2, QColor) else str(self._anim_col2)
                grad_str = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {c1}, stop:1 {c2})"
                curr_ss = self.styleSheet() or ""
                if re.search(r"\bbackground\s*:", curr_ss):
                    new_ss = re.sub(r"background\s*:[^;]+;", f"background: {grad_str};", curr_ss)
                else:
                    new_ss = curr_ss.rstrip(";") + f"; background: {grad_str};"
                self.setStyleSheet(new_ss)
            except RuntimeError:
                return

        self._bg_anim1 = QVariantAnimation(self)
        self._bg_anim1.setDuration(150)
        self._bg_anim1.setStartValue(QColor(start_bg1))
        self._bg_anim1.setEndValue(QColor(end_bg1))
        self._bg_anim1.valueChanged.connect(lambda val: setattr(self, '_anim_col1', val) or update_task_gradient())

        self._bg_anim2 = QVariantAnimation(self)
        self._bg_anim2.setDuration(150)
        self._bg_anim2.setStartValue(QColor(start_bg2))
        self._bg_anim2.setEndValue(QColor(end_bg2))
        self._bg_anim2.valueChanged.connect(lambda val: setattr(self, '_anim_col2', val) or update_task_gradient())

        self._bg_anim1.start()
        self._bg_anim2.start()

        if self.animator and hasattr(self, 'nameLabel'):
            txt_anim = self.animator.createAnimation(self.nameLabel, "text", start_text, end_text, duration=150)
            if txt_anim:
                txt_anim.start()
                self._txt_anim = txt_anim

        if self.on_update_callback:
            QTimer.singleShot(250, self.on_update_callback)

    def createSubtaskPrompt(self):
        controller = getattr(self.task_instance, 'controller_ref', None)
        if not controller:
            return
        controller.is_modal_active = True
        from Menu_ProjectList import CreateTaskOverlay
        CreateTaskOverlay(
            parent=controller.stackedWidget,
            animator=controller.animator,
            activeFont=controller.activeJetFamFont,
            title=f"CREATE SUBTASK FOR\n'{self.nameLabel.text()}'",
            on_create_callback=self.onSubtaskCreated,
            controller=controller
        )

    def onSubtaskCreated(self, sub_name, sub_deadline="", sub_weight=Themes.Weight.MEDIUM_PRIORITY if hasattr(Themes, 'Weight') else None):
        from ProjectClasses import Subtask, Weight
        new_sub = Subtask(
            parentID=self.task_instance.taskID,
            subtaskID=int(time.time()),
            name=sub_name,
            desc="",
            tags=[],
            weight=sub_weight if sub_weight else Weight.MEDIUM_PRIORITY,
            status=False
        )
        new_sub.controller_ref = self.task_instance.controller_ref
        if not hasattr(self.task_instance, 'subtasks') or self.task_instance.subtasks is None:
            self.task_instance.subtasks = []
        self.task_instance.subtasks.append(new_sub)
        
        # Force refresh the list to display the newly added subtask card
        if self.on_update_callback:
            self.on_update_callback(refresh_list=True)

    def editTaskPrompt(self):
        controller = getattr(self.task_instance, 'controller_ref', None)
        if not controller:
            return
        controller.is_modal_active = True
        from Menu_ProjectList import EditTaskOverlay
        EditTaskOverlay(
            parent=controller.stackedWidget,
            animator=controller.animator,
            activeFont=controller.activeJetFamFont,
            task_instance=self.task_instance,
            on_save_callback=self.onTaskEdited,
            controller=controller
        )

    def onTaskEdited(self, new_name, new_deadline, new_weight=None):
        self.task_instance.name = new_name
        self.task_instance.deadline = new_deadline
        if new_weight is not None:
            self.task_instance.weight = new_weight
        if self.on_update_callback:
            self.on_update_callback(refresh_list=True)

    def deleteTaskPrompt(self):
        controller = getattr(self.task_instance, 'controller_ref', None)
        if not controller:
            return
        controller.is_modal_active = True
        from Menu_ProjectList import ConfirmActionOverlay
        ConfirmActionOverlay(
            parent=controller.stackedWidget,
            animator=controller.animator,
            activeFont=controller.activeJetFamFont,
            title="DELETE TASK",
            message=f"Are you sure you want to delete task '{self.task_instance.name}'?\nThis action cannot be undone.",
            on_confirm=self.performDelete,
            controller=controller
        )

    def performDelete(self):
        project_ref = getattr(self.task_instance, 'project_ref', None)
        if project_ref and hasattr(project_ref, 'tasks'):
            project_ref.tasks = [t for t in project_ref.tasks if (t.taskID if hasattr(t, 'taskID') else t.get("taskID")) != self.task_instance.taskID]
        if self.on_update_callback:
            self.on_update_callback(refresh_list=True)

class SubtaskCardWidget(QFrame):
    """Custom widget for Subtask Cards"""
    def __init__(self, subtask, parent=None, on_update_callback=None):
        super().__init__(parent)
        self.subtask = subtask
        self.on_update_callback = on_update_callback
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setup_ui()

    def setup_ui(self):
        controller = getattr(self.subtask, 'controller_ref', None)
        activeFont = controller.activeJetFamFont if controller and hasattr(controller, 'activeJetFamFont') else "Arial"
        theme = controller.current_theme if controller and hasattr(controller, 'current_theme') else Themes.THEME_DEFAULT
        self.animator = getattr(controller, 'animator', None)

        completed = bool(getattr(self.subtask, 'status', False))

        bg1 = theme.core_pos_bg.hex1 if completed else theme.sidebar_neutralbtn_border
        bg2 = theme.core_pos_bg.hex2 if completed else theme.sidebar_neutralbtn_border
        border_col = theme.core_pos_border if completed else theme.sidebar_highlightedbtn_border

        self.setMinimumWidth(0)
        self.setObjectName("SubtaskCard")
        self.setStyleSheet(
            f"    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {bg1}, stop:1 {bg2});"
            f"    border: 3px solid {border_col};"
            f"    border-radius: 15px;"
        )
        self.installEventFilter(self)

        contentContainer = QHBoxLayout(self)
        contentContainer.setContentsMargins(10, 8, 10, 8)

        self.checkbox = CustomCheckBox("", checkmark_color=theme.project_text)
        self.checkbox.setChecked(completed)
        self.checkbox.setFont(QFont(activeFont, 14, QFont.Weight.Bold))
        self.checkbox.stateChanged.connect(self.onCheckboxChanged)

        chk_border = theme.core_pos_border if completed else theme.core_neutral_border
        chk_border_hover = theme.core_pos_border_hover
        
        self.checkbox.setStyleSheet(
            f"QCheckBox {{"
            f"    color: {theme.project_text};"
            f"    background: transparent;"
            f"    border: none; outline: none;"
            f"}}"
            f"QCheckBox::indicator {{"
            f"    width: 18px; height: 18px;"
            f"    background: {theme.core_neutral_bg.hex1};"
            f"    border: 2px solid {chk_border}; border-radius: 4px;"
            f"    outline: none;"
            f"}}"
            f"QCheckBox::indicator:hover {{"
            f"    border: 2px solid {chk_border_hover};"
            f"    outline: none;"
            f"}}"
            f"QCheckBox::indicator:checked {{"
            f"    background: {theme.core_pos_border};"
            f"    border: 2px solid {theme.core_pos_border};"
            f"    outline: none;"
            f"}}"
        )
        contentContainer.addWidget(self.checkbox)

        self.subtaskDetailsContainer = QVBoxLayout()
        self.subtaskDetailsContainer.setContentsMargins(0, 0, 0, 0)

        sub_name = getattr(self.subtask, "name", "")
        self.nameLabel = QLabel(sub_name)
        self.nameLabel.setFont(QFont(activeFont, 12, QFont.Weight.Bold))
        self.nameLabel.setWordWrap(True)
        self.nameLabel.setStyleSheet(f"color: {theme.core_widgets_gentext}; border: none; background: transparent;")

        sub_weight = getattr(self.subtask, "weight", None)
        weight_str = sub_weight.name.replace("_", " ").title() if hasattr(sub_weight, "name") else str(sub_weight)
        self.weightLabel = QLabel(weight_str)
        self.weightLabel.setFont(QFont(activeFont, 9, QFont.Weight.Light))
        self.weightLabel.setStyleSheet(f"color: {theme.core_widgets_gentext}; border: none; background: transparent;")

        self.subtaskDetailsContainer.addWidget(self.nameLabel)
        self.subtaskDetailsContainer.addWidget(self.weightLabel)
        contentContainer.addLayout(self.subtaskDetailsContainer, 1)

        btnEdit = EditIconButton(parent=self, animator=self.animator)
        btnEdit.clicked.connect(self.editTaskPrompt)

        btnDelete = DeleteIconButton(parent=self, animator=self.animator)
        btnDelete.clicked.connect(self.deleteTaskPrompt)

        contentContainer.addWidget(btnEdit)
        contentContainer.addWidget(btnDelete)

    def eventFilter(self, obj, event):
        controller = getattr(self.subtask, 'controller_ref', None)
        theme = controller.current_theme if controller and hasattr(controller, 'current_theme') else Themes.THEME_DEFAULT
        completed = bool(getattr(self.subtask, 'status', False))
        
        b_col = theme.core_pos_border if completed else theme.sidebar_highlightedbtn_border
        hl_col = theme.core_pos_border_hover

        if obj.objectName() == "SubtaskCard":
            if event.type() == QEvent.Type.Enter:
                if self.animator:
                    self.animator.animateOnHover(obj, ["border"], [b_col], [hl_col])
                return True
            elif event.type() == QEvent.Type.Leave:
                if self.animator:
                    self.animator.animateOnHover(obj, ["border"], [hl_col], [b_col])
                return True
        return super().eventFilter(obj, event)

    def onCheckboxChanged(self, state):
        new_status = (state == Qt.CheckState.Checked.value or state == 2)
        self.subtask.status = new_status

        controller = getattr(self.subtask, 'controller_ref', None)
        theme = controller.current_theme if controller and hasattr(controller, 'current_theme') else Themes.THEME_DEFAULT

        start_bg1 = theme.sidebar_neutralbtn_border if new_status else theme.core_pos_bg.hex1
        end_bg1 = theme.core_pos_bg.hex1 if new_status else theme.sidebar_neutralbtn_border

        start_bg2 = theme.sidebar_neutralbtn_border if new_status else theme.core_pos_bg.hex2
        end_bg2 = theme.core_pos_bg.hex2 if new_status else theme.sidebar_neutralbtn_border

        self._anim_col1 = QColor(start_bg1)
        self._anim_col2 = QColor(start_bg2)

        def update_subtask_gradient():
            try:
                c1 = self._anim_col1.name() if isinstance(self._anim_col1, QColor) else str(self._anim_col1)
                c2 = self._anim_col2.name() if isinstance(self._anim_col2, QColor) else str(self._anim_col2)
                grad_str = f"qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {c1}, stop:1 {c2})"
                curr_ss = self.styleSheet() or ""
                if re.search(r"\bbackground\s*:", curr_ss):
                    new_ss = re.sub(r"background\s*:[^;]+;", f"background: {grad_str};", curr_ss)
                else:
                    new_ss = curr_ss.rstrip(";") + f"; background: {grad_str};"
                self.setStyleSheet(new_ss)
            except RuntimeError:
                return

        self._bg_anim1 = QVariantAnimation(self)
        self._bg_anim1.setDuration(150)
        self._bg_anim1.setStartValue(QColor(start_bg1))
        self._bg_anim1.setEndValue(QColor(end_bg1))
        self._bg_anim1.valueChanged.connect(lambda val: setattr(self, '_anim_col1', val) or update_subtask_gradient())

        self._bg_anim2 = QVariantAnimation(self)
        self._bg_anim2.setDuration(150)
        self._bg_anim2.setStartValue(QColor(start_bg2))
        self._bg_anim2.setEndValue(QColor(end_bg2))
        self._bg_anim2.valueChanged.connect(lambda val: setattr(self, '_anim_col2', val) or update_subtask_gradient())

        self._bg_anim1.start()
        self._bg_anim2.start()

        if self.on_update_callback:
            QTimer.singleShot(250, self.on_update_callback)

    def editTaskPrompt(self):
        controller = getattr(self.subtask, 'controller_ref', None)
        if not controller:
            return
        controller.is_modal_active = True
        from Menu_ProjectList import EditTaskOverlay
        EditTaskOverlay(
            parent=controller.stackedWidget,
            animator=controller.animator,
            activeFont=controller.activeJetFamFont,
            title="EDIT SUBTASK",
            task_instance=self.subtask,
            on_save_callback=self.onSubtaskEdited,
            controller=controller
        )

    def onSubtaskEdited(self, new_name, new_deadline, new_weight=None):
        self.subtask.name = new_name
        if hasattr(self.subtask, 'deadline'):
            self.subtask.deadline = new_deadline
        if new_weight is not None:
            self.subtask.weight = new_weight
        if self.on_update_callback:
            self.on_update_callback(refresh_list=True)

    def deleteTaskPrompt(self):
        controller = getattr(self.subtask, 'controller_ref', None)
        if not controller:
            return
        controller.is_modal_active = True
        from Menu_ProjectList import ConfirmActionOverlay
        ConfirmActionOverlay(
            parent=controller.stackedWidget,
            animator=controller.animator,
            activeFont=controller.activeJetFamFont,
            title="DELETE SUBTASK",
            message=f"Are you sure you want to delete subtask '{self.subtask.name}'?\nThis action cannot be undone.",
            on_confirm=self.performDelete,
            controller=controller
        )

    def performDelete(self):
        parent_task = self.parent().task_instance if self.parent() and hasattr(self.parent(), 'task_instance') else None
        if parent_task and hasattr(parent_task, 'subtasks'):
            parent_task.subtasks = [s for s in parent_task.subtasks if (s.subtaskID if hasattr(s, 'subtaskID') else s.get("subtaskID")) != self.subtask.subtaskID]
        if self.on_update_callback:
            self.on_update_callback(refresh_list=True)


class HoverButton(QPushButton):
    """Custom Button that supports AnimationHandler's functionalities"""
    def __init__(self, text, parent=None, animator=None):
        super().__init__(text, parent)
        self.animator = animator
        self.anim_type = ["border"]
        self.start_val = []
        self.end_val = []
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def setHoverData(self, anim_type, start_val, end_val):
        """Stores animation details"""
        self.anim_type = anim_type
        self.start_val = start_val
        self.end_val = end_val

    def enterEvent(self, event):
        if self.animator and self.start_val and self.end_val:
            self.animator.animateOnHover(
                self, 
                self.anim_type, 
                self.start_val, 
                self.end_val
            )
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.animator and self.start_val and self.end_val:
            self.animator.animateOnHover(
                self, 
                self.anim_type, 
                self.end_val, 
                self.start_val
            )
        super().leaveEvent(event)

class EditIconButton(HoverButton):
    """Reusable Edit button with preset styling and icon resolution"""
    def __init__(self, parent=None, animator=None, theme=None):
        super().__init__("", parent=parent, animator=animator)
        theme = theme or (parent.controller_ref.current_theme if parent and hasattr(parent, 'controller_ref') and parent.controller_ref else Themes.THEME_DEFAULT)
        
        self.setFixedSize(32, 32)
        edit_icon_path = get_resolved_icon_path("icon_project_edit.png")
        if edit_icon_path and os.path.exists(edit_icon_path):
            pm = QPixmap(edit_icon_path).scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            tinted_pm = tint_pixmap(pm, QColor(theme.core_widgets_btntext))
            self.setIcon(QIcon(tinted_pm))
            self.setIconSize(QSize(18, 18))
            
        self.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {theme.core_pos_bg.hex1}, stop:0.8 {theme.core_pos_bg.hex2});"
            f"color: {theme.core_widgets_btntext};"
            f"border: 2px solid {theme.core_pos_border}; border-radius: 8px;"
            f"outline: none;"
        )
        self.setHoverData(["border"], [theme.core_widgets_border], [theme.core_pos_border_hover])


class DeleteIconButton(HoverButton):
    """Reusable Delete button with preset styling and icon resolution"""
    def __init__(self, parent=None, animator=None, theme=None, fixed_width=32):
        super().__init__("", parent=parent, animator=animator)
        theme = theme or (parent.controller_ref.current_theme if parent and hasattr(parent, 'controller_ref') and parent.controller_ref else Themes.THEME_DEFAULT)
        
        self.setFixedSize(fixed_width, 32)
        delete_icon_path = get_resolved_icon_path("icon_project_delete.png")
        if delete_icon_path and os.path.exists(delete_icon_path):
            pm = QPixmap(delete_icon_path).scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            tinted_pm = tint_pixmap(pm, QColor(theme.core_widgets_btntext))
            self.setIcon(QIcon(tinted_pm))
            self.setIconSize(QSize(18, 18))
            
        self.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {theme.core_neg_bg.hex1}, stop:0.8 {theme.core_neg_bg.hex2});"
            f"color: {theme.core_widgets_btntext};"
            f"border: 2px solid {theme.core_neg_border}; border-radius: 8px;"
            f"outline: none;"
        )
        self.setHoverData(["border"], [theme.core_widgets_border], [theme.core_neg_border_hover])

class ArchiveIconButton(HoverButton):
    """Reusable Delete button with preset styling and icon resolution"""
    def __init__(self, parent=None, animator=None, theme=None, fixed_width=32):
        super().__init__("", parent=parent, animator=animator)
        theme = theme or (parent.controller_ref.current_theme if parent and hasattr(parent, 'controller_ref') and parent.controller_ref else Themes.THEME_DEFAULT)
        
        self.setFixedSize(fixed_width, 32)
        delete_icon_path = get_resolved_icon_path("icon_sidebar_archive.png")
        if delete_icon_path and os.path.exists(delete_icon_path):
            pm = QPixmap(delete_icon_path).scaled(18, 18, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            tinted_pm = tint_pixmap(pm, QColor(theme.core_widgets_btntext))
            self.setIcon(QIcon(tinted_pm))
            self.setIconSize(QSize(18, 18))
            
        self.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {theme.core_neutral_bg.hex1}, stop:0.8 {theme.core_neutral_bg.hex2});"
            f"color: {theme.core_widgets_btntext};"
            f"border: 2px solid {theme.core_neutral_border}; border-radius: 8px;"
            f"outline: none;"
        )
        self.setHoverData(["border"], [theme.core_widgets_border], [theme.core_neg_border_hover])

class CustomCheckBox(QCheckBox):
    """Custom QCheckBox that paints the checkmark directly inside its indicator box."""
    def __init__(self, text="", parent=None, checkmark_color="#ffffff"):
        super().__init__(text, parent)
        self.checkmark_color = checkmark_color

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isChecked():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            
            opt = QStyleOptionButton()
            self.initStyleOption(opt)
            ind_rect = self.style().subElementRect(QStyle.SubElement.SE_CheckBoxIndicator, opt, self)
            
            if ind_rect.isValid() and not ind_rect.isEmpty():
                size = min(ind_rect.width(), ind_rect.height())
                pen = QPen(QColor(self.checkmark_color), 2.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                
                path = QPainterPath()
                x = ind_rect.x()
                y = ind_rect.y()
                path.moveTo(x + size * 0.25, y + size * 0.55)
                path.lineTo(x + size * 0.45, y + size * 0.75)
                path.lineTo(x + size * 0.75, y + size * 0.3)
                painter.drawPath(path)
            painter.end()

class SmoothGradientWidget(QWidget):
    """Custom widget rendering smooth diagonal gradients to eliminate colour banding"""
    def __init__(self, hex1, hex2, border_colour="black", border_width=4, parent=None):
        super().__init__(parent)
        self.c1 = QColor(hex1)
        self.c2 = QColor(hex2)
        self.border_colour = QColor(border_colour)
        self.border_width = border_width
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        steps = 15
        for i in range(steps + 1):
            t = i / steps
            r = int(self.c1.red() + (self.c2.red() - self.c1.red()) * t)
            g = int(self.c1.green() + (self.c2.green() - self.c1.green()) * t)
            b = int(self.c1.blue() + (self.c2.blue() - self.c1.blue()) * t)
            gradient.setColorAt(t, QColor(r, g, b))
        
        painter.fillRect(self.rect(), gradient)
        
        if self.border_width > 0:
            painter.setPen(QPen(self.border_colour, self.border_width))
            right_x = self.width() - (self.border_width // 2)
            painter.drawLine(right_x, 0, right_x, self.height())


class RoundedScrollBar(QScrollBar):
    """Custom painted scrollbar because QSS is annoying"""
    def __init__(self, orientation=Qt.Orientation.Vertical, parent=None, controller=None):
        super().__init__(orientation, parent)
        self.controller = controller
        theme = self.controller.current_theme if (self.controller and hasattr(self.controller, 'current_theme')) else Themes.THEME_DEFAULT
        
        self.handle_colour = QColor(f"{theme.scroll_handle}")
        self.setMouseTracking(True)
        
        self.color_anim = QVariantAnimation(self)
        self.color_anim.setDuration(200)
        self.color_anim.valueChanged.connect(self._on_colour_anim_value)

    def _on_colour_anim_value(self, colour):
        self.handle_colour = colour
        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        theme = self.controller.current_theme if (self.controller and hasattr(self.controller, 'current_theme')) else Themes.THEME_DEFAULT
        self.color_anim.stop()
        self.color_anim.setStartValue(self.handle_colour)
        self.color_anim.setEndValue(QColor(f"{theme.scroll_handle_hover}"))
        self.color_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        theme = self.controller.current_theme if (self.controller and hasattr(self.controller, 'current_theme')) else Themes.THEME_DEFAULT
        self.color_anim.stop()
        self.color_anim.setStartValue(self.handle_colour)
        self.color_anim.setEndValue(QColor(f"{theme.scroll_handle}"))
        self.color_anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        
        theme = self.controller.current_theme if (self.controller and hasattr(self.controller, 'current_theme')) else Themes.THEME_DEFAULT
        
        track_rect = self.rect()
        painter.setPen(QPen(QColor(f"{theme.scroll_border}"), 2))
        painter.setBrush(QColor(f"{theme.scroll_track}"))
        
        if self.orientation() == Qt.Orientation.Vertical:
            draw_rect = track_rect.adjusted(1, 10, -1, -10)
            painter.drawRoundedRect(draw_rect, 7, 7)
        else:
            draw_rect = track_rect.adjusted(10, 1, -10, -1)
            painter.drawRoundedRect(draw_rect, 7, 7)
        
        handle_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ScrollBar, opt, QStyle.SubControl.SC_ScrollBarSlider, self
        )
        if handle_rect.isValid() and not handle_rect.isEmpty():
            painter.setPen(QPen(QColor(f"{theme.scroll_border}"), 2))
            painter.setBrush(self.handle_colour)
            
            if self.orientation() == Qt.Orientation.Vertical:
                h_rect = handle_rect.adjusted(2, 2, -2, -2)
                painter.drawRoundedRect(h_rect, 5, 5)
            else:
                h_rect = handle_rect.adjusted(2, 2, -2, -2)
                painter.drawRoundedRect(h_rect, 5, 5)


class CustomStackedWidget(QStackedWidget):
    """Customized QStackedWidget to support card-deck animations"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.move_anim = QParallelAnimationGroup(self)
        self.is_animating = False

    def animateTransition(self, target_widget, enter_anim=True, duration=300):
        """Creates & runs the animation for card-deck view switching"""
        if self.is_animating:
            return
        
        current_widget = self.currentWidget()
        if current_widget == target_widget:
            return

        if self.indexOf(target_widget) == -1:
            self.addWidget(target_widget)

        self.is_animating = True
        w = self.width()
        h = self.height()

        target_widget.resize(w, h)
        if current_widget:
            current_widget.resize(w, h)

        anim_group = QParallelAnimationGroup(self)

        if enter_anim:
            target_widget.raise_()
            target_widget.show()
            target_widget.setGeometry(-w, 0, w, h)

            anim_in = QPropertyAnimation(target_widget, b"geometry", self)
            anim_in.setDuration(duration+150) # +150 ms makes the entrance animation smoother
            anim_in.setStartValue(QRect(-w, 0, w, h))
            anim_in.setEndValue(QRect(0, 0, w, h))
            anim_in.setEasingCurve(QEasingCurve.Type.OutQuint)
            anim_group.addAnimation(anim_in)
        else:
            if current_widget:
                current_widget.raise_()
                current_widget.show()
                target_widget.show()
                target_widget.setGeometry(0, 0, w, h)

                from Menu_ProjectList import ProjectDetailPage
                anim_out = QPropertyAnimation(current_widget, b"geometry", self)
                anim_out.setDuration(duration if not isinstance(target_widget, ProjectDetailPage) else duration-150)
                anim_out.setStartValue(QRect(0, 0, w, h))
                anim_out.setEndValue(QRect(-w, 0, w, h))
                anim_out.setEasingCurve(QEasingCurve.Type.InQuart)
                anim_group.addAnimation(anim_out)

        def on_finished():
            self.setCurrentWidget(target_widget)
            if current_widget:
                current_widget.setGeometry(0, 0, w, h)
            target_widget.setGeometry(0, 0, w, h)
            self.is_animating = False

        anim_group.finished.connect(on_finished)
        self.move_anim = anim_group
        anim_group.start()