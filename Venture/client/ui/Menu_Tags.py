import SettingsHandler, Themes, AnimationHandler, DummyList
from ProjectClasses import Project, Task, Subtask, Tag
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys, json, os, time, datetime, re, sqlite3

class TagsPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.activeFont = self.controller.activeJetFamFont

        layout = QVBoxLayout(self)
        label = QLabel("Tags Management View", self)
        label.setFont(QFont(self.activeFont, 20, QFont.Weight.Bold))
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)