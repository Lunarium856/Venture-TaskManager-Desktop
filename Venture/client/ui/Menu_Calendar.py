import SettingsHandler, Themes, AnimationHandler, DummyList
from ProjectClasses import Project, Task, Subtask, Tag
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys, json, os, time, datetime, re, sqlite3

class CalendarPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.activeFont = self.controller.activeJetFamFont

        calendar_layout = QVBoxLayout(self)
        cal_label = QLabel("Calendar View", self)
        cal_label.setFont(QFont(self.activeFont, 20, QFont.Weight.Bold))
        cal_label.setStyleSheet("color: white;")
        cal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        calendar_layout.addWidget(cal_label)