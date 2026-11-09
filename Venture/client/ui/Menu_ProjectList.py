import SettingsHandler, Themes, AnimationHandler, DummyList
from ProjectClasses import Project, Task, Subtask, Tag
from CustomWidgets import HoverButton, RoundedScrollBar
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys, json, os, time, datetime, re, sqlite3

class CreateProjectOverlay(QWidget):
    """Modal overlay parented to stackedWidget with 50% opacity backdrop and resize/recentering event filter."""
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
        self.deadlineInput = QLineEdit()
        self.deadlineInput.setFont(label_font)
        self.deadlineInput.setStyleSheet(
            f"background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_bg_widgets.hex1}, stop:0.8 {self.theme.core_bg_widgets.hex2});"
            f"border: 3px solid {self.theme.core_widgets_border}; " 
            f"border-radius: 10px; padding: 5px; font-size: 12px; color: {self.theme.core_widgets_gentext};"
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

        # tagsContainer = QVBoxLayout()
        # tagsLabel = QLabel("TAGS")
        # tagsLabel.setFont(label_font)
        # tagsLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")
        
        # tagsControlsLayout = QHBoxLayout()
        # tagsBtnLayout = QVBoxLayout()
        # tagsBtnLayout.setSpacing(4)
        
        # for text in ["+", "-", "🔄"]:
        #     b = QPushButton(text)
        #     b.setFixedSize(28, 28)
        #     b.setStyleSheet("border: 2px solid black; border-radius: 8px; background: white; font-weight: bold; color: black;")
        #     tagsBtnLayout.addWidget(b)
        
        # pillsWidget = QWidget()
        # pillsWidget.setStyleSheet("border: none; background: transparent;")
        # pillsLayout = QVBoxLayout(pillsWidget)
        # pillsLayout.setContentsMargins(0, 0, 0, 0)
        # pillsLayout.setSpacing(4)
        # for col in ["#b185ff", "#00ffff", "#ff69b4", "#ffa500", "#adff2f"]:
        #     p = QWidget()
        #     p.setFixedHeight(18); p.setFixedWidth(55)
        #     p.setStyleSheet(f"background-color: {col}; border: 2px solid black; border-radius: 6px;")
        #     pillsLayout.addWidget(p)

        # tagsControlsLayout.addLayout(tagsBtnLayout)
        # tagsControlsLayout.addWidget(pillsWidget)
        # tagsContainer.addWidget(tagsLabel)
        # tagsContainer.addLayout(tagsControlsLayout)
        # midLayout.addLayout(tagsContainer)

        # tasksContainer = QVBoxLayout()
        # tasksLabel = QLabel("TASKS")
        # tasksLabel.setFont(label_font)
        # tasksLabel.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; border: none; background: transparent;")
        # self.tasksListWidget = QListWidget()
        # self.tasksListWidget.setFixedHeight(90)
        # self.tasksListWidget.setStyleSheet(
        #     f"background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0.2 {self.theme.core_bg_widgets.hex1}, stop:0.8 {self.theme.core_bg_widgets.hex2});"
        #     f"border: 3px solid {self.theme.core_widgets_border};"
        #     f"border-radius: 10px; padding: 5px; font-size: 12px; color: black;"
        # )
        # tasksContainer.addWidget(self.tasksListWidget)
        # midLayout.addLayout(tasksContainer, 1)

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
        desc = self.descInput.toPlainText().strip()
        if name and self.on_create_callback:
            self.is_submitting = True
            self.on_create_callback(name, desc)
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
            tName.setStyleSheet("color: #ffa500; border: none; background: transparent;") # TODO: Figure out where in Themes to bind this colour
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
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_negativebutton_bg.hex1}, stop:1 {self.theme.core_negativebutton_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_negativebutton_border}; border-radius: 18px;"
        )
        self.btnBack.clicked.connect(self.controller.returnToProjects)

        self.btnDelete = QPushButton("DELETE PROJECT")
        self.btnDelete.setObjectName("deleteProject")
        self.btnDelete.setFont(QFont(self.activeFont, 14, QFont.Weight.Bold))
        self.btnDelete.setFixedHeight(45)
        self.btnDelete.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_negativebutton_bg.hex1}, stop:1 {self.theme.core_negativebutton_bg.hex2});"
            f"color: {self.theme.core_widgets_btntext}; border: 3px solid {self.theme.core_negativebutton_border}; border-radius: 18px;"
        )
        self.btnDelete.clicked.connect(self.controller.returnToProjects)

        btnContainerLayout.addWidget(self.btnBack)
        btnContainerLayout.addWidget(self.btnDelete)


class ProjectListPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.settingsFunctions = self.controller.settingsFunctions
        self.animator = self.controller.animator
        self.activeJetFamFont = self.controller.activeJetFamFont
        self.theme = self.controller.current_theme
        
        self.saved_projects = DummyList.dummyProjects

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
        self.gridContainerWidget.setStyleSheet("background-color: rgba(30, 30, 30, 0.90); border: 4px solid black; border-radius: 20px;")
        
        gridContainerLayout = QVBoxLayout(self.gridContainerWidget)
        gridContainerLayout.setContentsMargins(8, 8, 8, 8)

        self.scrollArea = QScrollArea(self.gridContainerWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setStyleSheet("background: transparent; border: none;")
        
        # Keep scrollbars always visible occupying dedicated edge tracks
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        
        # Assign Custom Painted Rounded Scrollbars passing controller for theme integration
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
        self.projectsGrid.setContentsMargins(10, 10, 10, 10)

        self.scrollArea.setWidget(self.scrollContentWidget)
        gridContainerLayout.addWidget(self.scrollArea)

        bottomBarLayout = QHBoxLayout()
        bottomBarLayout.setContentsMargins(5, 0, 5, 0)

        self.searchBar = QLineEdit(self)
        self.searchBar.setPlaceholderText("🔍 SEARCH...") # TODO: replace emoji with proper icon
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

    def populateGrid(self):
        while self.projectsGrid.count():
            item = self.projectsGrid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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

    def onNewProjectCreated(self, name, desc):
        new_proj = Project(
            projectID=int(time.time()),
            name=name,
            desc=desc if desc else "No description provided.",
            time_create=datetime.datetime.now().isoformat(),
            last_update=datetime.datetime.now().isoformat(),
            tasks=[],
            tags=[],
            icon="",
            progress=0.0,
            deadline="2026-12-31"
        )
        new_proj.controller_ref = self.controller
        self.saved_projects.append(new_proj)
        
        # Persist changes to local JSON storage
        DummyList.save_projects_to_json(self.saved_projects)
        
        self.populateGrid()