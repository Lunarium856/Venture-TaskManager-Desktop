from dataclasses import dataclass

@dataclass(frozen=True)
class GradientColourLayer:
    hex1: str
    hex2: str

@dataclass(frozen=True)
class Theme:
    name: str

    # Core
    core_bg_main: GradientColourLayer
    core_bg_side: GradientColourLayer
    core_bg_widgets: GradientColourLayer
    core_widgets_gentext: str
    core_widgets_btntext: str
    core_widgets_border: str

    core_positivebutton_bg: GradientColourLayer
    core_positivebutton_border: str
    core_positivebutton_border_hover: str

    core_negativebutton_bg: GradientColourLayer
    core_negativebutton_border: str
    core_negativebutton_border_hover: str

    sidebar_neutralbtn: str
    sidebar_neutralbtn_bg: str
    sidebar_neutralbtn_border: str
    sidebar_highlightedbtn: str
    sidebar_highlightedbtn_bg: str
    sidebar_highlightedbtn_border: str
    sidebar_activebtn: str
    
    scroll_track: str
    scroll_handle: str
    scroll_handle_hover: str
    scroll_border: str

    # Menu Project List
    project_bg: GradientColourLayer
    project_text: str
    project_border: str
    project_border_hover: str
    project_progress: GradientColourLayer

    # note: for entries with two pairs, if the user wants a flat colour, 
    # second pair's value just copies the first 


THEME_DEFAULT = Theme(
    name="Venture",

    core_bg_main=GradientColourLayer("#3e3e3e", "#1e1e1e"),
    core_bg_side=GradientColourLayer("#313131", "#1f1f1f"),
    core_bg_widgets=GradientColourLayer("#181818", "#252525"),
    core_widgets_gentext="#ffffff",
    core_widgets_btntext="#ffffff",
    core_widgets_border="#000000",

    core_positivebutton_bg=GradientColourLayer("#00a0bd", "#35ffbc"),
    core_positivebutton_border="#000000",
    core_positivebutton_border_hover="#ffffff",

    core_negativebutton_bg=GradientColourLayer("#ff2b24", "#ff6c24"),
    core_negativebutton_border="#000000",
    core_negativebutton_border_hover="#ffffff",

    sidebar_neutralbtn="#cccccc",
    sidebar_neutralbtn_bg="transparent",
    sidebar_neutralbtn_border="#1e1e1e",
    sidebar_highlightedbtn="#ffffff",
    sidebar_highlightedbtn_bg="#1e1e1e",
    sidebar_highlightedbtn_border="#444444",
    sidebar_activebtn="#23f3d7",

    scroll_track="#353535",
    scroll_handle="#444444",
    scroll_handle_hover="#93fcee",
    scroll_border="#000000",

    project_bg=GradientColourLayer("#6e6e6e", "#535353"),
    project_text="#ffffff",
    project_border="#000000",
    project_border_hover="#23f3d7",
    project_progress=GradientColourLayer("#00a0bd", "#35ffbc")
)


# Temporarily commented out the Retrobright theme because I keep changing the values here when trying to test things

# THEME_RETROBRIGHT = Theme(
#     name="Retro-Bright",
    
#     core_bg_main=GradientColourLayer("#d1c7ff", "#85ccff"),
#     core_bg_side=GradientColourLayer("#313131", "#1f1f1f"),
#     core_bg_widgets=GradientColourLayer("#181818", "#252525"),
#     core_widgets_gentext="#ffffff",
#     core_widgets_btntext="#ffffff",
#     core_widgets_border="#000000",

#     core_positivebutton_bg=GradientColourLayer("#00a0bd", "#35ffbc"),
#     core_positivebutton_border="#535353",
#     core_positivebutton_border_hover="#ffffff",

#     core_negativebutton_bg=GradientColourLayer("#ff6c24", "#ffa361"),
#     core_negativebutton_border="#535353",
#     core_negativebutton_border_hover="#ffffff",

#     sidebar_neutralbtn="#cccccc",
#     sidebar_neutralbtn_bg="transparent",
#     sidebar_neutralbtn_border="#1e1e1e",
#     sidebar_highlightedbtn="#ffffff",
#     sidebar_highlightedbtn_bg="#1e1e1e",
#     sidebar_highlightedbtn_border="#444444",
#     sidebar_activebtn="#23f3d7",

#     scroll_track="#353535",
#     scroll_handle="#444444",
#     scroll_handle_hover="#93fcee",
#     scroll_border="#000000",

#     project_bg=GradientColourLayer("#6e6e6e", "#535353"),
#     project_text="#ffffff",
#     project_border="#000000",
#     project_border_hover="#23f3d7",
#     project_progress=GradientColourLayer("#00a0bd", "#35ffbc")
# )

AVAILABLE_THEMES = {
    "Venture": THEME_DEFAULT
}

# AVAILABLE_THEMES = {
#     "Venture": THEME_DEFAULT,
#     "Retro-Bright": THEME_RETROBRIGHT
# }

def get_theme(name: str) -> Theme:
    """Retrieves a theme by name, falling back to default if not found."""
    return AVAILABLE_THEMES.get(name, THEME_DEFAULT)

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