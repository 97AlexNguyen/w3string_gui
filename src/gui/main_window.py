"""
Main GUI application window for W3Strings tool
"""

import tkinter as tk
from tkinter import ttk, messagebox

try:
    import sv_ttk
    HAS_THEME = True
except ImportError:
    HAS_THEME = False
    print("Warning: sv_ttk not installed. Dark theme disabled.")

from src.core.constants import *
from src.core.utils import get_w3strings_path, check_drag_drop_support
from src.gui.widgets import MissingExeDialog
from src.gui.tabs import DecodeTab, EncodeTab, CSVToolsTab


class W3StringsGUI:
    """Main GUI application class"""
    
    def __init__(self, root=None):
        # Check for drag and drop support
        self.has_dnd, self.dnd_files, self.TkinterDnD = check_drag_drop_support()
        
        # Use provided root or create new one
        if root is not None:
            self.root = root
            print("✓ Using provided root window")
        else:
            # Create new root window with DnD support if available
            if self.has_dnd and self.TkinterDnD:
                self.root = self.TkinterDnD.Tk()
                print("✓ Created new TkinterDnD root window")
            else:
                self.root = tk.Tk()
                print("✓ Created new standard root window")
            
        self.setup_window()
        self.check_dependencies()
        
        if self.validate_w3strings_exe():
            self.create_widgets()
        else:
            self.show_missing_exe_dialog()
            
    def setup_window(self):
        """Setup main window properties"""
        # Apply dark theme if available
        if HAS_THEME:
            sv_ttk.set_theme("dark")
            
        self.root.title(APP_TITLE)
        self.root.geometry(APP_GEOMETRY)
        
        # Debug info
        print(f"✓ Window setup complete. DnD support: {self.has_dnd}")
        
    def check_dependencies(self):
        """Check for required dependencies"""
        self.w3strings_path = get_w3strings_path()
        print(f"Looking for w3strings.exe at: {self.w3strings_path}")
        
    def validate_w3strings_exe(self):
        """Check if w3strings.exe exists"""
        exists = self.w3strings_path.exists()
        if not exists:
            print(f"w3strings.exe not found at: {self.w3strings_path}")
        return exists
        
    def show_missing_exe_dialog(self):
        """Show dialog for missing w3strings.exe"""
        dialog = MissingExeDialog(self.root, self.w3strings_path, DOWNLOAD_LINK)
        dialog.show()
        
    def create_widgets(self):
        """Create main application widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_tabs()
        
    def create_tabs(self):
        """Create all application tabs"""
        # Debug drag and drop parameters
        print(f"Creating tabs with DnD parameters: has_dnd={self.has_dnd}, dnd_files={self.dnd_files}")
        
        # Decode tab
        self.decode_tab = DecodeTab(
            self.root, self.notebook, self.w3strings_path, 
            self.has_dnd, self.dnd_files
        )
        
        # Encode tab
        self.encode_tab = EncodeTab(
            self.root, self.notebook, self.w3strings_path, 
            self.has_dnd, self.dnd_files
        )
        
        # CSV Tools tab
        self.csv_tools_tab = CSVToolsTab(self.root, self.notebook)
        
        print("✓ All tabs created successfully")
        
    def run(self):
        """Start the GUI application"""
        print("✓ Starting main event loop...")
        self.root.mainloop()