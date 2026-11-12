import SettingsHandler, Themes, AnimationHandler, DummyList
from ProjectClasses import Project, Task, Subtask, Tag
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys, json, os, time, datetime, re, sqlite3

class SettingsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.activeFont = self.controller.activeJetFamFont
        self.theme = self.controller.current_theme

        self.viewContainer = QWidget(self)
        self.viewContainer.setStyleSheet(
            f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.theme.core_bg_main.hex1}, stop:1 {self.theme.core_bg_main.hex2});"
            f"border-right: 4px solid black;"
        )

        baseLayout = QVBoxLayout(self)
        baseLayout.setContentsMargins(0, 0, 0, 0)
        baseLayout.addWidget(self.viewContainer)

        contentLayout = QVBoxLayout(self.viewContainer)
        label = QLabel("Settings View", self.viewContainer)
        label.setFont(QFont(self.activeFont, 20, QFont.Weight.Bold))
        label.setStyleSheet("color: white; border: none; background: transparent;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contentLayout.addWidget(label)