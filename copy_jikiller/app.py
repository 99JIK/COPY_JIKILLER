import os
import itertools
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import threading
import time
import csv
import sys

# --- Local Module Imports ---
from .utils import Taskbar, load_settings, save_settings, is_system_dark_theme
from .logic import process_content, CLANG_AVAILABLE, JAVALANG_AVAILABLE
from .ui import DiffWindow, InfoWindow, CustomMessagebox, AddExtensionDialog, ManageExtensionsDialog
from .i18n import LANGUAGES

class PlagiarismCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔪 COPY_JIKILLER") # Name Change
        self.root.geometry("1050x800") 
        
        try:
            self.root.iconbitmap(os.path.join('resource', 'copy_jikiller.ico')) # Name Change
        except tk.TclError:
            print("Warning: Icon file ('resource/copy_jikiller.ico') not found or corrupted.")
            
        if sys.platform == "win32":
            self.taskbar = Taskbar(self.root)
        else:
            self.taskbar = None
            
        self.scan_start_time = 0
        self.stop_event = threading.Event()
        self.directory, self.files_content = None, {}
        
        self._load_settings_and_language()
        self._setup_ui()
        
    def _load_settings_and_language(self):
        # Load settings from file.
        self.settings = load_settings()
        lang_code = self.settings.get("language", "EN")
        self.language = tk.StringVar(value=lang_code)
        
    def _setup_ui(self):
        self.style = ttk.Style()
        default_font = "Segoe UI Variable" if sys.platform == "win32" else "Helvetica"
        self.root.option_add("*Font", (default_font, 10))
        
        self.theme_display_name = tk.StringVar()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        container = ttk.Frame(self.root, padding=(30, 25))
        container.pack(fill=BOTH, expand=YES)
        container.rowconfigure(3, weight=1) 
        container.columnconfigure(0, weight=1)

        self.change_language(initial_setup=True)

        self._create_header(container, default_font)
        self._create_controls(container)
        self._create_action_buttons(container)
        self._create_results_view(container)
        self._create_statusbar(container)
        
        self.update_ui_text()
        self.toggle_theme_styles()
        
    def _create_header(self, parent, font):
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        title_subframe = ttk.Frame(header_frame)
        title_subframe.grid(row=0, column=0, sticky="w")
        ttk.Label(title_subframe, text="🔪 COPY_JIKILLER", font=(font, 24, "bold")).pack(side=LEFT, anchor="center") # Name Change
        self.info_button = ttk.Button(title_subframe, text="?", command=self.show_info_window, bootstyle="link", padding=(2,0)) # Style Change
        self.info_button.pack(side=LEFT, padx=10, pady=(5,0), anchor="center")
        
        settings_subframe = ttk.Frame(header_frame)
        settings_subframe.grid(row=0, column=1, sticky="e")
        
        self.theme_label = ttk.Label(settings_subframe)
        self.theme_label.pack(side=LEFT, padx=(0,5))
        self.theme_selector = ttk.Combobox(settings_subframe, textvariable=self.theme_display_name, state="readonly", width=11)
        self.theme_selector.pack(side=LEFT, padx=5)
        self.theme_selector.bind("<<ComboboxSelected>>", self.change_theme)
        
        self.lang_label = ttk.Label(settings_subframe)
        self.lang_label.pack(side=LEFT, padx=(10,5))
        self.lang_selector = ttk.Combobox(settings_subframe, textvariable=self.language, values=list(LANGUAGES.keys()), state="readonly", width=5)
        self.lang_selector.pack(side=LEFT, padx=5)
        self.lang_selector.bind("<<ComboboxSelected>>", self.change_language)

    def _create_controls(self, parent):
        self.controls_frame = ttk.Frame(parent)
        self.controls_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.controls_frame.columnconfigure((0, 1, 2), weight=1, uniform="group1")

        folder_frame = ttk.Labelframe(self.controls_frame, padding=15)
        folder_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.folder_title_label = ttk.Label(folder_frame, font="-weight bold")
        self.folder_title_label.pack(fill=X, pady=(0,10), anchor="w")
        self.select_button = ttk.Button(folder_frame, command=self.select_folder)
        self.select_button.pack(fill=X, pady=(0, 10))
        self.folder_label = ttk.Label(folder_frame, wraplength=250, justify=LEFT)
        self.folder_label.pack(fill=X, anchor="w")

        analysis_frame = ttk.Labelframe(self.controls_frame, padding=15)
        analysis_frame.grid(row=0, column=1, sticky="nsew", padx=10)
        self.analysis_title_label = ttk.Label(analysis_frame, font="-weight bold")
        self.analysis_title_label.pack(fill=X, pady=(0,10), anchor="w")
        self.analysis_mode_display_name = tk.StringVar()
        self.mode_selector = ttk.Combobox(analysis_frame, textvariable=self.analysis_mode_display_name, state="readonly")
        self.mode_selector.pack(fill=X, pady=(0, 10))
        self.recursive_var = tk.BooleanVar(value=True)
        self.recursive_check = ttk.Checkbutton(analysis_frame, variable=self.recursive_var)
        self.recursive_check.pack(fill=X, anchor="w")
        
        filter_frame = ttk.Labelframe(self.controls_frame, padding=15)
        filter_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 0))
        self.filter_title_label = ttk.Label(filter_frame, font="-weight bold")
        self.filter_title_label.pack(fill=X, pady=(0,10), anchor="w")
        
        ext_frame = ttk.Frame(filter_frame)
        ext_frame.pack(fill=X, pady=(0,10))
        self.extensions_menu = ttk.Menubutton(ext_frame, bootstyle="outline-secondary")
        self.extensions_menu.pack(side=LEFT, fill=X, expand=YES)
        
        ext_button_frame = ttk.Frame(ext_frame)
        ext_button_frame.pack(side=LEFT, padx=(5,0))
        add_ext_button = ttk.Button(ext_button_frame, text="➕", command=self.add_extension, width=2, bootstyle="outline-secondary")
        add_ext_button.pack(side=LEFT)
        manage_ext_button = ttk.Button(ext_button_frame, text="...", command=self.manage_extensions, width=2, bootstyle="outline-secondary")
        manage_ext_button.pack(side=LEFT, padx=(5,0))
        
        self.extension_vars = {ext: tk.BooleanVar(value=is_checked) for ext, is_checked in self.settings.get("extensions", {}).items()}
        self._build_extensions_menu()
        
        threshold_frame = ttk.Frame(filter_frame)
        threshold_frame.pack(fill=X)
        self.threshold_prefix_label = ttk.Label(threshold_frame)
        self.threshold_prefix_label.pack(side=LEFT)
        self.threshold_var = tk.DoubleVar(value=70)
        self.threshold_scale = ttk.Scale(threshold_frame, from_=0, to=100, variable=self.threshold_var, orient=HORIZONTAL, command=lambda e: self.threshold_value_label.config(text=f"{int(self.threshold_var.get())}%"))
        self.threshold_scale.pack(side=LEFT, fill=X, expand=YES, padx=5)
        self.threshold_value_label = ttk.Label(threshold_frame, text="70%", font="-size 11 -weight bold", width=4)
        self.threshold_value_label.pack(side=LEFT)
        
    def _create_action_buttons(self, parent):
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=2, column=0, sticky="ew", pady=(20, 10))
        action_frame.columnconfigure(0, weight=1)
        buttons_subframe = ttk.Frame(action_frame)
        buttons_subframe.grid(row=0, column=0, sticky="e")
        self.scan_button = ttk.Button(buttons_subframe, command=self.start_scan_thread, state=DISABLED, padding=(10,5))
        self.scan_button.pack(side=LEFT, padx=(0,10))
        self.stop_button = ttk.Button(buttons_subframe, command=self.stop_scan, state=DISABLED, padding=(10,5))
        self.stop_button.pack(side=LEFT, padx=(0,10))
        self.export_button = ttk.Button(buttons_subframe, command=self.export_to_csv, bootstyle="info", padding=(10,5), state=DISABLED)
        self.export_button.pack(side=LEFT)
        
    def _create_results_view(self, parent):
        result_frame = ttk.Frame(parent)
        result_frame.grid(row=3, column=0, sticky="nsew")
        result_frame.rowconfigure(0, weight=1); result_frame.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(result_frame, columns=("File1", "File2", "Similarity"), show='headings', bootstyle="secondary", height=15)
        self.tree.bind("<Double-1>", self.on_item_double_click)
        tree_scrollbar = ttk.Scrollbar(result_frame, orient=VERTICAL, command=self.tree.yview, bootstyle="secondary-round")
        self.tree.configure(yscroll=tree_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew"); tree_scrollbar.grid(row=0, column=1, sticky="ns")

    def _create_statusbar(self, parent):
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row=4, column=0, sticky="ew", pady=(15, 0))
        bottom_frame.columnconfigure(0, weight=1)
        self.progress_text_var = tk.StringVar()
        self.status_label = ttk.Label(bottom_frame, textvariable=self.progress_text_var, anchor=W); self.status_label.grid(row=0, column=0, sticky="ew")
        self.progress_bar = ttk.Progressbar(bottom_frame, mode='determinate'); self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5,0))
    
    def on_closing(self):
        self.settings["extensions"] = {ext: var.get() for ext, var in self.extension_vars.items()}
        save_settings(self.settings)
        self.root.destroy()
        
    def change_theme(self, event=None):
        display_name = self.theme_display_name.get()
        internal_name = next((k for k, v in self.theme_name_map.items() if v == display_name), "superhero")
        self.settings["theme"] = internal_name
        self.toggle_theme_styles()

    def change_language(self, event=None, initial_setup=False):
        lang_code = self.language.get()
        self.settings["language"] = lang_code
        self.texts = LANGUAGES.get(lang_code, LANGUAGES["EN"])
        if not initial_setup:
            self.update_ui_text()
            self.toggle_theme_styles()

    def update_ui_text(self):
        self.theme_name_map = self.texts["theme_display_names"]
        self.theme_selector["values"] = list(self.theme_name_map.values())
        current_theme_key = self.settings.get("theme", "superhero")
        self.theme_display_name.set(self.theme_name_map.get(current_theme_key, "Dark"))
        
        self.analysis_map = self.texts["analysis_mode_display_names"]
        available_modes = ["text", "python"]
        if CLANG_AVAILABLE: available_modes.append("c")
        if JAVALANG_AVAILABLE: available_modes.append("java")
        display_options = [self.analysis_map[key] for key in available_modes]
        self.mode_selector["values"] = display_options
        
        current_internal_mode = self.get_internal_analysis_mode()
        self.analysis_mode_display_name.set(self.analysis_map.get(current_internal_mode, display_options[0]))

        self.theme_label.config(text=self.texts["theme_label"]); self.lang_label.config(text=self.texts["lang_label"])
        self.folder_title_label.config(text=self.texts["folder_title"]); self.select_button.config(text=self.texts["select_button"])
        self.folder_label.config(text=self.texts["folder_label"]); self.analysis_title_label.config(text=self.texts["analysis_title"])
        self.recursive_check.config(text=self.texts["recursive_check"]); self.filter_title_label.config(text=self.texts["filter_title"])
        self.extensions_menu.config(text=self.texts["extensions_menu"]); self.threshold_prefix_label.config(text=self.texts["threshold_prefix_label"])
        self.scan_button.config(text=self.texts["scan_button"]); self.stop_button.config(text=self.texts["stop_button"])
        self.export_button.config(text=self.texts["export_button"]); self.progress_text_var.set(self.texts["status_ready"])
        self.tree.heading("File1", text=self.texts["tree_file1"]); self.tree.heading("File2", text=self.texts["tree_file2"]); self.tree.heading("Similarity", text=self.texts["tree_similarity"])
        self._build_extensions_menu() 

    def toggle_theme_styles(self):
        display_name = self.theme_display_name.get()
        internal_theme_name = next((k for k, v in self.theme_name_map.items() if v == display_name), 'superhero')
        self.style.theme_use(internal_theme_name)
        
        is_dark = internal_theme_name == 'superhero'
        scan_style = "danger" if is_dark else "primary"
        stop_style = "light-outline" if is_dark else "danger-outline"
        button_style = "light" if is_dark else "primary"

        self.scan_button.config(bootstyle=scan_style); self.stop_button.config(bootstyle=stop_style); self.progress_bar.config(bootstyle=f"{scan_style}-striped")
        self.recursive_check.config(bootstyle=f"{scan_style}-round-toggle"); self.threshold_scale.config(bootstyle=scan_style); self.select_button.config(bootstyle=button_style)
        self.info_button.config(bootstyle="link")

    def show_info_window(self):
        InfoWindow(self.root, self.texts)
    
    def on_item_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id: return
        item_values = self.tree.item(item_id, "values")
        file1_name, file2_name = item_values[0], item_values[1]
        content1, content2 = self.files_content.get(file1_name, ""), self.files_content.get(file2_name, "")
        DiffWindow(self.root, os.path.join(self.directory, file1_name), os.path.join(self.directory, file2_name), content1, content2)

    def select_folder(self):
        title = self.texts.get("dialog_select_folder", "Select Folder")
        directory = filedialog.askdirectory(title=title)
        if directory:
            self.directory = directory
            self.scan_button.config(state=NORMAL)
            self.folder_label.config(text=f"{self.texts['folder_prefix']}: {directory}")
            self.extensions_menu.config(state=DISABLED)
            self.recursive_check.config(state=DISABLED)
            try:
                extensions = [ext for ext, var in self.extension_vars.items() if var.get()]
                file_count = len(self._get_files_from_directory(self.directory, extensions, self.recursive_var.get()))
                self.progress_text_var.set(self.texts["status_file_count"].format(count=file_count))
            except Exception as e:
                self.progress_text_var.set(self.texts["status_error_reading"].format(error=e))
                
    def add_extension(self):
        dialog = AddExtensionDialog(self.root, self.texts)
        self.root.wait_window(dialog)
        new_ext = dialog.result
        if new_ext and new_ext not in self.extension_vars:
            self.extension_vars[new_ext] = tk.BooleanVar(value=True)
            self._build_extensions_menu()
            
    def manage_extensions(self):
        dialog = ManageExtensionsDialog(self.root, self.texts, self.extension_vars)
        self.root.wait_window(dialog)
        if dialog.deleted_extensions:
            for ext in dialog.deleted_extensions:
                del self.extension_vars[ext]
            self._build_extensions_menu()

    def _build_extensions_menu(self):
        menu = tk.Menu(self.extensions_menu, tearoff=0)
        self.all_extensions_var = tk.BooleanVar(value=all(self.extension_vars.values()))
        menu.add_checkbutton(label=self.texts.get("all_files", "All Files (*.*)"), variable=self.all_extensions_var, command=self._on_toggle_all_extensions)
        menu.add_separator()
        for ext, var in self.extension_vars.items():
            menu.add_checkbutton(label=ext, variable=var, command=self._on_toggle_extension)
        self.extensions_menu['menu'] = menu

    def _on_toggle_all_extensions(self):
        for var in self.extension_vars.values(): var.set(self.all_extensions_var.get())
            
    def _on_toggle_extension(self):
        self.all_extensions_var.set(all(var.get() for var in self.extension_vars.values()))

    def export_to_csv(self):
        title = self.texts.get("dialog_export_csv", "Export Results")
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")], title=title)
        if not filepath: return
        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f); writer.writerow([self.texts["tree_file1"], self.texts["tree_file2"], self.texts["tree_similarity"]])
                for item_id in self.tree.get_children(): writer.writerow(self.tree.item(item_id, "values"))
            CustomMessagebox(self.root, self.texts, self.texts["dialog_export_success"].format(file=os.path.basename(filepath)), title_key="dialog_success_title", bootstyle="success")
        except Exception as e:
            CustomMessagebox(self.root, self.texts, self.texts["dialog_export_error"].format(error=e), title_key="dialog_error_title", bootstyle="error")

    def start_scan_thread(self):
        if not self.directory:
            CustomMessagebox(self.root, self.texts, self.texts["dialog_no_folder"], title_key="dialog_warning_title", bootstyle="warning"); return
            
        for i in self.tree.get_children(): self.tree.delete(i)
        
        self.scan_button.config(state=DISABLED); self.stop_button.config(state=NORMAL)
        self.select_button.config(state=DISABLED); self.export_button.config(state=DISABLED)
        self.mode_selector.config(state=DISABLED); self.extensions_menu.config(state=DISABLED); self.recursive_check.config(state=DISABLED)
        
        self.progress_bar['value'], self.scan_start_time = 0, 0
        self.stop_event.clear()
        if self.taskbar: self.taskbar.setProgressState(self.taskbar.TBPF_NORMAL)
        
        threading.Thread(target=self.run_scan, daemon=True).start()
        
    def stop_scan(self):
        self.stop_event.set(); self.stop_button.config(state=DISABLED)

    def get_internal_analysis_mode(self):
        selected_display_name = self.analysis_mode_display_name.get()
        return next((k for k, v in self.analysis_map.items() if v == selected_display_name), 'text')

    def run_scan(self):
        try:
            extensions = [ext for ext, var in self.extension_vars.items() if var.get()]
            self.files_content = self._get_files_from_directory(self.directory, extensions, self.recursive_var.get())
            
            if len(self.files_content) < 2:
                self.root.after(0, lambda: CustomMessagebox(self.root, self.texts, self.texts["status_no_files"], title_key="dialog_info_title", bootstyle="info"))
                self.root.after(0, self.scan_finished, False); return

            comparisons, file_pairs = [], list(itertools.combinations(self.files_content.keys(), 2))
            total_comparisons, mode = len(file_pairs), self.get_internal_analysis_mode()
            self.progress_bar['maximum'] = total_comparisons
            
            self.root.after(0, self.update_progress, 0, total_comparisons)
            self.scan_start_time = time.time()

            for i, (file1_name, file2_name) in enumerate(file_pairs):
                if self.stop_event.is_set(): self.root.after(0, self.scan_finished, True); return
                
                content1, content2 = self.files_content[file1_name], self.files_content[file2_name]
                similarity = process_content(content1, content2, mode)
                comparisons.append((similarity, file1_name, file2_name))
                self.root.after(0, self.update_progress, i + 1, total_comparisons)
            
            comparisons.sort(reverse=True)
            self.root.after(0, self.update_results, comparisons)
        except Exception as e:
            self.root.after(0, lambda: CustomMessagebox(self.root, self.texts, self.texts["dialog_scan_error"].format(error=e), title_key="dialog_error_title", bootstyle="error"))
        finally:
             if not self.stop_event.is_set():
                self.root.after(0, self.scan_finished, False)
             
    def update_progress(self, current, total):
        self.progress_bar['value'] = current
        if self.taskbar: self.taskbar.setProgressValue(current, total)
        progress_percent = (current / total) * 100 if total > 0 else 0
        
        if current > 0 and self.scan_start_time > 0:
            elapsed_time = time.time() - self.scan_start_time
            eta_seconds = (elapsed_time / current) * (total - current)
            eta_str = f"{int(eta_seconds // 60)}m {int(eta_seconds % 60)}s"
            self.progress_text_var.set(self.texts["status_scanning"].format(percent=progress_percent, current=current, total=total, eta=eta_str))
        elif total > 0:
             self.progress_text_var.set(self.texts["status_file_count"].format(count=len(self.files_content), total=total))
        else:
            self.progress_text_var.set(self.texts["status_no_files"])
            
    def update_results(self, comparisons):
        threshold = self.threshold_var.get() / 100
        for similarity, file1, file2 in comparisons:
            if similarity >= threshold:
                self.tree.insert("", END, values=(file1, file2, f"{similarity * 100:.2f}"))
        if self.tree.get_children():
            self.export_button.config(state=NORMAL)

    def scan_finished(self, was_cancelled):
        self.scan_button.config(state=NORMAL); self.select_button.config(state=NORMAL); self.stop_button.config(state=DISABLED)
        self.mode_selector.config(state="readonly"); self.extensions_menu.config(state=NORMAL); self.recursive_check.config(state=NORMAL)
        
        if self.taskbar:
            if was_cancelled: self.taskbar.setProgressState(self.taskbar.TBPF_PAUSED)
            else: self.taskbar.setProgressState(self.taskbar.TBPF_NOPROGRESS)
        
        self.progress_text_var.set(self.texts["status_scan_cancelled"] if was_cancelled else self.texts["status_scan_done"])
        
    def _get_files_from_directory(self, directory, extensions, recursive):
        file_data = {}
        if not extensions: 
            return file_data 
            
        if recursive:
            for dirpath, _, filenames in os.walk(directory):
                for filename in filenames:
                    if not filename.startswith('.') and (any(filename.endswith(ext) for ext in extensions)):
                        filepath = os.path.join(dirpath, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                file_data[os.path.relpath(filepath, directory)] = f.read()
                        except Exception as e: print(f"File read error '{filepath}': {e}")
        else:
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath) and not filename.startswith('.') and (any(filename.endswith(ext) for ext in extensions)):
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: file_data[filename] = f.read()
                    except Exception as e: print(f"File read error '{filename}': {e}")
        return file_data
