import datetime, os, json

# Path setup for client/data/projects.json
dir_script = os.path.dirname(os.path.abspath(__file__))       # client/core
client_dir = os.path.dirname(dir_script)                      # client
root_dir = os.path.dirname(client_dir)                        # Venture root
dir_icons = os.path.join(root_dir, "assets", "icons")
data_dir = os.path.join(client_dir, "data")

if not os.path.exists(data_dir):
    os.makedirs(data_dir)

projects_json_path = os.path.join(data_dir, "projects.json")

import ProjectClasses

testIcon1 = os.path.join(dir_icons, "icon_sidebar_main.png") 
testIcon2 = os.path.join(dir_icons, "icon_sidebar_settings.png")
testIcon3 = os.path.join(dir_icons, "icon_sidebar_tags.png")

now = datetime.datetime.now().isoformat()

def get_initial_dummy_projects():
    return [
        ProjectClasses.Project(
            projectID=1234,
            name="Venture Testing",
            desc="Dummy Info",
            time_create=now,
            last_update=now,
            tasks=[],
            tags=[
                ProjectClasses.Tag(1234, 987, "Trial", " ", "ff0000"),
                ProjectClasses.Tag(1234, 986, "Issue", " ", "00ff00"),
                ProjectClasses.Tag(1234, 985, "To-do", " ", "0000ff"), 
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
            last_update=now,
            tasks=[],
            tags=[
                ProjectClasses.Tag(1234, 987, "Trial", " ", "ff0000"),
                ProjectClasses.Tag(1234, 986, "Issue", " ", "00ff00"),
                ProjectClasses.Tag(1234, 985, "To-do", " ", "0000ff"), 
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
            last_update=now,
            tasks=[],
            tags=[
                ProjectClasses.Tag(1234, 987, "Trial", " ", "ff0000"),
                ProjectClasses.Tag(1234, 986, "Issue", " ", "00ff00"),
                ProjectClasses.Tag(1234, 985, "To-do", " ", "0000ff"), 
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
        ),
        ProjectClasses.Project(
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
        ),
        ProjectClasses.Project(
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
        )
    ]

def load_projects_from_json():
    """Loads projects from projects.json, creating it with seed data if it doesn't exist."""
    if not os.path.exists(projects_json_path):
        initial_projects = get_initial_dummy_projects()
        save_projects_to_json(initial_projects)
        return initial_projects
    
    try:
        with open(projects_json_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            projects = []
            for item in raw_data:
                tags = [
                    ProjectClasses.Tag(
                        item["projectID"], 
                        t["tagID"], 
                        t["name"], 
                        t["desc"], 
                        t.get("textcolour", "#ffffff"),                # Fallback default text colour
                        t.get("bgcolour", t.get("colour", "#ff0000"))  # Fallback default bg colour
                    ) 
                    for t in item.get("tags", [])
                ]
                proj = ProjectClasses.Project(
                    projectID=item["projectID"],
                    name=item["name"],
                    desc=item["desc"],
                    time_create=item["time_create"],
                    last_update=item["last_update"],
                    tasks=item.get("tasks", []),
                    tags=tags,
                    icon=item["icon"],
                    progress=item["progress"],
                    deadline=item["deadline"]
                )
                projects.append(proj)
            return projects
    except (json.JSONDecodeError, IOError):
        return get_initial_dummy_projects()

def save_projects_to_json(projects_list):
    """Saves the current list of project objects into projects.json."""
    raw_data = []
    for proj in projects_list:
        tags_data = [{"tagID": t.tagID, "name": t.name, "desc": t.desc, "colour": t.colour} for t in proj.tags]
        raw_data.append({
            "projectID": proj.projectID,
            "name": proj.name,
            "desc": proj.desc,
            "time_create": proj.time_create,
            "last_update": proj.last_update,
            "tasks": proj.tasks,
            "tags": tags_data,
            "icon": proj.icon,
            "progress": proj.progress,
            "deadline": proj.deadline
        })
    
    try:
        with open(projects_json_path, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=4)
    except IOError as e:
        print(f"Error saving projects: {e}")

# Expose dummyProjects loaded dynamically from JSON
dummyProjects = load_projects_from_json()