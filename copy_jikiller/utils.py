import sys
import os
import json

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    import winreg

    class Taskbar:
        """A class to control the Windows Taskbar progress bar."""
        def __init__(self, root):
            self.root = root
            self.TBPF_NOPROGRESS, self.TBPF_NORMAL, self.TBPF_PAUSED, self.TBPF_ERROR = 0, 2, 8, 4
            try:
                self.taskbar = ctypes.WinDLL('ole32').CoCreateInstance(
                    wintypes.GUID('{56FDF344-FD6D-11d0-958A-006097C9A090}'), None,
                    ctypes.POINTER(ctypes.c_int)(),
                    wintypes.GUID('{ea1afb91-9e28-4b86-90e9-9e9f8a5eefaf}')
                )
            except Exception as e:
                self.taskbar = None
                print(f"Failed to create Taskbar controller: {e}")

        def setProgressState(self, state):
            if self.taskbar:
                try: self.taskbar.SetProgressState(self.root.winfo_id(), state)
                except Exception as e: print(f"Failed to set taskbar state: {e}")
        def setProgressValue(self, current, total):
            if self.taskbar and total > 0:
                try: self.taskbar.SetProgressValue(self.root.winfo_id(), current, total)
                except Exception as e: print(f"Failed to set taskbar value: {e}")

    def is_system_dark_theme():
        """Checks if the Windows system is using a dark theme."""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
            value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
            return value == 0
        except Exception:
            return True 
else:
    # Dummy class for non-Windows systems
    class Taskbar:
        def __init__(self, root): pass
        def setProgressState(self, state): pass
        def setProgressValue(self, current, total): pass
    def is_system_dark_theme():
        return True 

SETTINGS_FILE = "settings.json"

def load_settings():
    """Loads settings from settings.json and validates them."""
    default_settings = {
        "language": "EN", 
        "theme": "superhero", 
        "extensions": {".py": True, ".c": True, ".cpp": True, ".java": True, ".*": True}
    }
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            # --- Defensive coding for extensions ---
            if "extensions" not in settings or not isinstance(settings["extensions"], dict):
                settings["extensions"] = default_settings["extensions"]
            # --- Defensive coding for theme ---
            if settings.get("theme") not in ["superhero", "litera"]:
                settings["theme"] = default_settings["theme"]
            return settings
    except (FileNotFoundError, json.JSONDecodeError):
        return default_settings

def save_settings(settings):
    """Saves the given settings dictionary to settings.json."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")

def find_libclang_path():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
        lib_path = os.path.join(bundle_dir, 'libclang.dll')
        if os.path.exists(lib_path): return lib_path
    llvm_path = r'C:\Program Files\LLVM\bin\libclang.dll'
    if os.path.exists(llvm_path): return llvm_path
    from shutil import which
    if which('clang'): return which('clang')
    return None

def configure_clang(clang_module):
    if clang_module and not clang_module.cindex.Config.loaded:
        libclang_path = find_libclang_path()
        if libclang_path:
            clang_module.cindex.Config.set_library_file(libclang_path)
            return True
        else:
            return False
    return clang_module is not None and clang_module.cindex.Config.loaded
