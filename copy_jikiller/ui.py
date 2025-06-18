import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame
import difflib
import os
import sys

# Pillow library import for image processing
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: Pillow library is not installed. Banner image resizing will be disabled.")
    print("You can install it by running: pip install Pillow")

# --- Local Module Imports ---
# This structure assumes ui.py is inside the 'copy_jikiller' package
try:
    from .utils import resource_path
except ImportError:
    # Fallback for running the file directly (if needed for testing)
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)


class BaseToplevel(tk.Toplevel):
    """A base class for all Toplevel windows to handle common setup."""
    def __init__(self, parent, title=""):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        try:
            icon_path = resource_path(os.path.join('resource', 'copy_jikiller.ico'))
            self.iconbitmap(icon_path)
        except tk.TclError:
            print(f"Warning: Icon for window '{title}' not found.")

class DiffWindow(BaseToplevel):
    """A Toplevel window to display a side-by-side comparison of two files."""
    def __init__(self, parent, file1_path, file2_path, file1_content, file2_content):
        super().__init__(parent, f"Compare: {os.path.basename(file1_path)} vs {os.path.basename(file2_path)}")
        self.geometry("1200x800")
        
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=BOTH, expand=YES)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text=os.path.basename(file1_path), font="-weight bold").grid(row=0, column=0, sticky="ew", pady=5)
        ttk.Label(main_frame, text=os.path.basename(file2_path), font="-weight bold").grid(row=0, column=1, sticky="ew", pady=5)

        style = ttk.Style()
        current_theme = style.theme_use()
        
        theme_colors = {
            'superhero': {'bg': '#2B3E50', 'fg': '#FFFFFF', 'match_bg': '#660000'},
            'litera': {'bg': '#FFFFFF', 'fg': '#000000', 'match_bg': '#D6EAF8'}
        }
        colors = theme_colors.get(current_theme, theme_colors['superhero'])
        
        self.text1 = tk.Text(main_frame, wrap=WORD, relief="flat", background=colors['bg'], foreground=colors['fg'], font=("Consolas", 10))
        self.text2 = tk.Text(main_frame, wrap=WORD, relief="flat", background=colors['bg'], foreground=colors['fg'], font=("Consolas", 10))
        self.text1.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        self.text2.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        scrollbar = ttk.Scrollbar(main_frame, orient=VERTICAL, command=self._on_scroll)
        scrollbar.grid(row=1, column=2, sticky="ns")
        self.text1.config(yscrollcommand=scrollbar.set)
        self.text2.config(yscrollcommand=scrollbar.set)
        
        self.text1.bind("<MouseWheel>", self._on_mouse_wheel)
        self.text2.bind("<MouseWheel>", self._on_mouse_wheel)

        self.text1.insert(END, file1_content)
        self.text2.insert(END, file2_content)
        
        self.highlight_diff(file1_content, file2_content, colors['match_bg'])
        
        self.text1.config(state=DISABLED)
        self.text2.config(state=DISABLED)

    def _on_scroll(self, *args):
        # Synchronize scrolling of both text widgets.
        self.text1.yview(*args)
        self.text2.yview(*args)

    def _on_mouse_wheel(self, event):
        # Cross-platform mouse wheel scrolling.
        if sys.platform == "darwin":
            delta = event.delta
        else:
            delta = int(-1*(event.delta/120))
            
        self.text1.yview_scroll(delta, "units")
        self.text2.yview_scroll(delta, "units")
        return "break" 

    def highlight_diff(self, content1, content2, match_bg_color):
        # Highlight matching lines in both text widgets.
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
        self.text1.tag_config('match', background=match_bg_color)
        self.text2.tag_config('match', background=match_bg_color)
        d = difflib.SequenceMatcher(None, lines1, lines2)
        for tag, i1, i2, j1, j2 in d.get_opcodes():
            if tag == 'equal':
                for i in range(i1, i2):
                    self.text1.tag_add('match', f"{i + 1}.0", f"{i + 1}.end")
                for j in range(j1, j2):
                    self.text2.tag_add('match', f"{j + 1}.0", f"{j + 1}.end")


class InfoWindow(BaseToplevel):
    """A Toplevel window to display information about the application."""
    def __init__(self, parent, texts):
        super().__init__(parent, texts.get("info_title", "Info"))
        self.geometry("700x650")
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=BOTH, expand=YES)
        
        self.canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        
        self.content_frame = ttk.Frame(self.canvas, padding=25)
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

        # BUG FIX: Bind mouse wheel to the Toplevel window itself, not the canvas.
        self.bind_all("<MouseWheel>", self._on_mouse_wheel, add="+")
        self.bind("<Destroy>", self._on_destroy)

        self._populate_content(texts)
        self.canvas.bind("<Configure>", self._on_resize) 

    def _populate_content(self, texts):
        self.banner_label = ttk.Label(self.content_frame)
        self.banner_label.pack(pady=(0, 25), anchor="center")
        self.after(50, self._load_and_resize_banner)

        inner_content_frame = ttk.Frame(self.content_frame, padding=(25,0))
        inner_content_frame.pack(fill=X)

        ttk.Label(inner_content_frame, text=texts.get("info_usage_title", "How to Use"), font="-size 14 -weight bold").pack(fill=X, pady=(0, 10), anchor="w")
        ttk.Label(inner_content_frame, text=texts.get("info_usage_text", ""), justify=LEFT, wraplength=600).pack(fill=X, anchor="w", pady=(0, 25))
        
        ttk.Label(inner_content_frame, text=texts.get("info_ast_title", "What is AST?"), font="-size 14 -weight bold").pack(fill=X, pady=(0, 10), anchor="w")
        ttk.Label(inner_content_frame, text=texts.get("info_ast_text", ""), justify=LEFT, wraplength=600).pack(fill=X, anchor="w", pady=(0, 25))
        
        ttk.Label(inner_content_frame, text=texts.get("info_dev_title", "Information"), font="-size 14 -weight bold").pack(fill=X, pady=(0, 10), anchor="w")
        ttk.Label(inner_content_frame, text=texts.get("info_dev_text", ""), justify=LEFT).pack(fill=X, anchor="w")

    def _load_and_resize_banner(self, event_width=None):
        try:
            if not PIL_AVAILABLE: raise FileNotFoundError
            image_path = resource_path(os.path.join('resource', 'copy_jikiller.png'))
            self.original_image = Image.open(image_path)
            
            max_width = (event_width or self.canvas.winfo_width()) - 50 
            if max_width <= 20: return 
            aspect_ratio = self.original_image.height / self.original_image.width
            new_width = max_width
            new_height = int(new_width * aspect_ratio)
            if new_width <= 0 or new_height <= 0: return

            resized_image = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.banner_image_tk = ImageTk.PhotoImage(resized_image)
            self.banner_label.config(image=self.banner_image_tk)
        except Exception as e:
            print(f"Error processing banner image: {e}")
            self.banner_label.config(text="COPY_JIKILLER", font="-size 18 -weight bold")

    def _on_resize(self, event):
        self.canvas.itemconfig(self.canvas_frame_id, width=event.width)
        self._load_and_resize_banner(event.width)
        
    def _on_mouse_wheel(self, event):
        if sys.platform == "darwin": delta = event.delta
        else: delta = int(-1*(event.delta/120))
        self.canvas.yview_scroll(delta, "units")
        
    def _on_destroy(self, event):
        if event.widget == self:
            self.unbind_all("<MouseWheel>")

class CustomMessagebox(BaseToplevel):
    def __init__(self, parent, texts, message, title_key="dialog_info_title", bootstyle="info", alert=False):
        super().__init__(parent, texts.get(title_key, "Info"))

        if alert: self.bell()

        main_frame = ttk.Frame(self, padding=25)
        main_frame.pack(expand=YES, fill=BOTH)
        main_frame.columnconfigure(1, weight=1) 

        icon_map = {'info': 'ℹ️', 'warning': '⚠️', 'error': '❗', 'success': '✔️'}
        icon_char = icon_map.get(bootstyle, 'info')
        
        icon_label = ttk.Label(main_frame, text=icon_char, font="-size 24", bootstyle=bootstyle)
        icon_label.grid(row=0, column=0, padx=(0, 15), pady=10, sticky='n')
        
        message_label = ttk.Label(main_frame, text=message, wraplength=300, justify=LEFT)
        message_label.grid(row=0, column=1, pady=10, sticky='w')

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(15, 0))
        
        ok_button = ttk.Button(button_frame, text=texts.get("dialog_ok", "OK"), command=self.destroy, bootstyle=bootstyle, width=10)
        ok_button.pack()
        
        self.after(10, self._center_window)
        self.resizable(False, False)

    def _center_window(self):
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

class AddExtensionDialog(BaseToplevel):
    def __init__(self, parent, texts):
        super().__init__(parent, texts.get("dialog_add_ext_title", "Add Extension"))
        self.result = None
        self.texts = texts

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=X)
        
        ttk.Label(main_frame, text=texts.get("dialog_add_ext_label", "Enter new extension:")).pack(pady=5)
        self.entry = ttk.Entry(main_frame)
        self.entry.pack(fill=X, pady=5)
        self.entry.focus_set()
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        add_button = ttk.Button(button_frame, text=texts.get("dialog_add", "Add"), command=self._on_add)
        add_button.pack(side=LEFT, padx=5)
        cancel_button = ttk.Button(button_frame, text=texts.get("dialog_cancel", "Cancel"), command=self.destroy, bootstyle="outline")
        cancel_button.pack(side=LEFT, padx=5)

        self.after(10, self._center_window)
        self.resizable(False, False)
        self.bind("<Return>", self._on_add)

    def _on_add(self, event=None):
        value = self.entry.get().strip()
        if value and value.startswith("."):
            self.result = value
            self.destroy()
        else:
            CustomMessagebox(self, self.texts, self.texts.get("dialog_invalid_ext_msg"), title_key="dialog_invalid_input_title", bootstyle="error")

    def _center_window(self):
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

class ManageExtensionsDialog(BaseToplevel):
    def __init__(self, parent, texts, extension_vars):
        super().__init__(parent, texts.get("dialog_manage_ext_title", "Manage Extensions"))
        self.deleted_extensions = []
        
        self.default_extensions = {".py", ".c", ".cpp", ".java"}
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        
        ttk.Label(main_frame, text=texts.get("dialog_manage_ext_label", "Select extensions to delete:")).pack(pady=5, anchor="w")
        
        list_frame = ScrolledFrame(main_frame, autohide=True)
        list_frame.pack(fill=BOTH, expand=YES, pady=5)
        
        self.check_vars = {}
        has_deletable = False
        for ext in extension_vars:
            if ext not in self.default_extensions:
                has_deletable = True
                var = tk.BooleanVar()
                cb = ttk.Checkbutton(list_frame.container, text=ext, variable=var)
                cb.pack(anchor="w", padx=10, pady=2)
                self.check_vars[ext] = var
        
        if not has_deletable:
            ttk.Label(list_frame.container, text=texts.get("dialog_no_custom_ext", "No custom extensions to delete.")).pack(padx=10, pady=10)

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        delete_button = ttk.Button(button_frame, text=texts.get("dialog_delete_button", "Delete Selected"), command=self._on_delete, bootstyle="danger")
        delete_button.pack(side=LEFT, padx=5)
        if not has_deletable: delete_button.config(state=DISABLED)
        
        cancel_button = ttk.Button(button_frame, text=texts.get("dialog_cancel_button", "Cancel"), command=self.destroy, bootstyle="outline")
        cancel_button.pack(side=LEFT, padx=5)

        self.after(10, self._center_window)

    def _on_delete(self):
        self.deleted_extensions = [ext for ext, var in self.check_vars.items() if var.get()]
        if not self.deleted_extensions:
            return
        self.destroy()

    def _center_window(self):
        self.update_idletasks()
        parent = self.master
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
