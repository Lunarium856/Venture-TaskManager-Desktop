from dataclasses import dataclass

@dataclass(frozen=True)
class GradientColourLayer:
    path1: str
    hex1: str
    path2: str
    hex2: str

@dataclass(frozen=True)
class Theme:
    name: str
    bg_main: GradientColourLayer
    bg_sidebar: GradientColourLayer
    bg_widgets: GradientColourLayer
    text_content: GradientColourLayer
    text_button: GradientColourLayer
    active_button: GradientColourLayer
    scroll_track: str
    scroll_handle: str
    scroll_handle_hover: str
    scroll_border: str
    project_bg: GradientColourLayer
    project_text: str
    project_border: str
    project_border_hover: str
    project_progress: GradientColourLayer

    # note: for entries with two pairs, if the user wants a flat colour, 
    # second pair's value just copies the first 


THEME_DEFAULT = Theme(
    name="Venture",
    bg_main=GradientColourLayer("main/bg1", "#3e3e3e", "main/bg2", "#1e1e1e"),
    bg_sidebar=GradientColourLayer("side/bg1", "#3e3e3e", "side/bg2", "#1e1e1e"),
    bg_widgets=GradientColourLayer("txt/c1", "#ffffff", "widgets/c2", "#aaaaaa"),
    text_content=GradientColourLayer("txt/c1", "#ffffff", "txt/c2", "#aaaaaa"),
    text_button=GradientColourLayer("btn/c1", "#ffffff", "btn/c2", "#aaaaaa"),
    active_button=GradientColourLayer("act/c1", "#00ff00", "act/c2", "#00aa00"),
    scroll_track="#353535",
    scroll_handle="#444444",
    scroll_handle_hover="#ffffff",
    scroll_border="#000000",
    project_bg=GradientColourLayer("project/bg1", "#6e6e6e", "project/bg2", "#535353"),
    project_text="#ffffff",
    project_border="#000000",
    project_border_hover="#08af40",
    project_progress=GradientColourLayer("project/prog1", "#9dc7ff", "project/prog2", "#c0d7ff")
)

THEME_RETROBRIGHT = Theme(
    name="Retro-Bright",
    bg_main=GradientColourLayer("main/bg1", "#3e3e3e", "main/bg2", "#1e1e1e"),
    bg_sidebar=GradientColourLayer("side/bg1", "#3e3e3e", "side/bg2", "#1e1e1e"),
    bg_widgets=GradientColourLayer("txt/c1", "#ffffff", "widgets/c2", "#aaaaaa"),
    text_content=GradientColourLayer("txt/c1", "#ffffff", "txt/c2", "#aaaaaa"),
    text_button=GradientColourLayer("btn/c1", "#ffffff", "btn/c2", "#aaaaaa"),
    active_button=GradientColourLayer("act/c1", "#00ff00", "act/c2", "#00aa00"),
    scroll_track="#353535",
    scroll_handle="#444444",
    scroll_handle_hover="#ffffff",
    scroll_border="#000000",
    project_bg=GradientColourLayer("project/bg1", "#6e6e6e", "project/bg2", "#535353"),
    project_text="#000000",
    project_border="#000000",
    project_border_hover="#08af40",
    project_progress=GradientColourLayer("project/prog1", "#9dc7ff", "project/prog2", "#c0d7ff")
)

# THEME_RETROBRIGHT = Theme(
#     name="Retro-Bright",
#     bg_main=GradientColourLayer("main/bg1", "#3e3e3e", "main/bg2", "#1e1e1e"),
#     bg_sidebar=GradientColourLayer("side/bg1", "#3e3e3e", "side/bg2", "#1e1e1e"),
#     bg_widgets=GradientColourLayer("txt/c1", "#ffffff", "widgets/c2", "#aaaaaa"),
#     text_content=GradientColourLayer("txt/c1", "#ffffff", "txt/c2", "#aaaaaa"),
#     text_button=GradientColourLayer("btn/c1", "#ffffff", "btn/c2", "#aaaaaa"),
#     active_button=GradientColourLayer("act/c1", "#00ff00", "act/c2", "#00aa00"),
#     scroll_track="#353535",
#     scroll_handle="#444444",
#     scroll_handle_hover="#ffffff",
#     scroll_border="#000000",
#     project_bg=GradientColourLayer("project/bg1", "#9dc7ff", "project/bg2", "#c0d7ff"),
#     project_text="#000000",
#     project_border="#000000",
#     project_border_hover="#08af40",
#     project_progress=GradientColourLayer("project/prog1", "#00ff0a", "project/prog2", "#c2fabf")
# )

# THEME_RETROBRIGHT = Theme()
# THEME_PYTHON = Theme()
# THEME_SPRING = Theme()
# THEME_SUMMER = Theme()
# THEME_AUTUMN = Theme()
# THEME_WINTER = Theme()


# self.colour_mainBG1 = self.qsettings.value("main/bgcol1", QColor("#7c3aff"), type=QColor)
# self.colour_mainBG2 = self.qsettings.value("main/bgcol2", QColor("#35709b"), type=QColor)

# self.colour_newProjectBG1 = self.qsettings.value("main/newproject1", QColor("#fdeda6"), type=QColor)
# self.colour_newProjectBG2 = self.qsettings.value("main/newproject2", QColor("#fff500"), type=QColor)
# self.colour_newProjectBG1_HL = self.qsettings.value("main/newproject1highlight", QColor("#73e7a7"), type=QColor)
# self.colour_newProjectBG2_HL = self.qsettings.value("main/newproject2highlight", QColor("#08af40"), type=QColor)
# self.colour_newProjectText = self.qsettings.value("main/btntext", QColor("black"), type=QColor)
# self.colour_newProjectText_HL = self.qsettings.value("main/btntexthighlight", QColor("#ececec"), type=QColor)

# self.colour_sidebarBG = self.qsettings.value("sidebar/bgcol", QColor("#c0b8e4"), type=QColor)
# self.colour_sidebarBtnText = self.qsettings.value("sidebar/btntextcol", QColor("#5c5c5c"), type=QColor)
# self.colour_sidebarActiveMenu = self.qsettings.value("sidebar/activebtncol", QColor("#f1eeff"), type=QColor)
# self.colour_sidebarBtn_HL = self.qsettings.value("sidebar/activebtntextcol", QColor("#0086b8"), type=QColor)
# self.colour_name = self.qsettings.value("sidebar/appname", QColor("#000000"), type=QColor)

# self.colour_noProjectsBG1 = self.qsettings.value("main/noproject1", self.colour_sidebarBG.lighter(140), type=QColor)
# self.colour_noProjectsBG2 = self.qsettings.value("main/noproject2", self.colour_sidebarBG, type=QColor)
# self.colour_projectWidgetBG1 = self.qsettings.value("project/projectwidgetbgcol1", QColor("#faf8ff"), type=QColor)
# self.colour_projectWidgetBG2 = self.qsettings.value("project/projectwidgetbgcol2", QColor("#85ccff"), type=QColor)
# self.colour_projectWidgetText = self.qsettings.value("project/projectwidgettext", QColor("#000000"), type=QColor)
# self.colour_projectWidgetBorder = self.qsettings.value("project/projectwidgetborder", QColor("#000000"), type=QColor)
# self.colour_projectWidget_HL = self.qsettings.value("project/projectwidgethighlight", QColor("#08af40"), type=QColor)

# self.colour_editBtnBG1 = self.qsettings.value("actions/editbtn1", QColor("#ff6c24"), type=QColor)
# self.colour_editBtnBG2 = self.qsettings.value("actions/editbtn2", QColor("#ffa361"), type=QColor)
# self.colour_deleteBtnBG1 = self.qsettings.value("actions/deletebtn1", QColor("#dd0202"), type=QColor)
# self.colour_deleteBtnBG2 = self.qsettings.value("actions/deletebtn2", QColor("#c12659"), type=QColor)
# self.colour_actionBtnBorder = self.qsettings.value("actions/btnborder", self.colour_projectWidgetBorder, type=QColor)
# self.colour_actionBtnBorder_HL = self.qsettings.value("actions/btnborderhighlight", self.colour_projectWidget_HL, type=QColor)

# self.colour_projectProgress1 = self.qsettings.value("project/projectprogress1", QColor("#00ff0a"), type=QColor)
# self.colour_projectProgress2 = self.qsettings.value("project/projectprogress2", QColor("#c2fabf"), type=QColor)