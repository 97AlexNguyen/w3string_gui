"""
Tab implementations for the W3Strings GUI
"""

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from src.core.constants import *
from .widgets import EnhancedListbox
from src.core.utils import parse_drop_files, open_folder, log_message
from src.processors.command_handler import CommandHandler
from src.processors.csv_processor import CSVProcessor


class BaseTab:
    """Base class for all tabs"""
    def __init__(self, parent, w3strings_path):
        self.parent = parent
        self.w3strings_path = w3strings_path
        self.command_handler = CommandHandler(w3strings_path)
        
    def create_file_selection_section(self, frame, title, row_start=0):
        """Create common file selection UI elements"""
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(row_start + 1, weight=1)
        
        ttk.Label(frame, text=title, font=("Arial", 10, "bold")).grid(
            row=row_start, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # File listbox frame
        listbox_frame = ttk.Frame(frame)
        listbox_frame.grid(row=row_start + 1, column=0, columnspan=3, 
                          sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)
        
        return listbox_frame


