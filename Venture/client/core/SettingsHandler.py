import Themes
from PyQt6.QtWidgets import QColorDialog
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QColor
import os

class Settings:
    def __init__ (self, main_window):
        self.main_window = main_window
        dir_script = os.path.dirname(os.path.abspath(__file__))
        settings_path = os.path.join(dir_script, "settings.ini")
        self.qsettings = QSettings(settings_path, QSettings.Format.IniFormat)

        self.init_ColourSettings()
        self.init_SystemSettings()

    def newColour_MainBG(self, accessMode: str):
        """ACCESS MODES:\n
        R = Read | L = Load | O = Overwrite | S = Save | C = Clear """
        match(accessMode.upper()):
            case "R":
                print("Not yet implemented")
                pass
            case "L":
                self.main_window.setBGColour()
            case "O":
                newColour1 = QColorDialog.getColor(self.colour_mainBG1, self.main_window, "Select Start Background Color")
                if newColour1.isValid():
                    self.colour_mainBG1 = newColour1
                    self.qsettings.setValue("main/bgcol1", self.colour_mainBG1)
                newColour2 = QColorDialog.getColor(self.colour_mainBG2, self.main_window, "Select End Background Color")
                if newColour2.isValid():
                    self.colour_mainBG2 = newColour2
                    self.qsettings.setValue("main/bgcol2", self.colour_mainBG2)
                self.main_window.setBGColour()
            case "S":
                self.qsettings.sync()
            case "C": 
                self.colour_mainBG1 = QColor("#7c3aff")
                self.colour_mainBG2 = QColor("#35709b")
                self.qsettings.setValue("main/bgcol1", self.colour_mainBG1)
                self.qsettings.setValue("main/bgcol2", self.colour_mainBG2)
                self.main_window.setBGColour()
            case _:
                raise TypeError("Invalid access mode")
        self.qsettings.sync() 
        
    def init_ColourSettings(self):
        # Load theme colors and default retro palette settings
        self.colour_mainBG1 = self.qsettings.value("main/bgcol1", QColor("#7c3aff"), type=QColor)
        self.colour_mainBG2 = self.qsettings.value("main/bgcol2", QColor("#35709b"), type=QColor)
        
        self.colour_sidebarBG = self.qsettings.value("sidebar/bgcol", QColor("#c0b8e4"), type=QColor)
        self.colour_sidebarBtnText = self.qsettings.value("sidebar/btntextcol", QColor("#5c5c5c"), type=QColor)
        self.colour_sidebarActiveMenu = self.qsettings.value("sidebar/activebtncol", QColor("#f1eeff"), type=QColor)
        self.colour_sidebarBtn_HL = self.qsettings.value("sidebar/activebtntextcol", QColor("#0086b8"), type=QColor)
        
        self.colour_newProjectBG1 = self.qsettings.value("main/newproject1", QColor("#fdeda6"), type=QColor)
        self.colour_newProjectBG2 = self.qsettings.value("main/newproject2", QColor("#fff500"), type=QColor)
        self.colour_newProjectText = self.qsettings.value("main/btntext", QColor("black"), type=QColor)
        
        self.colour_noProjectsBG1 = self.qsettings.value("main/noproject1", self.colour_sidebarBG.lighter(140), type=QColor)
        self.colour_noProjectsBG2 = self.qsettings.value("main/noproject2", self.colour_sidebarBG, type=QColor)

    def init_SystemSettings(self):
        self.startupWindowState = self.qsettings.value("startupWindowState", 1, type=int)