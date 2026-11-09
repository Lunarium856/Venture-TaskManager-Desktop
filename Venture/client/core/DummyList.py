import ProjectClasses, datetime, os

folder_icons = "icons"
dir_script = os.path.dirname(os.path.abspath(__file__))
dir_icons = os.path.join(dir_script, folder_icons)

testIcon1 = os.path.join(dir_icons, "icon_sidebar_main.png") 
testIcon2 = os.path.join(dir_icons, "icon_sidebar_settings.png")
testIcon3 = os.path.join(dir_icons, "icon_sidebar_tags.png")

now = datetime.datetime.now().isoformat()

dummyProjects = []
dummyProjects.append(ProjectClasses.Project(
    projectID=1234,
    name="Venture Testing",
    desc="Dummy Info",
    time_create=now,
    last_update=now,
    tasks=[],
    tags = [
        ProjectClasses.Tag(1234, 987, "Trial", " ", "ff0000"),
        ProjectClasses.Tag(1234, 986, "Issue", " ", "00ff00"),
        ProjectClasses.Tag(1234, 985, "To-do", " ", "0000ff"), 
    ],
    icon=testIcon1,
    progress=75,
    deadline="2025-12-31"
))

dummyProjects.append(ProjectClasses.Project(
    projectID=2345,
    name="Still Testing",
    desc="The quick brown dog jumped over the lazy dog.",
    time_create=now,
    last_update=now,
    tasks=[],
    tags = [
        ProjectClasses.Tag(1234, 987, "Trial", " ", "ff0000"),
        ProjectClasses.Tag(1234, 986, "Issue", " ", "00ff00"),
        ProjectClasses.Tag(1234, 985, "To-do", " ", "0000ff"), 
    ],
    icon=testIcon2,
    progress=37,
    deadline="2025-12-31"
))

dummyProjects.append(ProjectClasses.Project(
    projectID=3456,
    name="Even More Testing",
    desc="It was me, Barry! I reversed the text in the previous entry to throw you for a loop, so now you're out of touch with ",
    time_create=now,
    last_update=now,
    tasks=[],
    tags = [
        ProjectClasses.Tag(1234, 987, "Trial", " ", "ff0000"),
        ProjectClasses.Tag(1234, 986, "Issue", " ", "00ff00"),
        ProjectClasses.Tag(1234, 985, "To-do", " ", "0000ff"), 
    ],
    icon=testIcon3,
    progress=75,
    deadline="2025-12-31"
))

dummyProjects.append(ProjectClasses.Project(
    projectID=4567,
    name="Fix this app",
    desc="Dummy Info",
    time_create=now,
    last_update=now,
    tasks=[],
    tags = [
        ProjectClasses.Tag(1234, 987, "Trial", " ", "ff0000"),
        ProjectClasses.Tag(1234, 986, "Issue", " ", "00ff00"),
        ProjectClasses.Tag(1234, 985, "To-do", " ", "0000ff"), 
    ],
    icon=testIcon1,
    progress=75,
    deadline="2025-12-31"
))

dummyProjects.append(ProjectClasses.Project(
    projectID=5678,
    name="Just do it",
    desc="The quick brown dog jumped over the lazy dog.",
    time_create=now,
    last_update=now,
    tasks=[],
    tags = [
        ProjectClasses.Tag(1234, 987, "Trial", " ", "ff0000"),
        ProjectClasses.Tag(1234, 986, "Issue", " ", "00ff00"),
        ProjectClasses.Tag(1234, 985, "To-do", " ", "0000ff"), 
    ],
    icon=testIcon2,
    progress=37,
    deadline="2025-12-31"
))

dummyProjects.append(ProjectClasses.Project(
    projectID=6789,
    name="Crazy? I was crazy once. They locked me in a room. A rubber room! A rubber room with rats, and rats make me crazy.",
    desc="Crazy? I was crazy once. They locked me in a room. A rubber room! A rubber room with rats, and rats make me crazy. Crazy? I was crazy once. They locked me in a room. A rubber room! A rubber room with rats, and rats make me crazy. Crazy? I was crazy once. They locked me in a room. A rubber room! A rubber room with rats, and rats make me crazy. Crazy? I was crazy once. They locked me in a room. A rubber room! A rubber room with rats, and rats make me crazy. Crazy? I was crazy once. They locked me in a room. A rubber room! A rubber room with rats, and rats make me crazy. Crazy? I was crazy once.",
    time_create=now,
    last_update=now,
    tasks=[],
    tags = [
        ProjectClasses.Tag(1234, 987, "Trial", " ", "ff0000"),
        ProjectClasses.Tag(1234, 986, "Issue", " ", "00ff00"),
        ProjectClasses.Tag(1234, 985, "To-do", " ", "0000ff"), 
    ],
    icon=testIcon3,
    progress=75,
    deadline="2025-12-31"
))