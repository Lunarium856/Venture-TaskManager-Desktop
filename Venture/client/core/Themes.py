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
    core_bg_lists: str
    core_widgets_gentext: str
    core_widgets_btntext: str
    core_widgets_border: str

    # Core - For States
    core_neutral_bg: GradientColourLayer
    core_neutral_border: str
    core_neutral_border_hover: str

    core_pos_bg: GradientColourLayer
    core_pos_border: str
    core_pos_border_hover: str

    core_neg_bg: GradientColourLayer
    core_neg_border: str
    core_neg_border_hover: str

    core_tertiary_bg: GradientColourLayer
    core_tertiary_border: str
    core_tertiary_border_hover: str

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

    core_bg_main=GradientColourLayer("#3e3e3e", "#252525"),
    core_bg_side=GradientColourLayer("#222433", "#15102E"),
    core_bg_widgets=GradientColourLayer("#181818", "#252525"),
    core_bg_lists="", # default theme & behaviours render a semi-transparent black box (10, 10, 10, 0.5).
    core_widgets_gentext="#ffffff",
    core_widgets_btntext="#ffffff",
    core_widgets_border="#000000",

    core_neutral_bg=GradientColourLayer("#444444", "#353535"),
    core_neutral_border="#000000",
    core_neutral_border_hover="#ffffff",

    core_pos_bg=GradientColourLayer("#00a0bd", "#23f3d7"),
    core_pos_border="#000000",
    core_pos_border_hover="#ffffff",

    core_neg_bg=GradientColourLayer("#ff2b24", "#ff6c24"),
    core_neg_border="#000000",
    core_neg_border_hover="#ffffff",

    core_tertiary_bg=GradientColourLayer("#222433","#15102E"),
    core_tertiary_border="#444444",
    core_tertiary_border_hover="#ffffff",

    sidebar_neutralbtn="#cccccc",
    sidebar_neutralbtn_bg="transparent",
    sidebar_neutralbtn_border="#1e1e1e",
    sidebar_highlightedbtn="#ffffff",
    sidebar_highlightedbtn_bg="#13151F",
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
    project_progress=GradientColourLayer("#00a0bd", "#23f3d7")
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

#     core_pos_bg=GradientColourLayer("#00a0bd", "#35ffbc"),
#     core_pos_border="#535353",
#     core_pos_border_hover="#ffffff",

#     core_neg_bg=GradientColourLayer("#ff6c24", "#ffa361"),
#     core_neg_border="#535353",
#     core_neg_border_hover="#ffffff",

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