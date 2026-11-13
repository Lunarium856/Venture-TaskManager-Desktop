import SettingsHandler, Themes, AnimationHandler, DummyList
from ProjectClasses import Project, Task, Subtask, Tag, Status
from CustomWidgets import HoverButton, RoundedScrollBar, SmoothGradientWidget, get_resolved_icon_path, tint_pixmap
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys, json, os, time, datetime, re, sqlite3
from Menu_ProjectList import load_projects_from_json

class DayCellWidget(QWidget):
    """Custom widget representing an individual day cell in the calendar grid"""
    def __init__(self, date: datetime.date, is_current_month: bool, events: list, parent=None, controller=None):
        super().__init__(parent)
        self.date = date
        self.is_current_month = is_current_month
        self.events = events
        self.controller = controller
        self.theme = controller.current_theme if controller and hasattr(controller, 'current_theme') else Themes.THEME_DEFAULT
        self.activeFont = controller.activeJetFamFont if controller and hasattr(controller, 'activeJetFamFont') else "Arial"
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Day number label
        dayNumLbl = QLabel(str(self.date.day), self)
        dayNumLbl.setFont(QFont(self.activeFont, 11, QFont.Weight.Bold))
        
        is_today = (self.date == datetime.date.today())
        if is_today:
            dayNumLbl.setStyleSheet(f"color: {self.theme.sidebar_activebtn}; background: transparent; border: none;")
        elif self.is_current_month:
            dayNumLbl.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; background: transparent; border: none;")
        else:
            dayNumLbl.setStyleSheet(f"color: rgba(150, 150, 150, 0.5); background: transparent; border: none;")
            
        layout.addWidget(dayNumLbl)

        # Event / Deadline badges
        if self.events:
            eventCount = len(self.events)
            badgeLbl = QLabel(f"{eventCount} task{'s' if eventCount > 1 else ''}", self)
            badgeLbl.setFont(QFont(self.activeFont, 9, QFont.Weight.Bold))
            badgeLbl.setStyleSheet(
                f"color: {self.theme.core_widgets_btntext};"
                f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0.2 {self.theme.core_pos_bg.hex1}, stop:0.9 {self.theme.core_pos_bg.hex2});"
                f"border-radius: 6px; padding: 2px 4px;"
            )
            layout.addWidget(badgeLbl)

        layout.addStretch()

        # Cell styling
        bg_opacity = "0.35" if is_today else ("0.15" if self.is_current_month else "0.05")
        border_color = self.theme.core_pos_border if is_today else self.theme.core_widgets_border
        
        self.setStyleSheet(
            "QWidget {"
            f"    background-color: rgba(30, 30, 30, {bg_opacity});"
            f"    border: 2px solid {border_color};"
            f"    border-radius: 10px;"
            "}"
        )


class CalendarPage(QWidget):
    """Fully custom interactive Calendar view integrating project & task deadlines"""
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.activeFont = self.controller.activeJetFamFont
        self.theme = self.controller.current_theme
        self.current_date = datetime.date.today()

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

        mainLayout = QVBoxLayout(self.viewContainer)
        mainLayout.setContentsMargins(25, 20, 25, 20)
        mainLayout.setSpacing(15)

        # Header Row: Navigation & Title
        headerRow = QHBoxLayout()
        headerRow.setSpacing(15)

        self.btnPrev = HoverButton("<", self, self.controller.animator)
        self.btnPrev.setFixedSize(40, 40)
        self.btnPrev.setFont(QFont(self.activeFont, 14, QFont.Weight.Bold))
        self.btnPrev.setStyleSheet(
            f"color: {self.theme.core_widgets_btntext};"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_pos_bg.hex1}, stop:1 {self.theme.core_pos_bg.hex2});"
            f"border: 2px solid {self.theme.core_pos_border}; border-radius: 12px;"
        )
        self.btnPrev.setHoverData(["border"], [self.theme.core_pos_border], [self.theme.core_pos_border_hover])
        self.btnPrev.clicked.connect(self.prevMonth)

        self.monthTitleLbl = QLabel("", self)
        self.monthTitleLbl.setFont(QFont(self.activeFont, 20, QFont.Weight.Bold))
        self.monthTitleLbl.setStyleSheet(f"color: {self.theme.sidebar_activebtn}; background: transparent; border: none;")
        self.monthTitleLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btnNext = HoverButton(">", self, self.controller.animator)
        self.btnNext.setFixedSize(40, 40)
        self.btnNext.setFont(QFont(self.activeFont, 14, QFont.Weight.Bold))
        self.btnNext.setStyleSheet(
            f"color: {self.theme.core_widgets_btntext};"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_pos_bg.hex1}, stop:1 {self.theme.core_pos_bg.hex2});"
            f"border: 2px solid {self.theme.core_pos_border}; border-radius: 12px;"
        )
        self.btnNext.setHoverData(["border"], [self.theme.core_pos_border], [self.theme.core_pos_border_hover])
        self.btnNext.clicked.connect(self.nextMonth)

        headerRow.addWidget(self.btnPrev)
        headerRow.addWidget(self.monthTitleLbl, 1)
        headerRow.addWidget(self.btnNext)
        mainLayout.addLayout(headerRow)

        # Days of week header
        weekdaysRow = QHBoxLayout()
        weekdaysRow.setSpacing(8)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for d in days:
            lbl = QLabel(d, self)
            lbl.setFont(QFont(self.activeFont, 11, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color: {self.theme.core_widgets_gentext}; background: transparent; border: none;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            weekdaysRow.addWidget(lbl, 1)
        mainLayout.addLayout(weekdaysRow)

        # Calendar Grid container
        self.gridContainer = QWidget(self)
        self.gridContainer.setStyleSheet(
            f"background-color: {self.theme.core_bg_lists if self.theme.core_bg_lists else 'rgba(10, 10, 10, 0.5)'};"
            f"border: none; border-radius: 15px;"
        )
        self.calendarGrid = QGridLayout(self.gridContainer)
        self.calendarGrid.setSpacing(8)
        self.calendarGrid.setContentsMargins(10, 10, 10, 10)

        mainLayout.addWidget(self.gridContainer, 1)

        # Bottom control bar
        bottomBar = QHBoxLayout()
        self.btnToday = HoverButton("TODAY", self, self.controller.animator)
        self.btnToday.setFont(QFont(self.activeFont, 12, QFont.Weight.Bold))
        self.btnToday.setFixedHeight(40); self.btnToday.setFixedWidth(140)
        self.btnToday.setStyleSheet(
            f"color: {self.theme.core_widgets_btntext};"
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_neutral_bg.hex1}, stop:1 {self.theme.core_neutral_bg.hex2});"
            f"border: 2px solid {self.theme.core_neutral_border}; border-radius: 12px;"
        )
        self.btnToday.setHoverData(["border"], [self.theme.core_neutral_border], [self.theme.core_neutral_border_hover])
        self.btnToday.clicked.connect(self.goToToday)

        bottomBar.addWidget(self.btnToday)
        bottomBar.addStretch()
        mainLayout.addLayout(bottomBar)

        self.populateCalendar()

    def showEvent(self, event):
        super().showEvent(event)
        self.populateCalendar()

    def prevMonth(self):
        first_day = datetime.date(self.current_date.year, self.current_date.month, 1)
        prev_month_last_day = first_day - datetime.timedelta(days=1)
        self.current_date = datetime.date(prev_month_last_day.year, prev_month_last_day.month, 1)
        self.populateCalendar()

    def nextMonth(self):
        if self.current_date.month == 12:
            self.current_date = datetime.date(self.current_date.year + 1, 1, 1)
        else:
            self.current_date = datetime.date(self.current_date.year, self.current_date.month + 1, 1)
        self.populateCalendar()

    def goToToday(self):
        self.current_date = datetime.date.today()
        self.populateCalendar()

    def get_deadline_events(self):
        """Collects all project and task deadlines mapped by date string (YYYY-MM-DD)"""
        events_map = {}
        projects = load_projects_from_json()
        
        for proj in projects:
            if getattr(proj, 'is_archived', False):
                continue
            if hasattr(proj, 'deadline') and proj.deadline and proj.deadline != "No Deadline":
                d_str = str(proj.deadline)[:10]
                events_map.setdefault(d_str, []).append(f"Project: {proj.name}")
            
            for task in getattr(proj, 'tasks', []):
                t_deadline = getattr(task, 'deadline', "No Deadline")
                if t_deadline and t_deadline != "No Deadline":
                    t_str = str(t_deadline)[:10]
                    t_name = task.name if hasattr(task, 'name') else task.get('name', '')
                    events_map.setdefault(t_str, []).append(f"Task: {t_name} ({proj.name})")
                    
        return events_map

    def populateCalendar(self):
        while self.calendarGrid.count():
            item = self.calendarGrid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        year = self.current_date.year
        month = self.current_date.month
        self.monthTitleLbl.setText(self.current_date.strftime("%B %Y").upper())

        events_map = self.get_deadline_events()

        first_day_of_month = datetime.date(year, month, 1)
        start_weekday = first_day_of_month.weekday() # 0 = Mon, 6 = Sun
        current_grid_date = first_day_of_month - datetime.timedelta(days=start_weekday)

        for col in range(7):
            self.calendarGrid.setColumnStretch(col, 1)
        for row in range(6):
            self.calendarGrid.setRowStretch(row, 1)

        for row in range(6):
            for col in range(7):
                date_str = current_grid_date.isoformat()
                day_events = events_map.get(date_str, [])
                is_current_month = (current_grid_date.month == month)

                cell = DayCellWidget(current_grid_date, is_current_month, day_events, parent=self.gridContainer, controller=self.controller)
                self.calendarGrid.addWidget(cell, row, col)

                current_grid_date += datetime.timedelta(days=1)