import ttkbootstrap as ttk
from copy_jikiller.app import PlagiarismCheckerApp
from copy_jikiller.utils import load_settings
import sys

if __name__ == "__main__":
    # Load settings to determine the initial theme
    settings = load_settings()
    initial_theme = settings.get("theme", "superhero")
    
    # Create the main window with the correct initial theme
    root = ttk.Window(themename=initial_theme)
    app = PlagiarismCheckerApp(root)
    root.mainloop()