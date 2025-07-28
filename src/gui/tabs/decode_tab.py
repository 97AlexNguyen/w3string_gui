"""
Decode tab implementation for W3Strings GUI
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from src.core.constants import *
from src.gui.widgets import EnhancedListbox
from src.core.utils import parse_drop_files, open_folder, log_message
from src.gui.tabs.base_tab import BaseTab

class DecodeTab(BaseTab):
    """Decode tab implementation"""
    def __init__(self, parent, notebook, w3strings_path, has_dnd, dnd_files=None):
        super().__init__(parent, w3strings_path)
        self.files = []
        self.has_dnd = has_dnd
        self.dnd_files = dnd_files
        
        # Debug info
        print(f"DecodeTab: has_dnd={has_dnd}, dnd_files={dnd_files}")
        
        self.create_tab(notebook)
        
    def create_tab(self, notebook):
        self.frame = ttk.Frame(notebook, padding="10")
        notebook.add(self.frame, text=f"{EMOJI_DECODE} Decode W3Strings")
        
        # File selection section
        listbox_frame = self.create_file_selection_section(
            self.frame, "Select W3Strings Files to Decode:", 0)
        
        # Enhanced listbox
        self.enhanced_listbox = EnhancedListbox(listbox_frame, self.files, 
                                               height=8, selectmode=tk.MULTIPLE)
        self.listbox = self.enhanced_listbox.listbox
        self.listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Setup drag & drop if available
        if self.has_dnd and self.dnd_files:
            try:
                self.listbox.drop_target_register(self.dnd_files)
                self.listbox.dnd_bind('<<Drop>>', self.on_drop)
                print("✓ Drag & Drop setup successful for decode tab")
            except Exception as e:
                print(f"✗ Failed to setup drag & drop for decode tab: {e}")
                self.has_dnd = False
        else:
            print("⚠ Drag & Drop not available for decode tab")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, 
                                 command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        # Drag & drop tip
        if self.has_dnd:
            ttk.Label(self.frame, text=DRAG_DROP_TIP, foreground=TIPS_TEXT_COLOR, 
                     font=TIPS_TEXT_FONT).grid(row=2, column=0, columnspan=3, sticky=tk.W)

        # Buttons
        self.create_buttons()
        
        # Options
        self.create_options()
        
        # Action buttons
        self.create_action_buttons()
        
        # Output area
        self.create_output_area()
        
    def create_buttons(self):
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(5, 10), sticky=tk.W)
        
        ttk.Button(button_frame, text=f"{EMOJI_FOLDER} Add W3Strings Files", 
                  command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text=f"{EMOJI_CLEAR} Clear", 
                  command=self.clear_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text=f"{EMOJI_REMOVE} Remove Selected", 
                  command=self.remove_selected_files).pack(side=tk.LEFT)
        
    def create_options(self):
        options_frame = ttk.LabelFrame(self.frame, text="Decode Options", padding="5")
        options_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Verbose options
        ttk.Label(options_frame, text="Verbose:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.verbose_var = tk.StringVar(value=VERBOSE_NONE)
        verbose_frame = ttk.Frame(options_frame)
        verbose_frame.grid(row=0, column=1, columnspan=2, sticky=tk.W)
        
        ttk.Radiobutton(verbose_frame, text="None", variable=self.verbose_var, 
                       value=VERBOSE_NONE).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(verbose_frame, text="Verbose", variable=self.verbose_var, 
                       value=VERBOSE_NORMAL).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(verbose_frame, text="Very Verbose", variable=self.verbose_var, 
                       value=VERBOSE_VERY).pack(side=tk.LEFT)
        
    def create_action_buttons(self):
        action_frame = ttk.Frame(self.frame)
        action_frame.grid(row=5, column=0, columnspan=3, pady=(0, 10), sticky=tk.W)
        
        ttk.Button(action_frame, text=f"{EMOJI_DECODE} Decode Files", 
                  command=self.decode_files, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_folder_btn = ttk.Button(action_frame, text=f"{EMOJI_FOLDER} Open Output Folder", 
                                         command=self.open_output_folder, state="disabled")
        self.open_folder_btn.pack(side=tk.LEFT)
        
    def create_output_area(self):
        ttk.Label(self.frame, text="Decode Output:", font=("Arial", 10, "bold")).grid(
            row=6, column=0, columnspan=3, sticky=tk.W, pady=(10, 5))
        
        self.output_text = scrolledtext.ScrolledText(self.frame, height=10, wrap=tk.WORD)
        self.output_text.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def on_drop(self, event):
        """Handle drag and drop files"""
        print(f"Drop event received: {event.data}")
        files = parse_drop_files(event.data)
        print(f"Parsed files: {files}")
        self.add_files_to_list(files)
        
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select W3Strings Files",
            filetypes=W3STRINGS_FILETYPES
        )
        self.add_files_to_list(files)
        
    def add_files_to_list(self, files):
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.listbox.insert(tk.END, os.path.basename(file))
                print(f"Added file: {file}")
                
    def clear_files(self):
        self.files.clear()
        self.listbox.delete(0, tk.END)
        
    def remove_selected_files(self):
        selected_indices = list(self.listbox.curselection())
        selected_indices.reverse()
        
        for index in selected_indices:
            self.listbox.delete(index)
            del self.files[index]
            
    def decode_files(self):
        def worker():
            success, output_folder = self.command_handler.process_files(
                "decode", self.files, self.verbose_var.get(), self.output_text)
            if success and output_folder:
                self.last_output_folder = output_folder
                self.open_folder_btn.config(state="normal")
        threading.Thread(target=worker, daemon=True).start()
        
    def open_output_folder(self):
        if hasattr(self, 'last_output_folder'):
            open_folder(self.last_output_folder)
        else:
            messagebox.showwarning("Warning", "No output folder yet!")