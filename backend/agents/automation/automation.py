import os
from glob import glob
import subprocess
from rapidfuzz.process import extractOne
from rapidfuzz.fuzz import ratio


def get_desktop_apps():
    # Common Linux application paths
    desktop_paths = [
        "/usr/share/applications/*.desktop",                    # System-wide applications
        "/usr/local/share/applications/*.desktop",              # Local system applications
        "~/.local/share/applications/*.desktop",                # User applications
        "/var/lib/snapd/desktop/applications/*.desktop",        # Snap applications
        "/var/lib/flatpak/exports/share/applications/*.desktop", # Flatpak applications
        "~/.local/share/flatpak/exports/share/applications/*.desktop", # User Flatpak applications
        "/opt/*/share/applications/*.desktop",                  # Applications in /opt
        "/usr/share/applications/kde4/*.desktop",               # KDE4 applications
        "/usr/share/applications/kde5/*.desktop",               # KDE5 applications
        "/usr/share/applications/gnome/*.desktop",              # GNOME applications
        "/usr/share/applications/xfce4/*.desktop",              # XFCE applications
        "/snap/*/current/meta/gui/*.desktop",                   # Snap applications (alternative path)
    ]
    
    # Expand all paths and collect desktop files
    desktop_files = []
    for path in desktop_paths:
        expanded_path = os.path.expanduser(path)
        found_files = glob(expanded_path)
        if found_files:
            print(f"Found files in {expanded_path}:")
        desktop_files.extend(found_files)
    
    apps = {}
    for file in desktop_files:
        try:
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            name, exec_cmd = None, None
            for line in lines:
                if line.startswith("Name="):
                    name = line[5:].strip().lower()
                if line.startswith("Exec="):
                    exec_cmd = line[5:].strip().split(" ")[0]
            if name and exec_cmd:
                apps[name] = exec_cmd
        except (IOError, PermissionError) as e:
            print(f"Warning: Could not read {file}: {e}")
            continue
            
    return apps

def open_app(app_name):
    apps = get_desktop_apps()
    app = extractOne(app_name, apps.keys(), scorer=ratio, score_cutoff=70)
    if app:
        matched_name, score, _ = app
        print(f"Matched '{app_name}' to '{matched_name}' with score {score}")
        
        # Set up environment variables to reduce warnings
        env = os.environ.copy()
        env.update({
            'GTK_MODULES': '',  # Disable GTK modules to reduce warnings
            'QT_LOGGING_RULES': '*.debug=false',  # Reduce Qt debug output
            'QT_ACCESSIBILITY': '0',  # Disable accessibility to reduce warnings
        })
        
        try:
            # Use subprocess.Popen with environment variables and redirect stderr
            process = subprocess.Popen(
                [apps[matched_name]],
                env=env,
                stderr=subprocess.DEVNULL,  # Suppress error messages
                stdout=subprocess.DEVNULL,  # Suppress output
                start_new_session=True  # Run in new session to prevent terminal from being affected
            )
            return True
        except Exception as e:
            print(f"Error launching application: {e}")
            return False
    else:
        print(f"Could not find application: {app_name}")
        return False

# open_app("telegrm")
# get_desktop_apps()