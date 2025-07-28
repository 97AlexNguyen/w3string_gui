"""
Dialog for missing w3strings.exe file
"""

import tkinter as tk
from tkinter import ttk

from ..core.utils import copy_to_clipboard, open_web_link


class MissingExeDialog:
    """Dialog for missing w3strings.exe"""
    
    def __init__(self, parent, exe_path, link):
        self.parent = parent
        self.exe_path = exe_path
        self.link = link
        self.dlg = None
        
    def show(self):
        """Show the dialog"""
        self.dlg = tk.Toplevel(self.parent)
        self.dlg.title("Missing w3strings.exe")
        self.dlg.geometry("460x220")
        self.dlg.resizable(False, False)
        self.dlg.grab_set()
        
        self.create_widgets()
        self.parent.wait_window(self.dlg)
        
    def create_widgets(self):
        """Create dialog widgets"""
        # Title label
        ttk.Label(self.dlg, text="⚠️  w3strings.exe not found!", 
                  font=("Segoe UI", 12, "bold")).pack(pady=(15, 5))
        
        # Message text
        txt = tk.Text(self.dlg, height=4, wrap="word", relief="flat",
                      background=self.dlg["bg"], borderwidth=0)
        txt.insert("end", f"Expected at:\n{self.exe_path}\n\n"
                          "Download the tool from:\n" + self.link)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=20)

        # Button frame
        btn_frame = ttk.Frame(self.dlg)
        btn_frame.pack(pady=10)

        # Buttons
        ttk.Button(btn_frame, text="🌐 Open link", 
                   command=self.open_link).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📋 Copy link", 
                   command=self.copy_link).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Close", 
                   command=self.close_dialog).pack(side="right", padx=5)

    def copy_link(self):
        """Copy download link to clipboard"""
        if copy_to_clipboard(self.dlg, self.link):
            # Show brief confirmation
            self.dlg.title("Link copied!")
            self.dlg.after(1000, lambda: self.dlg.title("Missing w3strings.exe"))

    def open_link(self):
        """Open download link in browser"""
        open_web_link(self.link)
        
    def close_dialog(self):
        """Close dialog and exit application"""
        self.dlg.destroy()
        self.parent.destroy()