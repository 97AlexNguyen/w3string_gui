"""
Custom widgets for the W3Strings GUI application
"""

import tkinter as tk
from tkinter import messagebox
from src.core.utils import open_folder, open_file_with_system, copy_to_clipboard
import os

class ToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        
    def showtip(self, text):
        """Display text in tooltip window"""
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
        
    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()


def create_tooltip(widget, text):
    """Helper function to create tooltip"""
    tooltip = ToolTip(widget, text)
    
    def enter(event):
        tooltip.showtip(text)
    def leave(event):
        tooltip.hidetip()
        
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


class EnhancedListbox:
    """Enhanced Listbox with tooltip and context menu support"""
    def __init__(self, parent, file_list, **kwargs):
        self.parent = parent
        self.file_list = file_list
        self.listbox = tk.Listbox(parent, **kwargs)
        self.tooltip = None
        self.setup_bindings()
        self.create_context_menu()
        
    def setup_bindings(self):
        self.listbox.bind('<Motion>', self.on_mouse_move)
        self.listbox.bind('<Leave>', self.hide_tooltip)
        self.listbox.bind('<Button-3>', self.show_context_menu)  # Right click
        
    def create_context_menu(self):
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="📁 Open File Location", command=self.open_file_location)
        self.context_menu.add_command(label="📄 Open File", command=self.open_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Copy Path", command=self.copy_path)
        self.context_menu.add_command(label="🗑️ Remove from List", command=self.remove_from_list)
        
    def on_mouse_move(self, event):
        index = self.listbox.nearest(event.y)
        if 0 <= index < len(self.file_list):
            full_path = self.file_list[index]
            self.show_tooltip(full_path, event.x_root, event.y_root)
        else:
            self.hide_tooltip()
            
    def show_tooltip(self, text, x, y):
        self.hide_tooltip()
        self.tooltip = tk.Toplevel()
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x+10}+{y+10}")
        label = tk.Label(self.tooltip, text=text, justify=tk.LEFT,
                        background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                        font=("Segoe UI", "8", "normal"), wraplength=400)
        label.pack(ipadx=1)
        
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
            
    def show_context_menu(self, event):
        index = self.listbox.nearest(event.y)
        if 0 <= index < len(self.file_list):
            self.selected_index = index
            self.context_menu.post(event.x_root, event.y_root)
            
    def open_file_location(self):
        if hasattr(self, 'selected_index'):
            file_path = self.file_list[self.selected_index]
            folder_path = os.path.dirname(file_path)
            open_folder(folder_path)
            
    def open_file(self):
        if hasattr(self, 'selected_index'):
            file_path = self.file_list[self.selected_index]
            open_file_with_system(file_path)
            
    def copy_path(self):
        if hasattr(self, 'selected_index'):
            file_path = self.file_list[self.selected_index]
            if copy_to_clipboard(self.parent, file_path):
                messagebox.showinfo("Copy", "Path copied to clipboard!")
            
    def remove_from_list(self):
        if hasattr(self, 'selected_index'):
            self.listbox.delete(self.selected_index)
            del self.file_list[self.selected_index]


class MissingExeDialog:
    """Dialog for missing w3strings.exe"""
    def __init__(self, parent, exe_path, link):
        self.dlg = tk.Toplevel(parent)
        self.dlg.title("Missing w3strings.exe")
        self.dlg.geometry("460x220")
        self.dlg.resizable(False, False)
        self.dlg.grab_set()
        
        self.exe_path = exe_path
        self.link = link
        self.parent = parent
        
        self.create_widgets()
        
    def create_widgets(self):
        from tkinter import ttk
        
        ttk.Label(self.dlg, text="⚠️  w3strings.exe not found!", 
                  font=("Segoe UI", 12, "bold")).pack(pady=(15,5))
        
        txt = tk.Text(self.dlg, height=4, wrap="word", relief="flat",
                      background=self.dlg["bg"], borderwidth=0)
        txt.insert("end", f"Expected at:\n{self.exe_path}\n\n"
                          "Download the tool from:\n" + self.link)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=20)

        btn_frame = ttk.Frame(self.dlg)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="🌐 Open link", 
                   command=self.open_link).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📋 Copy link", 
                   command=self.copy_link).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Close", 
                   command=self.close_dialog).pack(side="right", padx=5)

    def copy_link(self):
        copy_to_clipboard(self.dlg, self.link)

    def open_link(self):
        from src.core.utils import open_web_link
        open_web_link(self.link)
        
    def close_dialog(self):
        self.dlg.destroy()
        self.parent.destroy()
        
    def show(self):
        self.parent.wait_window(self.dlg)