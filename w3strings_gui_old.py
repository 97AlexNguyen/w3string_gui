import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import threading
from pathlib import Path
import webbrowser
import platform
import webbrowser
import sv_ttk     
import sys
import re

def get_exe_directory():
    """Get the directory containing the actual exe file"""
    if getattr(sys, 'frozen', False):
        # When running from packaged exe
        return Path(sys.executable).parent
    else:
        # When running from Python script
        return Path(__file__).parent.resolve()
    

def show_missing_exe_dialog(parent, exe_path, link):
    dlg = tk.Toplevel(parent)
    dlg.title("Missing w3strings.exe")
    dlg.geometry("460x220")
    dlg.resizable(False, False)
    dlg.grab_set()                 

    ttk.Label(dlg, text="⚠️  w3strings.exe not found!", 
              font=("Segoe UI", 12, "bold")).pack(pady=(15,5))
    txt = tk.Text(dlg, height=4, wrap="word", relief="flat",
                  background=dlg["bg"], borderwidth=0)
    txt.insert("end", f"Expected at:\n{exe_path}\n\n"
                      "Download the tool from:\n" + link)
    txt.configure(state="disabled")
    txt.pack(fill="both", expand=True, padx=20)

    btn_frame = ttk.Frame(dlg)
    btn_frame.pack(pady=10)

    def copy_link():
        dlg.clipboard_clear()
        dlg.clipboard_append(link)

    ttk.Button(btn_frame, text="🌐 Open link", 
               command=lambda: webbrowser.open(link)).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="📋 Copy link", 
               command=copy_link).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="Close", 
               command=lambda: (dlg.destroy(), parent.destroy())
               ).pack(side="right", padx=5)

    parent.wait_window(dlg)       

LINK = "https://www.nexusmods.com/witcher3/mods/1055?tab=files"

# Try to import tkinterdnd2 for drag & drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False
    print("Warning: tkinterdnd2 not installed. Drag & drop feature disabled.")
    print("Install with: pip install tkinterdnd2")



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
            self.open_folder(folder_path)
            
    def open_file(self):
        if hasattr(self, 'selected_index'):
            file_path = self.file_list[self.selected_index]
            self.open_file_with_system(file_path)
            
    def copy_path(self):
        if hasattr(self, 'selected_index'):
            file_path = self.file_list[self.selected_index]
            self.parent.clipboard_clear()
            self.parent.clipboard_append(file_path)
            messagebox.showinfo("Copy", "Path copied to clipboard!")
            
    def remove_from_list(self):
        if hasattr(self, 'selected_index'):
            self.listbox.delete(self.selected_index)
            del self.file_list[self.selected_index]
            
    def open_folder(self, path):
        """Open folder in system file manager"""
        try:
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', path])
            else:  # Linux
                subprocess.run(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {str(e)}")
            
    def open_file_with_system(self, file_path):
        """Open file with system default application"""
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")

class  W3StringsGui:
    def __init__(self, root):
        # Use TkinterDnD if available
        if HAS_DND:
            self.root = TkinterDnD.Tk() if root is None else root
        else:
            self.root = root if root is not None else tk.Tk()
        sv_ttk.set_theme("dark")
        self.root.title("W3Strings GUI")
        self.root.geometry("950x750")
        base_path = get_exe_directory()
        self.w3strings_path = base_path / "w3strings_tool" / "w3strings.exe"

        if not self.w3strings_path.exists():
            msg = f"w3strings.exe not found at:\n{self.w3strings_path}\n"
            messagebox.showerror("Missing w3strings.exe", msg)
            webbrowser.open(LINK)
            self.root.destroy()
            return

        # Selected files for each tab
        self.decode_files = []
        self.encode_files = []
        
        # CSV merge files
        self.merge_idkey_file = tk.StringVar()
        self.merge_text_file = tk.StringVar()
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_decode_tab()
        self.create_encode_tab()
        self.create_csv_tools_tab()
        
    def create_decode_tab(self):
        # Decode tab
        decode_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(decode_frame, text="🔓 Decode W3Strings")
        
        # Configure grid
        decode_frame.columnconfigure(1, weight=1)
        decode_frame.rowconfigure(2, weight=1)
        decode_frame.rowconfigure(5, weight=1)
        
        # File selection section
        ttk.Label(decode_frame, text="Select W3Strings Files to Decode:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # File listbox with scrollbar
        listbox_frame = ttk.Frame(decode_frame)
        listbox_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        # Enhanced listbox with tooltip
        self.decode_enhanced_listbox = EnhancedListbox(listbox_frame, self.decode_files, height=8, selectmode=tk.MULTIPLE)
        self.decode_listbox = self.decode_enhanced_listbox.listbox
        self.decode_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Setup drag & drop if available
        if HAS_DND:
            self.decode_listbox.drop_target_register(DND_FILES)
            self.decode_listbox.dnd_bind('<<Drop>>', lambda e: self.on_drop_decode(e))
        
        decode_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.decode_listbox.yview)
        decode_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.decode_listbox.configure(yscrollcommand=decode_scrollbar.set)
        
        # Drag & drop info
        if HAS_DND:
            ttk.Label(decode_frame, text="Tip: You can drag and drop files directly into the list", 
                     foreground="green", font=("Arial", 11)).grid(row=2, column=0, columnspan=3, sticky=tk.W)
        
        # File operation buttons
        decode_button_frame = ttk.Frame(decode_frame)
        decode_button_frame.grid(row=3, column=0, columnspan=3, pady=(5, 10), sticky=tk.W)
        
        ttk.Button(decode_button_frame, text="📁 Add W3Strings Files", 
                  command=self.add_decode_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(decode_button_frame, text="🗑️ Clear All", 
                  command=self.clear_decode_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(decode_button_frame, text="❌ Remove Selected", 
                  command=self.remove_selected_decode_files).pack(side=tk.LEFT)
        
        # Decode options
        decode_options_frame = ttk.LabelFrame(decode_frame, text="Decode Options", padding="5")
        decode_options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Verbose options for decode
        ttk.Label(decode_options_frame, text="Verbose:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.decode_verbose_var = tk.StringVar(value="none")
        decode_verbose_frame = ttk.Frame(decode_options_frame)
        decode_verbose_frame.grid(row=0, column=1, columnspan=2, sticky=tk.W)
        
        ttk.Radiobutton(decode_verbose_frame, text="None", variable=self.decode_verbose_var, 
                       value="none").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(decode_verbose_frame, text="Verbose", variable=self.decode_verbose_var, 
                       value="verbose").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(decode_verbose_frame, text="Very Verbose", variable=self.decode_verbose_var, 
                       value="very_verbose").pack(side=tk.LEFT)
        
        # Decode action frame
        decode_action_frame = ttk.Frame(decode_frame)
        decode_action_frame.grid(row=5, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        ttk.Button(decode_action_frame, text="🔓 Decode Files", command=self.decode_files_action, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        self.decode_open_folder_btn = ttk.Button(decode_action_frame, text="📁 Open Output Folder", 
                                               command=self.open_decode_output_folder, state="disabled")
        self.decode_open_folder_btn.pack(side=tk.LEFT)
        
        # Output area for decode
        ttk.Label(decode_frame, text="Decode Output:", font=("Arial", 10, "bold")).grid(
            row=6, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.decode_output_text = scrolledtext.ScrolledText(decode_frame, height=10, wrap=tk.WORD)
        self.decode_output_text.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def create_encode_tab(self):
        # Encode tab
        encode_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(encode_frame, text="🔒 Encode CSV")
        
        # Configure grid
        encode_frame.columnconfigure(1, weight=1)
        encode_frame.rowconfigure(2, weight=1)
        encode_frame.rowconfigure(5, weight=1)
        
        # File selection section
        ttk.Label(encode_frame, text="Select CSV Files to Encode:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # File listbox with scrollbar
        encode_listbox_frame = ttk.Frame(encode_frame)
        encode_listbox_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        encode_listbox_frame.columnconfigure(0, weight=1)
        encode_listbox_frame.rowconfigure(0, weight=1)
        
        # Enhanced listbox with tooltip
        self.encode_enhanced_listbox = EnhancedListbox(encode_listbox_frame, self.encode_files, height=8, selectmode=tk.MULTIPLE)
        self.encode_listbox = self.encode_enhanced_listbox.listbox
        self.encode_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Setup drag & drop if available
        if HAS_DND:
            self.encode_listbox.drop_target_register(DND_FILES)
            self.encode_listbox.dnd_bind('<<Drop>>', lambda e: self.on_drop_encode(e))
        
        encode_scrollbar = ttk.Scrollbar(encode_listbox_frame, orient=tk.VERTICAL, command=self.encode_listbox.yview)
        encode_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.encode_listbox.configure(yscrollcommand=encode_scrollbar.set)
        
        # Drag & drop info
        if HAS_DND:
            ttk.Label(encode_frame, text="Tip: You can drag and drop files directly into the list", 
                     foreground="green", font=("Arial", 10)).grid(row=2, column=0, columnspan=3, sticky=tk.W)
        
        # File operation buttons
        encode_button_frame = ttk.Frame(encode_frame)
        encode_button_frame.grid(row=3, column=0, columnspan=3, pady=(5, 10), sticky=tk.W)
        
        ttk.Button(encode_button_frame, text="📁 Add CSV Files", 
                  command=self.add_encode_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(encode_button_frame, text="🗑️ Clear All", 
                  command=self.clear_encode_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(encode_button_frame, text="❌ Remove Selected", 
                  command=self.remove_selected_encode_files).pack(side=tk.LEFT)
        
        # Encode options
        encode_options_frame = ttk.LabelFrame(encode_frame, text="Encode Options", padding="5")
        encode_options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        encode_options_frame.columnconfigure(1, weight=1)
        
        # ID Space option
        ttk.Label(encode_options_frame, text="ID Space:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.id_space_var = tk.StringVar()
        self.id_space_entry = ttk.Entry(encode_options_frame, textvariable=self.id_space_var, width=15)
        self.id_space_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        
        # Force ignore ID space check
        self.force_ignore_var = tk.BooleanVar(value=True)  # Set default to True
        ttk.Checkbutton(encode_options_frame, text="Force ignore ID space check", 
                       variable=self.force_ignore_var).grid(row=0, column=2, sticky=tk.W)
        
        # Verbose options for encode
        ttk.Label(encode_options_frame, text="Verbose:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        self.encode_verbose_var = tk.StringVar(value="none")
        encode_verbose_frame = ttk.Frame(encode_options_frame)
        encode_verbose_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W)
        
        ttk.Radiobutton(encode_verbose_frame, text="None", variable=self.encode_verbose_var, 
                       value="none").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(encode_verbose_frame, text="Verbose", variable=self.encode_verbose_var, 
                       value="verbose").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(encode_verbose_frame, text="Very Verbose", variable=self.encode_verbose_var, 
                       value="very_verbose").pack(side=tk.LEFT)
        
        # Encode action frame
        encode_action_frame = ttk.Frame(encode_frame)
        encode_action_frame.grid(row=5, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        ttk.Button(encode_action_frame, text="🔒 Encode Files", command=self.encode_files_action, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
                  
        self.encode_open_folder_btn = ttk.Button(encode_action_frame, text="📁 Open Output Folder", 
                                               command=self.open_encode_output_folder, state="disabled")
        self.encode_open_folder_btn.pack(side=tk.LEFT)
        
        # Output area for encode
        ttk.Label(encode_frame, text="Encode Output:", font=("Arial", 10, "bold")).grid(
            row=6, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.encode_output_text = scrolledtext.ScrolledText(encode_frame, height=10, wrap=tk.WORD)
        self.encode_output_text.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def create_csv_tools_tab(self):
        # CSV Tools tab
        csv_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(csv_frame, text="🛠️ CSV Tools")
        
        # Configure grid
        csv_frame.columnconfigure(0, weight=1)
        csv_frame.rowconfigure(5, weight=1)
        
        # Split section
        split_frame = ttk.LabelFrame(csv_frame, text="Split CSV (ID/Key + Text)", padding="10")
        split_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        split_frame.columnconfigure(1, weight=1)
        
        ttk.Label(split_frame, text="Split a CSV file into two separate files: ID/Key and Text").grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        ttk.Label(split_frame, text="Format: id|key(hex)|key(str)|text").grid(
            row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Add numbering option
        self.add_line_numbers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(split_frame, text="📝 Add line numbers to text file (recommended)", 
                       variable=self.add_line_numbers_var,
                       command=self.update_split_info).grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Info label that changes based on checkbox
        self.split_info_label = ttk.Label(split_frame, text="", foreground="Green", font=("Arial", 10))
        self.split_info_label.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        self.update_split_info()  # Initialize the label
        
        ttk.Button(split_frame, text="🔪 Select CSV to Split", command=self.select_file_split, 
                  width=30).grid(row=4, column=0, sticky=tk.W)
        
        # Merge section - Redesigned
        merge_frame = ttk.LabelFrame(csv_frame, text="Merge CSV (ID/Key + Text)", padding="10")
        merge_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        merge_frame.columnconfigure(1, weight=1)
        
        ttk.Label(merge_frame, text="Merge an ID/Key file and a Text file into a single complete CSV file").grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Smart merge option
        self.smart_merge_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(merge_frame, text="🧠 Smart merge (auto-detect numbered lines)", 
                       variable=self.smart_merge_var,
                       command=self.update_merge_info).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Info label for merge
        self.merge_info_label = ttk.Label(merge_frame, text="", foreground="Green", font=("Arial", 10))
        self.merge_info_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        self.update_merge_info()  # Initialize the label
        
        # ID/Key file selection
        ttk.Label(merge_frame, text="ID/Key File:").grid(row=3, column=0, sticky=tk.W, padx=(0, 5))
        self.idkey_entry = ttk.Entry(merge_frame, textvariable=self.merge_idkey_file, state="readonly")
        self.idkey_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(merge_frame, text="📁 Browse", command=self.select_idkey_file, 
                  width=10).grid(row=3, column=2, padx=(0, 5))
        ttk.Button(merge_frame, text="❌", command=self.clear_idkey_file, 
                  width=3).grid(row=3, column=3)
        
        # Text file selection
        ttk.Label(merge_frame, text="Text File:").grid(row=4, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        self.text_entry = ttk.Entry(merge_frame, textvariable=self.merge_text_file, state="readonly")
        self.text_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        ttk.Button(merge_frame, text="📁 Browse", command=self.select_text_file, 
                  width=10).grid(row=4, column=2, padx=(0, 5), pady=(5, 0))
        ttk.Button(merge_frame, text="❌", command=self.clear_text_file, 
                  width=3).grid(row=4, column=3, pady=(5, 0))
        
        # Merge button
        merge_button_frame = ttk.Frame(merge_frame)
        merge_button_frame.grid(row=5, column=0, columnspan=4, pady=(10, 0))
        
        self.merge_button = ttk.Button(merge_button_frame, text="🔗 Merge Files", 
                                     command=self.merge_selected_files, state="disabled")
        self.merge_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.csv_open_folder_btn = ttk.Button(merge_button_frame, text="📁 Open Output Folder", 
                                            command=self.open_csv_output_folder, state="disabled")
        self.csv_open_folder_btn.pack(side=tk.LEFT)
        
        # Info section
        info_frame = ttk.LabelFrame(csv_frame, text="User Guide", padding="10")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        info_text = """
            Recommended workflow:
            1. Decode .w3strings files to CSV
            2. Use Split to separate CSV into two files: ID/Key and Text (with line numbers)
            3. Edit/translate the Text file (keep line count and order unchanged)
            4. Select ID/Key and Text files, then Merge to combine them
            5. Encode CSV back to .w3strings

            Note: You must keep the line count unchanged when editing the Text file!
        """
        
        ttk.Label(info_frame, text=info_text.strip(), justify=tk.LEFT, 
                 foreground="green").grid(row=0, column=0, sticky=(tk.W, tk.N))
        
        # Output area for CSV tools
        ttk.Label(csv_frame, text="CSV Tools Output:", font=("Arial", 10, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        self.csv_output_text = scrolledtext.ScrolledText(csv_frame, height=8, wrap=tk.WORD)
        self.csv_output_text.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def update_split_info(self):
        """Update split info label based on checkbox"""
        if self.add_line_numbers_var.get():
            self.split_info_label.config(text="Text will be numbered: '1:Text content', '2:Text content', ...")
        else:
            self.split_info_label.config(text="Text will be saved as-is without line numbers")
    
    def update_merge_info(self):
        """Update merge info label based on checkbox"""
        if self.smart_merge_var.get():
            self.merge_info_label.config(text="Auto-detect and handle numbered lines (1:, 2:, ...)")
        else:
            self.merge_info_label.config(text="Directly merge each line without handling line numbers")
        
    # Drag & Drop methods
    def on_drop_decode(self, event):
        files = self.parse_drop_files(event.data)
        self.add_files_to_decode_list(files)
        
    def on_drop_encode(self, event):
        files = self.parse_drop_files(event.data)
        self.add_files_to_encode_list(files)
        
    def parse_drop_files(self, data):
        """Parse dropped files data"""
        # Remove curly braces and split by spaces, handling paths with spaces
        files = []
        if data.startswith('{') and data.endswith('}'):
            data = data[1:-1]
        
        # Split by } { pattern to handle multiple files
        file_list = data.split('} {')
        for file_path in file_list:
            file_path = file_path.strip('{}')
            if os.path.isfile(file_path):
                files.append(file_path)
        return files
    
    # Decode tab methods
    def add_decode_files(self):
        files = filedialog.askopenfilenames(
            title="Select W3Strings Files",
            filetypes=[("W3Strings files", "*.w3strings"), ("All files", "*.*")]
        )
        self.add_files_to_decode_list(files)
        
    def add_files_to_decode_list(self, files):
        for file in files:
            if file not in self.decode_files:
                self.decode_files.append(file)
                self.decode_listbox.insert(tk.END, os.path.basename(file))
                
    def clear_decode_files(self):
        self.decode_files.clear()
        self.decode_listbox.delete(0, tk.END)
        
    def remove_selected_decode_files(self):
        selected_indices = list(self.decode_listbox.curselection())
        selected_indices.reverse()
        
        for index in selected_indices:
            self.decode_listbox.delete(index)
            del self.decode_files[index]
    
    # Encode tab methods
    def add_encode_files(self):
        files = filedialog.askopenfilenames(
            title="Select CSV Files",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        self.add_files_to_encode_list(files)
        
    def add_files_to_encode_list(self, files):
        for file in files:
            if file not in self.encode_files:
                self.encode_files.append(file)
                self.encode_listbox.insert(tk.END, os.path.basename(file))
                
    def clear_encode_files(self):
        self.encode_files.clear()
        self.encode_listbox.delete(0, tk.END)
        
    def remove_selected_encode_files(self):
        selected_indices = list(self.encode_listbox.curselection())
        selected_indices.reverse()
        
        for index in selected_indices:
            self.encode_listbox.delete(index)
            del self.encode_files[index]
            
    # CSV Merge methods
    def select_idkey_file(self):
        file_path = filedialog.askopenfilename(
            title="Select ID/Key file (CSV)",
            filetypes=[("CSV Files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.merge_idkey_file.set(file_path)
            self.check_merge_ready()
            
    def select_text_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Text file",
            filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.merge_text_file.set(file_path)
            self.check_merge_ready()
            
    def clear_idkey_file(self):
        self.merge_idkey_file.set("")
        self.check_merge_ready()
        
    def clear_text_file(self):
        self.merge_text_file.set("")
        self.check_merge_ready()
        
    def check_merge_ready(self):
        """Enable merge button if both files are selected"""
        if self.merge_idkey_file.get() and self.merge_text_file.get():
            self.merge_button.config(state="normal")
        else:
            self.merge_button.config(state="disabled")
            
    def merge_selected_files(self):
        idkey_file = self.merge_idkey_file.get()
        text_file = self.merge_text_file.get()
        
        if not idkey_file or not text_file:
            messagebox.showwarning("Warning", "Please select both files!")
            return
            
        self.csv_output_text.delete(1.0, tk.END)
        self.log_output(f"ID/Key file: {os.path.basename(idkey_file)}", self.csv_output_text)
        self.log_output(f"Text file: {os.path.basename(text_file)}", self.csv_output_text)
        self.log_output("Merging files...", self.csv_output_text)
        self.merge_csv(idkey_file, text_file)
            
    # Command building and execution methods
    def log_output(self, message, output_widget):
        output_widget.insert(tk.END, message + "\n")
        output_widget.see(tk.END)
        self.root.update_idletasks()
        
    def build_command(self, action, file_path, verbose_var):
        cmd = [str(self.w3strings_path)]
        
        if action == "decode":
            cmd.extend(["-d", file_path])
        elif action == "encode":
            cmd.extend(["-e", file_path])
            
            # Add ID space if provided for encoding
            if self.id_space_var.get().strip():
                cmd.extend(["-i", self.id_space_var.get().strip()])
                
            # Add force ignore option
            if self.force_ignore_var.get():
                cmd.append("--force-ignore-id-space-check-i-know-what-i-am-doing")
                
        # Add verbose options
        verbose = verbose_var.get()
        if verbose == "verbose":
            cmd.append("-v")
        elif verbose == "very_verbose":
            cmd.append("--very-verbose")
            
        return cmd
        
    def execute_command(self, cmd, output_widget):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.stdout:
                self.log_output(f"Output: {result.stdout}", output_widget)
            if result.stderr:
                self.log_output(f"Error: {result.stderr}", output_widget)
            if result.returncode == 0:
                self.log_output("✓ Command executed successfully", output_widget)
            else:
                self.log_output(f"✗ Command failed with return code {result.returncode}", output_widget)
                
            return result.returncode == 0
            
        except Exception as e:
            self.log_output(f"Exception: {str(e)}", output_widget)
            return False
            
    def process_files(self, action, file_list, verbose_var, output_widget, open_folder_btn):
        if not file_list:
            messagebox.showwarning("Warning", "Please select at least one file.")
            return
            
        if not self.w3strings_path.exists():
            messagebox.showerror("Error", f"w3strings.exe not found at: {self.w3strings_path}")
            return
            
        # Clear output
        output_widget.delete(1.0, tk.END)
        
        success_count = 0
        total_files = len(file_list)
        output_folders = set()
        
        for i, file_path in enumerate(file_list, 1):
            self.log_output(f"[{i}/{total_files}] Processing: {os.path.basename(file_path)}", output_widget)
            
            # Validate file extension
            if action == "decode" and not file_path.endswith('.w3strings'):
                self.log_output(f"⚠ Warning: {file_path} is not a .w3strings file", output_widget)
            elif action == "encode" and not file_path.endswith('.csv'):
                self.log_output(f"⚠ Warning: {file_path} is not a .csv file", output_widget)
                
            cmd = self.build_command(action, file_path, verbose_var)
            self.log_output(f"Command: {' '.join(cmd)}", output_widget)
            
            if self.execute_command(cmd, output_widget):
                success_count += 1
                # Store output folder for "Open Folder" button
                output_folders.add(os.path.dirname(file_path))
                
            self.log_output("-" * 50, output_widget)
            
        self.log_output(f"Completed: {success_count}/{total_files} files processed successfully", output_widget)
        
        # Enable "Open Output Folder" button if any files were processed successfully
        if success_count > 0 and output_folders:
            # Store the first output folder for the button
            setattr(self, f"{action}_last_output_folder", list(output_folders)[0])
            open_folder_btn.config(state="normal")
        
    def decode_files_action(self):
        def worker():
            self.process_files("decode", self.decode_files, self.decode_verbose_var, 
                             self.decode_output_text, self.decode_open_folder_btn)
        threading.Thread(target=worker, daemon=True).start()
        
    def encode_files_action(self):
        def worker():
            self.process_files("encode", self.encode_files, self.encode_verbose_var, 
                             self.encode_output_text, self.encode_open_folder_btn)
        threading.Thread(target=worker, daemon=True).start()
        
    # Open folder methods
    def open_folder(self, path):
        """Open folder in system file manager"""
        try:
            if platform.system() == 'Windows':
                os.startfile(path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', path])
            else:  # Linux
                subprocess.run(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder: {str(e)}")
            
    def open_decode_output_folder(self):
        if hasattr(self, 'decode_last_output_folder'):
            self.open_folder(self.decode_last_output_folder)
        else:
            messagebox.showwarning("Warning", "No output folder yet!")
            
    def open_encode_output_folder(self):
        if hasattr(self, 'encode_last_output_folder'):
            self.open_folder(self.encode_last_output_folder)
        else:
            messagebox.showwarning("Warning", "No output folder yet!")
            
    def open_csv_output_folder(self):
        if hasattr(self, 'csv_last_output_folder'):
            self.open_folder(self.csv_last_output_folder)
        else:
            messagebox.showwarning("Warning", "No output folder yet!")
        
    # CSV Tools methods with line numbering feature
    def split_csv(self, filepath):
        try:
            with open(filepath, encoding='utf-8') as f:
                lines = f.readlines()
            
            meta_lines = [line for line in lines if line.startswith(';')]
            data_lines = [line for line in lines if not line.startswith(';')]
            
            ids_keys = []
            texts = []
            
            for line in data_lines:
                parts = line.strip().split('|', maxsplit=3)
                if len(parts) == 4:
                    ids_keys.append('|'.join(parts[:3]))
                    texts.append(parts[3])
                else:
                    ids_keys.append(line.strip())
                    texts.append("")
            
            base_name = os.path.splitext(filepath)[0]
            idkey_path = base_name + "_idkey.csv"
            
            # Create text file name based on numbering option
            if self.add_line_numbers_var.get():
                text_path = base_name + "_text_numbered.txt"
            else:
                text_path = base_name + "_text.txt"
            
            # Save ID/Key file
            with open(idkey_path, 'w', encoding='utf-8') as f1:
                for meta in meta_lines:
                    f1.write(meta)
                for line in ids_keys:
                    f1.write(line + '\n')
            
            # Save Text file with or without numbering
            with open(text_path, 'w', encoding='utf-8') as f2:
                if self.add_line_numbers_var.get():
                    # Add line numbers to each line
                    for i, text in enumerate(texts, 1):
                        f2.write(f"{i}:{text}\n")
                else:
                    # Save as-is
                    for text in texts:
                        f2.write(text + '\n')
            
            # Enable open folder button and store output folder
            self.csv_last_output_folder = os.path.dirname(filepath)
            self.csv_open_folder_btn.config(state="normal")
            
            self.log_output(f"✓ Split successful!", self.csv_output_text)
            self.log_output(f"ID/Key file: {idkey_path}", self.csv_output_text)
            self.log_output(f"Text file: {text_path}", self.csv_output_text)
            if self.add_line_numbers_var.get():
                self.log_output(f"Text has been numbered", self.csv_output_text)
            messagebox.showinfo("Success", f"File split successfully!\nSaved:\n{idkey_path}\n{text_path}")
            
        except Exception as e:
            error_msg = f"Error splitting file: {str(e)}"
            self.log_output(f"✗ {error_msg}", self.csv_output_text)
            messagebox.showerror("Error", error_msg)
    
    def merge_csv(self, idkey_file, text_file):
        try:
            with open(idkey_file, encoding='utf-8') as f1:
                lines = f1.readlines()
            
            meta_lines = [line for line in lines if line.startswith(';')]
            data_lines = [line for line in lines if not line.startswith(';')]
            
            with open(text_file, encoding='utf-8') as f2:
                text_lines = [line.rstrip('\n\r') for line in f2.readlines()]
            
            texts = []
            
            if self.smart_merge_var.get():
                # Smart merge: Auto-detect and handle line numbers
                self.log_output("🧠 Using smart merge - detecting line number format", self.csv_output_text)
                
                numbered_count = 0
                for line in text_lines:
                    # Check if line starts with number:
                    match = re.match(r'^(\d+):(.*)', line)
                    if match:
                        numbered_count += 1
                        # Get content after ":":
                        texts.append(match.group(2))
                    else:
                        # If no line number, keep as-is
                        texts.append(line)
                
                if numbered_count > 0:
                    self.log_output(f"✓ Detected {numbered_count}/{len(text_lines)} numbered lines", self.csv_output_text)
                else:
                    self.log_output("ℹ No numbered lines detected, treating as plain text", self.csv_output_text)
            else:
                # Simple merge: Direct merge
                self.log_output("📝 Using simple merge - not handling line numbers", self.csv_output_text)
                texts = text_lines
            
            if len(data_lines) != len(texts):
                error_msg = f"Line count mismatch: ID/Key has {len(data_lines)} lines, Text has {len(texts)} lines"
                self.log_output(f"✗ {error_msg}", self.csv_output_text)
                messagebox.showerror("Error", error_msg)
                return
            
            merged_lines = []
            for idline, text in zip(data_lines, texts):
                merged = idline.rstrip('\n\r') + '|' + text
                merged_lines.append(merged)
            
            output_path = os.path.splitext(idkey_file)[0] + "_merged.csv"
            with open(output_path, 'w', encoding='utf-8') as f:
                for meta in meta_lines:
                    f.write(meta)
                for line in merged_lines:
                    f.write(line + '\n')
            
            # Enable open folder button and store output folder
            self.csv_last_output_folder = os.path.dirname(output_path)
            self.csv_open_folder_btn.config(state="normal")
            
            self.log_output(f"✓ Merge successful!", self.csv_output_text)
            self.log_output(f"Result file: {output_path}", self.csv_output_text)
            messagebox.showinfo("Success", f"Files merged successfully!\nSaved at:\n{output_path}")
            
        except Exception as e:
            error_msg = f"Error merging files: {str(e)}"
            self.log_output(f"✗ {error_msg}", self.csv_output_text)
            messagebox.showerror("Error", error_msg)
    
    def select_file_split(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV file to split",
            filetypes=[("CSV Files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.csv_output_text.delete(1.0, tk.END)
            self.log_output(f"Splitting file: {os.path.basename(file_path)}", self.csv_output_text)
            self.split_csv(file_path)

def main():
    if HAS_DND:
        root = None  
    else:
        root = tk.Tk()
    app =  W3StringsGui(root)
    app.root.mainloop()

if __name__ == "__main__":
    main()