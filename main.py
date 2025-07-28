"""
Main entry point for W3Strings GUI application
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    # Import drag and drop support first
    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
        HAS_DND = True
        print("✓ tkinterdnd2 loaded successfully")
    except ImportError:
        HAS_DND = False
        TkinterDnD = None
        DND_FILES = None
        print("⚠ Warning: tkinterdnd2 not available. Drag & drop disabled.")
    
    from src.gui.main_window import W3StringsGUI
    
    def main():
        """Main entry point"""
        print("Starting W3Strings GUI...")
        
        # Create root window with proper DnD support
        if HAS_DND:
            root = TkinterDnD.Tk()
            print("✓ Using TkinterDnD root window")
        else:
            import tkinter as tk
            root = tk.Tk()
            print("✓ Using standard Tk root window")
        
        # Create app with root window
        app = W3StringsGUI(root)
        app.run()
        
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Falling back to standalone GUI...")
    
    # Fallback to standalone version
    try:
        import w3strings_gui_old
        w3strings_gui_old.main()
    except ImportError as e2:
        print(f"Could not import standalone GUI either: {e2}")
        print("Please check your Python environment and dependencies.")
        sys.exit(1)