import datetime, os
import ProjectClasses

# Path setup for client assets
dir_script = os.path.dirname(os.path.abspath(__file__))       # client/core
client_dir = os.path.dirname(dir_script)                      # client
root_dir = os.path.dirname(client_dir)                        # Venture root
dir_icons = os.path.join(root_dir, "assets", "icons")

testIcon1 = os.path.join(dir_icons, "icon_sidebar_main.png") 
testIcon2 = os.path.join(dir_icons, "icon_sidebar_settings.png")
testIcon3 = os.path.join(dir_icons, "icon_sidebar_tags.png")

now = datetime.datetime.now().isoformat()

read = True
# read = False

def get_initial_dummy_projects():
    """Pure initial sample data generator"""
    if read == False:
        return

    return [
        ProjectClasses.Project(
            projectID=1234,
            name="Venture Testing",
            desc="Dummy Info",
            time_create=now,
            time_elapsed="0d 0h 0m",
            last_update=now,
            tasks=[],
            tags=[
                ProjectClasses.Tag(1234, 987, "Trial", " ", "#ffffff", "#ff0000"),
                ProjectClasses.Tag(1234, 986, "Issue", " ", "#ffffff", "#00ff00"),
                ProjectClasses.Tag(1234, 985, "To-do", " ", "#ffffff", "#0000ff"), 
            ],
            icon=testIcon1,
            progress=75,
            deadline="2025-12-31"
        ),
        ProjectClasses.Project(
            projectID=2345,
            name="Still Testing",
            desc="The quick brown dog jumped over the lazy dog.",
            time_create=now,
            time_elapsed="0d 0h 0m",
            last_update=now,
            tasks=[],
            tags=[
                ProjectClasses.Tag(1234, 987, "Trial", " ", "#ffffff", "#ff0000"),
                ProjectClasses.Tag(1234, 986, "Issue", " ", "#ffffff", "#00ff00"),
                ProjectClasses.Tag(1234, 985, "To-do", " ", "#ffffff", "#0000ff"), 
            ],
            icon=testIcon2,
            progress=37,
            deadline="2025-12-31"
        ),
        ProjectClasses.Project(
            projectID=3456,
            name="Even More Testing",
            desc="It was me, Barry! I reversed the text in the previous entry to throw you for a loop.",
            time_create=now,
            time_elapsed="0d 0h 0m",
            last_update=now,
            tasks=[],
            tags=[
                ProjectClasses.Tag(1234, 987, "Trial", " ", "#ffffff", "#ff0000"),
                ProjectClasses.Tag(1234, 986, "Issue", " ", "#ffffff", "#00ff00"),
                ProjectClasses.Tag(1234, 985, "To-do", " ", "#ffffff", "#0000ff"), 
            ],
            icon=testIcon3,
            progress=75,
            deadline="2025-12-31"
        ),
        ProjectClasses.Project(
            projectID=4567,
            name="Fix this app",
            desc="Dummy Info",
            time_create=now,
            time_elapsed="0d 0h 0m",
            last_update=now,
            tasks=[],
            tags=[
                ProjectClasses.Tag(1234, 987, "Trial", " ", "#ffffff", "#ff0000"),
                ProjectClasses.Tag(1234, 986, "Issue", " ", "#ffffff", "#00ff00"),
                ProjectClasses.Tag(1234, 985, "To-do", " ", "#ffffff", "#0000ff"), 
            ],
            icon=testIcon1,
            progress=75,
            deadline="2025-12-31"
        ),
        ProjectClasses.Project(
            projectID=5678,
            name="Just do it",
            desc="The quick brown dog jumped over the lazy dog.",
            time_create=now,
            time_elapsed="0d 0h 0m",
            last_update=now,
            tasks=[],
            tags=[
                ProjectClasses.Tag(1234, 987, "Trial", " ", "#ffffff", "#ff0000"),
                ProjectClasses.Tag(1234, 986, "Issue", " ", "#ffffff", "#00ff00"),
                ProjectClasses.Tag(1234, 985, "To-do", " ", "#ffffff", "#0000ff"), 
            ],
            icon=testIcon2,
            progress=37,
            deadline="2025-12-31"
        ),
        ProjectClasses.Project(
            projectID=6789,
            name="Crazy? I was crazy once.",
            desc="Crazy? I was crazy once. They locked me in a room. A rubber room! A rubber room with rats, and rats make me crazy.",
            time_create=now,
            time_elapsed="0d 0h 0m",
            last_update=now,
            tasks=[],
            tags=[
                ProjectClasses.Tag(1234, 987, "Trial", " ", "#ffffff", "#ff0000"),
                ProjectClasses.Tag(1234, 986, "Issue", " ", "#ffffff", "#00ff00"),
                ProjectClasses.Tag(1234, 985, "To-do", " ", "#ffffff", "#0000ff"), 
            ],
            icon=testIcon3,
            progress=75,
            deadline="2025-12-31"
        )
    ]