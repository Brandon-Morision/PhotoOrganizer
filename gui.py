# gui.py
import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from ttkbootstrap import Style
from ttkbootstrap.constants import *

from organizer import PhotoOrganizer, SUPPORTED_EXTENSIONS 


# --- Tooltip Class (Integrated for robustness) ---
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.x = 0
        self.y = 0
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave) # Hide on click

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.show) # Show after 500ms

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

    def show(self):
        if self.tooltip_window or not self.text:
            return
        
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5 

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True) 
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes("-topmost", True) 

        label = ttk.Label(self.tooltip_window, text=self.text, background="#ffffe0",
                          relief=tk.SOLID, borderwidth=1, font=("Arial", 9, "normal"))
        label.pack(padx=5, pady=3)

    def hide(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# --- GUI Class ---
class PhotoOrganizerGUI:
    def __init__(self):
        self.app = tk.Tk()
        self.app.title("📁 Photo Organizer")
        self.app.geometry("700x800") 
        self.app.resizable(False, False)

        if os.path.exists("icon.ico"):
            self.app.iconbitmap("icon.ico")

        self.style = Style("superhero")
        self.style.master = self.app 

        self._create_widgets()

    def _create_widgets(self):
        # Main Title
        ttk.Label(self.app, text="Photo Organizer by Name/Date", font=("Segoe UI", 18, "bold"),
                  bootstyle="primary").pack(pady=15)

        # --- Folder Selection Frame ---
        folder_frame = ttk.LabelFrame(self.app, text="Folders", padding=(20, 10))
        folder_frame.pack(padx=20, pady=10, fill=X)

        # Source Folder
        ttk.Label(folder_frame, text="Source Folder:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.source_entry = ttk.Entry(folder_frame, width=60)
        self.source_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        browse_source_btn = ttk.Button(folder_frame, text="Browse", bootstyle="info-outline",
                                       command=lambda: self.browse_folder(self.source_entry))
        browse_source_btn.grid(row=0, column=2, padx=10, pady=5)
        Tooltip(browse_source_btn, "Select the folder containing your photos and videos.")

        # Destination Folder
        ttk.Label(folder_frame, text="Destination Folder:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.dest_entry = ttk.Entry(folder_frame, width=60)
        self.dest_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        browse_dest_btn = ttk.Button(folder_frame, text="Browse", bootstyle="info-outline",
                                     command=lambda: self.browse_folder(self.dest_entry))
        browse_dest_btn.grid(row=1, column=2, padx=10, pady=5)
        Tooltip(browse_dest_btn, "Select or create the folder where organized files will be placed.")
        
        folder_frame.grid_columnconfigure(1, weight=1) 

        # --- Organization Options Frame ---
        options_frame = ttk.LabelFrame(self.app, text="Organization Options", padding=(20, 10))
        options_frame.pack(padx=20, pady=10, fill=X)

        # Organization Mode
        ttk.Label(options_frame, text="Organize by:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.organization_mode_var = tk.StringVar(value="name") 
        name_rb = ttk.Radiobutton(options_frame, text="Name (e.g., 'EventName_001.jpg' -> 'EventName')",
                                  value="name", variable=self.organization_mode_var, bootstyle="info")
        name_rb.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        Tooltip(name_rb, "Organize into folders based on the filename prefix (e.g., 'MyTrip_123.jpg' -> 'MyTrip').")

        date_rb = ttk.Radiobutton(options_frame, text="Date (e.g., '2023/05' using EXIF/Mod Date)",
                                  value="date", variable=self.organization_mode_var, bootstyle="info")
        date_rb.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        Tooltip(date_rb, "Organize into folders based on the file's creation date (EXIF for images, modification date otherwise).")

        # Copy instead of Move
        self.copy_var = tk.BooleanVar()
        copy_checkbox = ttk.Checkbutton(options_frame, text="Copy files instead of Moving them",
                                        variable=self.copy_var, bootstyle="secondary")
        copy_checkbox.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")
        Tooltip(copy_checkbox, "If checked, files will be copied to the destination, leaving originals in the source folder.")


        # --- File Type Filters Frame ---
        filter_frame = ttk.LabelFrame(self.app, text="File Type Filters", padding=(20, 10))
        filter_frame.pack(padx=20, pady=10, fill=X)

        ttk.Label(filter_frame, text="Include these types:").grid(row=0, column=0, columnspan=5, padx=10, pady=5, sticky="w")

        self.file_type_vars = {}
        sorted_extensions = sorted(list(SUPPORTED_EXTENSIONS))
        
        col_count = 5 
        for i, ext in enumerate(sorted_extensions):
            var = tk.BooleanVar(value=True) 
            self.file_type_vars[ext] = var
            chk = ttk.Checkbutton(filter_frame, text=ext.upper(), variable=var, bootstyle="info")
            chk.grid(row=(i // col_count) + 1, column=i % col_count, padx=5, pady=2, sticky="w")
            Tooltip(chk, f"Include {ext.upper()} files in the organization process.")

        # Select/Deselect All buttons for filters
        select_all_btn = ttk.Button(filter_frame, text="Select All", bootstyle="light-outline", command=lambda: self._toggle_all_file_types(True))
        select_all_btn.grid(row=(len(sorted_extensions) // col_count) + 2, column=0, padx=5, pady=10, sticky="w")
        Tooltip(select_all_btn, "Select all supported file types.")

        deselect_all_btn = ttk.Button(filter_frame, text="Deselect All", bootstyle="light-outline", command=lambda: self._toggle_all_file_types(False))
        deselect_all_btn.grid(row=(len(sorted_extensions) // col_count) + 2, column=1, padx=5, pady=10, sticky="w")
        Tooltip(deselect_all_btn, "Deselect all supported file types.")


        # --- BOTTOM ELEMENTS: Footer, Control Buttons, Progress Bar, Log ---
        # Pack elements from bottom up, so they are guaranteed to be visible

        # Footer
        ttk.Label(self.app, text="Created with 🧠 using Python & ttkbootstrap", font=("Segoe UI", 9, "italic"),
                  bootstyle="info").pack(side=BOTTOM, pady=5)

        # Control Buttons
        control_buttons_frame = ttk.Frame(self.app, padding=10)
        control_buttons_frame.pack(side=BOTTOM, pady=10) # Pack to BOTTOM first

        self.organize_button = ttk.Button(control_buttons_frame, text="🧹 Organize Now", bootstyle="success", 
                                          width=20, command=self.start_organizing_process)
        self.organize_button.pack(side=LEFT, padx=10)
        Tooltip(self.organize_button, "Click to start the file organization process.")

        theme_toggle_btn = ttk.Button(control_buttons_frame, text="🌙 Toggle Theme", bootstyle="warning-outline",
                                      width=20, command=self.toggle_theme)
        theme_toggle_btn.pack(side=LEFT, padx=10)
        Tooltip(theme_toggle_btn, "Switch between light (Flatly) and dark (Superhero) themes.")

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.app, variable=self.progress_var, maximum=100, mode="determinate", length=600, bootstyle=INFO)
        self.progress_bar.pack(side=BOTTOM, pady=15, padx=20, fill=X) # Pack to BOTTOM, allow horizontal fill

        # Log Frame (This will now fill the remaining space above the fixed bottom elements)
        log_frame = ttk.Frame(self.app, padding=5)
        log_frame.pack(padx=20, pady=10, fill=BOTH, expand=True) # Will expand to fill remaining space

        self.log_box = tk.Text(log_frame, height=10, bg="#1e1e1e", fg="#c0c0c0", insertbackground="white",
                               font=("Consolas", 10), wrap=WORD, state=DISABLED) 
        self.log_box.pack(side=LEFT, fill=BOTH, expand=True)

        log_scrollbar = ttk.Scrollbar(log_frame, orient=VERTICAL, command=self.log_box.yview)
        log_scrollbar.pack(side=RIGHT, fill=Y)
        self.log_box.config(yscrollcommand=log_scrollbar.set)

        self.log_box.config(state=NORMAL) 
        self.log_box.insert(tk.END, "Log output will appear here...\n")
        self.log_box.config(state=DISABLED) 

    def _toggle_all_file_types(self, select_all: bool):
        """Helper to select or deselect all file type checkboxes."""
        for var in self.file_type_vars.values():
            var.set(select_all)

    def browse_folder(self, entry_widget):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, folder_selected)

    def toggle_theme(self):
        current_theme = self.style.theme_use()
        new_theme = "flatly" if current_theme == "superhero" else "superhero"
        self.style.theme_use(new_theme)

    def _update_log(self, message):
        """Callback to update the log_box from the background thread."""
        self.log_box.config(state=NORMAL) 
        self.log_box.insert(tk.END, message)
        self.log_box.see(tk.END) 
        self.log_box.config(state=DISABLED) 

    def _update_progress(self, value):
        """Callback to update the progress_bar from the background thread."""
        self.progress_var.set(value)

    def _on_organization_done(self, processed, skipped):
        """Callback to run in the main thread when organization is complete."""
        self.organize_button.config(state=NORMAL) 
        self.progress_var.set(0) 
        self.app.after(0, lambda: self._update_log("\nOrganization process finished.\n"))
        
        self.app.after(0, lambda: messagebox.showinfo("Done", f"Processed: {processed} file(s)\nSkipped: {skipped} file(s)"))

    def start_organizing_process(self):
        src = self.source_entry.get()
        dest = self.dest_entry.get()
        use_copy = self.copy_var.get()
        organization_mode = self.organization_mode_var.get()
        
        selected_extensions = {ext for ext, var in self.file_type_vars.items() if var.get()}
        
        if not selected_extensions:
            messagebox.showerror("Error", "Please select at least one file type to organize.")
            return

        if not os.path.isdir(src):
            messagebox.showerror("Error", f"Source folder does not exist:\n{src}")
            return
        
        files_in_source = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]
        if not files_in_source:
            messagebox.showinfo("Info", "Source folder is empty. No files to organize.")
            return

        operation_type = "copy" if use_copy else "move"
        confirm_msg = (
            f"You are about to {operation_type} {len(files_in_source)} file(s)\n"
            f"from:\n'{src}'\n"
            f"into:\n'{dest}'\n"
            f"organized by: '{organization_mode.capitalize()}'\n"
            f"filtering: {', '.join(sorted([ext.upper() for ext in selected_extensions]))}."
        )
        if not messagebox.askyesno("Confirm Organization", confirm_msg):
            return 

        self.log_box.config(state=NORMAL)
        self.log_box.delete(1.0, tk.END)
        self.log_box.config(state=DISABLED)
        self.app.after(0, lambda: self._update_log("Starting organization...\n"))

        self.organize_button.config(state=DISABLED) 

        organizer = PhotoOrganizer() 

        threading.Thread(
            target=organizer.organize_files,
            args=(
                src,
                dest,
                self._update_progress,      
                self._update_log,           
                self._on_organization_done, 
                use_copy,
                organization_mode,
                selected_extensions         
            ),
            daemon=True 
        ).start()

    def run(self):
        self.app.mainloop()