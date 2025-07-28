"""
Enhanced CSV Tools tab with advanced splitting capabilities
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

from src.core.constants import *
from src.core.utils import open_folder, log_message
from src.processors.csv_processor import CSVProcessor


class CSVToolsTab:
    """Enhanced CSV Tools tab with advanced splitting features"""
    
    def __init__(self, parent, notebook):
        self.parent = parent
        
        # File storage
        self.idkey_file = ""
        self.text_files = []
        
        # Create tab UI
        self.create_tab(notebook)
        
    def create_tab(self, notebook):
        """Create the CSV tools tab UI with scrollable content"""
        # Main tab frame
        self.main_frame = ttk.Frame(notebook, padding="5")
        notebook.add(self.main_frame, text=f"{EMOJI_TOOLS} CSV Tools")
        
        # Configure main frame
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width)
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Grid canvas and scrollbar
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure scrollable frame
        self.scrollable_frame.columnconfigure(0, weight=1)
        
        # Create UI sections
        self.create_split_section()
        self.create_merge_section()
        self.create_info_section()
        self.create_output_area()
        
        # Bind mousewheel
        self.bind_mousewheel()
        
    def bind_mousewheel(self):
        """Bind mousewheel scrolling to canvas"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
            
    def create_split_section(self):
        """Create enhanced CSV split section with multiple modes"""
        split_frame = ttk.LabelFrame(self.scrollable_frame, text="🔪 Advanced CSV Split", padding="10")
        split_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        split_frame.columnconfigure(0, weight=1)

        # Description
        ttk.Label(split_frame, text="Split CSV into ID/Key and Text files with advanced options", 
                font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))

        # Split mode selection
        mode_frame = ttk.LabelFrame(split_frame, text="Split Mode", padding="5")
        mode_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Cấu hình lại grid để có layout đều hơn
        mode_frame.columnconfigure(0, weight=1)
        mode_frame.columnconfigure(1, weight=1) 
        mode_frame.columnconfigure(2, weight=1)

        self.split_mode_var = tk.StringVar(value="basic")
        
        # Row 1: 3 buttons (Basic, ID Range, Text Length)
        ttk.Radiobutton(mode_frame, text="Basic Split", variable=self.split_mode_var, 
                    value="basic", command=self.on_split_mode_change).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Radiobutton(mode_frame, text="By ID Range", variable=self.split_mode_var, 
                    value="by_id_range", command=self.on_split_mode_change).grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        ttk.Radiobutton(mode_frame, text="By Text Length", variable=self.split_mode_var, 
                    value="by_text_length", command=self.on_split_mode_change).grid(row=0, column=2, sticky=tk.W)
        
        # Row 2: 2 buttons (Count, Pattern)
        ttk.Radiobutton(mode_frame, text="By Count", variable=self.split_mode_var, 
                    value="by_count", command=self.on_split_mode_change).grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(5, 0))
        ttk.Radiobutton(mode_frame, text="By Pattern", variable=self.split_mode_var, 
                    value="by_pattern", command=self.on_split_mode_change).grid(row=1, column=1, sticky=tk.W, padx=(0, 5), pady=(5, 0))

        # Parameters frame (dynamic based on mode)
        self.params_frame = ttk.LabelFrame(split_frame, text="Parameters", padding="5")
        self.params_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        self.params_frame.columnconfigure(1, weight=1)

        # Text format option
        format_frame = ttk.Frame(split_frame)
        format_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        self.add_line_numbers_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(format_frame, text=f"{EMOJI_NOTES} Use format ID:content (recommended)", 
                    variable=self.add_line_numbers_var,
                    command=self.update_split_info).pack(side=tk.LEFT)

        # Info label
        self.split_info_label = ttk.Label(split_frame, text="", foreground=TIPS_TEXT_COLOR, font=TIPS_TEXT_FONT)
        self.split_info_label.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Split button
        ttk.Button(split_frame, text=f"{EMOJI_SPLIT} Select CSV to Split", 
                command=self.select_file_split, width=25).grid(row=5, column=0, sticky=tk.W)

        # Initialize parameters display
        self.on_split_mode_change()
        self.update_split_info()

    def on_split_mode_change(self):
        """Update parameters frame based on selected split mode"""
        # Clear existing parameters
        for widget in self.params_frame.winfo_children():
            widget.destroy()

        mode = self.split_mode_var.get()

        if mode == "basic":
            ttk.Label(self.params_frame, text="No additional parameters needed for basic split", 
                    foreground=TIPS_TEXT_COLOR).grid(row=0, column=0, sticky=tk.W)

        elif mode == "by_id_range":
            ttk.Label(self.params_frame, text="Range Size:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
            self.range_size_var = tk.StringVar(value="500")
            ttk.Entry(self.params_frame, textvariable=self.range_size_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
            
            ttk.Label(self.params_frame, text="Max Files:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
            self.max_files_var = tk.StringVar(value="10")
            ttk.Entry(self.params_frame, textvariable=self.max_files_var, width=8).grid(row=0, column=3, sticky=tk.W)
            
            ttk.Label(self.params_frame, text="Split numeric IDs into chunks (e.g., first 500 entries, next 500 entries...)", 
                    foreground=TIPS_TEXT_COLOR, font=TIPS_TEXT_FONT).grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))

        elif mode == "by_text_length":
            ttk.Label(self.params_frame, text="Length Threshold:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
            self.length_threshold_var = tk.StringVar(value="200")
            ttk.Entry(self.params_frame, textvariable=self.length_threshold_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
            
            ttk.Label(self.params_frame, text="Split into long texts (≥threshold) and short texts (<threshold)", 
                    foreground=TIPS_TEXT_COLOR, font=TIPS_TEXT_FONT).grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))

        elif mode == "by_count":
            ttk.Label(self.params_frame, text="Entries per file:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
            self.entries_per_file_var = tk.StringVar(value="100")
            ttk.Entry(self.params_frame, textvariable=self.entries_per_file_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
            
            ttk.Label(self.params_frame, text="Split into multiple files with equal number of entries", 
                    foreground=TIPS_TEXT_COLOR, font=TIPS_TEXT_FONT).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        elif mode == "by_pattern":
            ttk.Label(self.params_frame, text="Pattern (Regex):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
            self.pattern_var = tk.StringVar()
            ttk.Entry(self.params_frame, textvariable=self.pattern_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
            
            ttk.Label(self.params_frame, text="Name:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
            self.pattern_name_var = tk.StringVar(value="custom")
            ttk.Entry(self.params_frame, textvariable=self.pattern_name_var, width=12).grid(row=0, column=3, sticky=tk.W)
            
            self.case_sensitive_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(self.params_frame, text="Case sensitive", 
                        variable=self.case_sensitive_var).grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
            
            ttk.Label(self.params_frame, text="Examples: 'dialog|quest' (contains dialog or quest), '^Hello' (starts with Hello)", 
                    foreground=TIPS_TEXT_COLOR, font=TIPS_TEXT_FONT).grid(row=2, column=0, columnspan=4, sticky=tk.W, pady=(5, 0))
            

    def create_merge_section(self):
        """Create merge section (unchanged from original)"""
        merge_frame = ttk.LabelFrame(self.scrollable_frame, text="🔗 Merge CSV (Single ID/Key + Multiple Text)", padding="10")
        merge_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        merge_frame.columnconfigure(0, weight=1)

        ttk.Label(merge_frame, text="Merge 1 ID/Key file and multiple Text files into a complete CSV").grid(
            row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 5))

        # Smart merge option
        self.smart_merge_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(merge_frame, text=f"{EMOJI_SMART} Auto-detect format (ID:content or ID|content)", 
                       variable=self.smart_merge_var,
                       command=self.update_merge_info).grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 5))

        # Single ID/Key file selection
        idkey_section = ttk.LabelFrame(merge_frame, text="ID/Key File (Only 1 file)", padding="5")
        idkey_section.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        idkey_section.columnconfigure(0, weight=1)

        # ID/Key file display and buttons
        idkey_display_frame = ttk.Frame(idkey_section)
        idkey_display_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        idkey_display_frame.columnconfigure(0, weight=1)

        self.idkey_file_var = tk.StringVar()
        self.idkey_entry = ttk.Entry(idkey_display_frame, textvariable=self.idkey_file_var, 
                                    state="readonly", font=TIPS_TEXT_FONT)
        self.idkey_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        idkey_btn_frame = ttk.Frame(idkey_display_frame)
        idkey_btn_frame.grid(row=0, column=1, sticky=tk.E)

        ttk.Button(idkey_btn_frame, text=f"Select", 
                  command=self.select_idkey_file, width=10).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(idkey_btn_frame, text=f"Clear", 
                  command=self.clear_idkey_file, width=8).pack(side=tk.LEFT)

        # Multiple text files section
        text_section = ttk.LabelFrame(merge_frame, text="Text Files (Priority from top to bottom)", padding="5")
        text_section.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        text_section.columnconfigure(0, weight=1)
        text_section.rowconfigure(1, weight=1)

        # Priority info
        priority_info = ttk.Label(text_section, 
                                text="Priority: The file above has higher priority when handling duplicate IDs", 
                                foreground=TIPS_TEXT_COLOR, font=TIPS_TEXT_FONT)
        priority_info.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Text files listbox
        listbox_frame = ttk.Frame(text_section)
        listbox_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        listbox_frame.columnconfigure(0, weight=1)
        listbox_frame.rowconfigure(0, weight=1)

        self.text_listbox = tk.Listbox(listbox_frame, height=4, selectmode=tk.SINGLE, font=TIPS_TEXT_FONT)
        self.text_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        text_scroll = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.text_listbox.yview)
        text_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.text_listbox.configure(yscrollcommand=text_scroll.set)
        
        # Text control buttons
        text_btn_frame = ttk.Frame(text_section)
        text_btn_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Row 1: Add/Remove buttons
        text_btn_row1 = ttk.Frame(text_btn_frame)
        text_btn_row1.pack(fill=tk.X, pady=(0, 3))

        ttk.Button(text_btn_row1, text=f"Add", 
                  command=self.add_text_files, width=10).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(text_btn_row1, text=f"Remove", 
                  command=self.remove_text_file, width=8).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(text_btn_row1, text=f"Clear", 
                  command=self.clear_text_files, width=10).pack(side=tk.LEFT)

        # Row 2: Priority control buttons
        text_btn_row2 = ttk.Frame(text_btn_frame)
        text_btn_row2.pack(fill=tk.X)

        ttk.Button(text_btn_row2, text="Up", 
                  command=self.move_text_up, width=8).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(text_btn_row2, text="Down", 
                  command=self.move_text_down, width=8).pack(side=tk.LEFT)
        
        # Info label for merge
        self.merge_info_label = ttk.Label(merge_frame, text="", foreground=TIPS_TEXT_COLOR, font=TIPS_TEXT_FONT)
        self.merge_info_label.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        self.update_merge_info()

        # Merge button
        merge_button_frame = ttk.Frame(merge_frame)
        merge_button_frame.grid(row=5, column=0, columnspan=4, pady=(10, 0))

        self.merge_button = ttk.Button(merge_button_frame, text=f"Merge Files", 
                                     command=self.merge_selected_files, state="disabled")
        self.merge_button.pack(side=tk.LEFT, padx=(0, 10))

        self.open_folder_btn = ttk.Button(merge_button_frame, text=f"Open Output Folder", 
                                         command=self.open_output_folder, state="disabled")
        self.open_folder_btn.pack(side=tk.LEFT)
        
    def create_info_section(self):
        """Create enhanced user guide section"""
        info_frame = ttk.LabelFrame(self.scrollable_frame, text="📖 Enhanced User Guide", padding="8")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        info_text = """Enhanced workflow with advanced splitting:
            1. Decode .w3strings files to CSV
            2. Use Advanced Split with multiple modes:
               • Basic: Traditional ID/Key + Text split
               • By ID Range: Split numeric IDs into ranges (great for team work)
               • By Text Length: Separate long/short texts (prioritize complex translations)
               • By Count: Equal distribution (balanced workload)
               • By Pattern: Filter by content (e.g., dialog vs UI texts)
            3. Distribute split files to translators based on expertise
            4. Use Merge to combine all translated files with priority handling
            5. Encode back to .w3strings

            Benefits: Flexible splitting, team collaboration, automatic conflict resolution"""

        ttk.Label(info_frame, text=info_text.strip(), justify=tk.LEFT, 
                 foreground=TIPS_TEXT_COLOR, font=TIPS_TEXT_FONT).grid(row=0, column=0, sticky=(tk.W, tk.N))

    def create_output_area(self):
        """Create output text area"""
        ttk.Label(self.scrollable_frame, text="CSV Tools Output:", 
                 font=("Arial", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=(10, 5))

        self.output_text = scrolledtext.ScrolledText(self.scrollable_frame, height=8, wrap=tk.WORD, font=TIPS_TEXT_FONT)
        self.output_text.grid(row=4, column=0, sticky=(tk.W, tk.E))

        # Initialize CSV processor
        self.csv_processor = CSVProcessor(self.output_text)

    def update_split_info(self):
        """Update split info label based on current settings"""
        mode = self.split_mode_var.get()
        format_info = "Format: ID:content" if self.add_line_numbers_var.get() else "Format: ID|content"
        
        mode_descriptions = {
            "basic": "Basic split into 1 ID/Key file + 1 Text file",
            "by_id_range": "Split into 1 ID/Key file + multiple Text files by ID ranges",
            "by_text_length": "Split into 1 ID/Key file + 2 Text files (long/short texts)",
            "by_count": "Split into 1 ID/Key file + multiple Text files with equal entries",
            "by_pattern": "Split into 1 ID/Key file + 2 Text files (matching/non-matching pattern)"
        }
        
        description = mode_descriptions.get(mode, "")
        self.split_info_label.config(text=f"{description} | {format_info}")

    def update_merge_info(self):
        """Update merge info label"""
        if self.smart_merge_var.get():
            self.merge_info_label.config(text="Auto-detect format ID:content or ID|content")
        else:
            self.merge_info_label.config(text="Only use format ID|content")

    def get_split_parameters(self):
        """Get parameters based on current split mode"""
        mode = self.split_mode_var.get()
        params = {}

        if mode == "by_id_range":
            try:
                params['range_size'] = int(self.range_size_var.get())
                params['max_files'] = int(self.max_files_var.get())
            except ValueError:
                raise ValueError("Range size and max files must be valid numbers")

        elif mode == "by_text_length":
            try:
                params['length_threshold'] = int(self.length_threshold_var.get())
            except ValueError:
                raise ValueError("Length threshold must be a valid number")

        elif mode == "by_count":
            try:
                params['entries_per_file'] = int(self.entries_per_file_var.get())
                if params['entries_per_file'] <= 0:
                    raise ValueError("Entries per file must be greater than 0")
            except ValueError:
                raise ValueError("Entries per file must be a valid positive number")

        elif mode == "by_pattern":
            pattern = self.pattern_var.get().strip()
            if not pattern:
                raise ValueError("Pattern cannot be empty")
            
            params['pattern'] = pattern
            params['pattern_name'] = self.pattern_name_var.get().strip() or "custom"
            params['case_sensitive'] = self.case_sensitive_var.get()

        return params

    def select_file_split(self):
        """Select and split CSV file with advanced options"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file to split",
            filetypes=CSV_FILETYPES
        )
        if not file_path:
            return

        try:
            # Get split parameters
            mode = self.split_mode_var.get()
            params = self.get_split_parameters()
            
            # Clear output and start splitting
            self.output_text.delete(1.0, tk.END)
            log_message(self.output_text, f"Starting {mode} split for: {os.path.basename(file_path)}")
            
            success, files, output_folder = self.csv_processor.split_csv_advanced(
                file_path, mode, params, self.add_line_numbers_var.get())
            
            if success:
                self.last_output_folder = output_folder
                self.open_folder_btn.config(state="normal")
                
                # Show success message with file list
                file_list = "\n".join([os.path.basename(f) for f in files])
                messagebox.showinfo("Success", f"Files split successfully!\n\nCreated {len(files)} files:\n{file_list}")
            else:
                messagebox.showerror("Error", "Could not split file!")
                
        except ValueError as e:
            messagebox.showerror("Parameter Error", str(e))
        except Exception as e:
            log_message(self.output_text, f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Split failed: {str(e)}")

    # Merge-related methods (unchanged from original)
    def refresh_text_display(self):
        """Refresh text listbox display with priority indicators"""
        self.text_listbox.delete(0, tk.END)
        for i, file_path in enumerate(self.text_files):
            display_name = f"[{i+1}] {os.path.basename(file_path)}"
            self.text_listbox.insert(tk.END, display_name)

    def select_idkey_file(self):
        """Select single ID/Key file"""
        file_path = filedialog.askopenfilename(
            title="Select ID/Key file (CSV)",
            filetypes=CSV_FILETYPES
        )
        if file_path:
            self.idkey_file = file_path
            self.idkey_file_var.set(os.path.basename(file_path))
            self.check_merge_ready()

    def clear_idkey_file(self):
        """Clear ID/Key file"""
        self.idkey_file = ""
        self.idkey_file_var.set("")
        self.check_merge_ready()

    def add_text_files(self):
        """Add text files"""
        files = filedialog.askopenfilenames(
            title="Select Text files",
            filetypes=TEXT_FILETYPES
        )
        for file_path in files:
            if file_path not in self.text_files:
                self.text_files.append(file_path)
        self.refresh_text_display()
        self.check_merge_ready()

    def remove_text_file(self):
        """Remove selected text file"""
        selection = self.text_listbox.curselection()
        if selection:
            index = selection[0]
            del self.text_files[index]
            self.refresh_text_display()
            self.check_merge_ready()

    def clear_text_files(self):
        """Clear all text files"""
        self.text_files.clear()
        self.refresh_text_display()
        self.check_merge_ready()

    def move_text_up(self):
        """Move selected text file up in priority"""
        selection = self.text_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            self.text_files[index], self.text_files[index-1] = self.text_files[index-1], self.text_files[index]
            self.refresh_text_display()
            self.text_listbox.selection_set(index-1)

    def move_text_down(self):
        """Move selected text file down in priority"""
        selection = self.text_listbox.curselection()
        if selection and selection[0] < len(self.text_files) - 1:
            index = selection[0]
            self.text_files[index], self.text_files[index+1] = self.text_files[index+1], self.text_files[index]
            self.refresh_text_display()
            self.text_listbox.selection_set(index+1)
            
    def check_merge_ready(self):
        """Enable merge button if files are selected"""
        if self.idkey_file and self.text_files:
            self.merge_button.config(state="normal")
        else:
            self.merge_button.config(state="disabled")
            
    def merge_selected_files(self):
        """Merge files with priority-based conflict resolution"""
        if not self.idkey_file or not self.text_files:
            messagebox.showwarning("Warning", "Please select an ID/Key file and at least one Text file!")
            return
            
        self.output_text.delete(1.0, tk.END)
        log_message(self.output_text, f"ID/Key file: {os.path.basename(self.idkey_file)}")
        
        log_message(self.output_text, f"Text files list (by priority):")
        for i, f in enumerate(self.text_files):
            log_message(self.output_text, f"  [{i+1}] {os.path.basename(f)}")
            
        log_message(self.output_text, "Starting merge with priority order...")
        
        success, output_file, output_folder = self.csv_processor.merge_csv_with_priority(
            [self.idkey_file], self.text_files,
            self.smart_merge_var.get())
        
        if success:
            self.last_output_folder = output_folder
            self.open_folder_btn.config(state="normal")
            messagebox.showinfo("Success", f"Files merged successfully!\nResult saved at:\n{output_file}")
        else:
            messagebox.showerror("Error", "Could not merge files!")
            
    def open_output_folder(self):
        """Open the output folder"""
        if hasattr(self, 'last_output_folder'):
            open_folder(self.last_output_folder)
        else:
            messagebox.showwarning("Warning", "No output folder yet!")