"""
Dialog for resolving ID conflicts during merge operations
"""

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class ConflictResolutionDialog:
    """Dialog for resolving ID conflicts with detailed view and user choice"""
    
    def __init__(self, parent, idkey_conflicts, text_conflicts):
        self.parent = parent
        self.idkey_conflicts = idkey_conflicts
        self.text_conflicts = text_conflicts
        self.result = None  # Will store user choices
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Resolve Duplicate IDs")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.transient(parent)
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔍 Duplicate IDs Detected", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Info text
        total_conflicts = len(self.idkey_conflicts) + len(self.text_conflicts)
        info_text = f"Found {total_conflicts} duplicate IDs. Please choose how to resolve each ID:"
        ttk.Label(main_frame, text=info_text, foreground="orange").pack(pady=(0, 10))
        
        # Create notebook for different conflict types
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # ID/Key conflicts tab
        if self.idkey_conflicts:
            self.create_idkey_conflicts_tab(notebook)
            
        # Text conflicts tab  
        if self.text_conflicts:
            self.create_text_conflicts_tab(notebook)
        
        # Global action buttons
        action_frame = ttk.LabelFrame(main_frame, text="Global Actions", padding="10")
        action_frame.pack(fill=tk.X, pady=(0, 10))
        
        global_btn_frame = ttk.Frame(action_frame)
        global_btn_frame.pack()
        
        ttk.Button(global_btn_frame, text="📁 Prefer First File (All)", 
                  command=self.choose_all_first).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(global_btn_frame, text="📁 Prefer Last File (All)", 
                  command=self.choose_all_last).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(global_btn_frame, text="🔀 Use System Default", 
                  command=self.use_system_default).pack(side=tk.LEFT)
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="✅ Apply", 
                  command=self.apply_choices).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="❌ Cancel", 
                  command=self.cancel).pack(side=tk.RIGHT)
        
        # Initialize choices storage
        self.idkey_choices = {}
        self.text_choices = {}
        
    def create_idkey_conflicts_tab(self, notebook):
        """Create tab for ID/Key conflicts"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text=f"ID/Key Conflicts ({len(self.idkey_conflicts)})")
        
        # Create treeview for conflicts
        columns = ('ID', 'File', 'Data')
        tree = ttk.Treeview(frame, columns=columns, show='tree headings', height=15)
        
        # Configure columns
        tree.heading('#0', text='Select', anchor=tk.W)
        tree.heading('ID', text='Text ID', anchor=tk.W)
        tree.heading('File', text='Source File', anchor=tk.W)
        tree.heading('Data', text='ID/Key Data', anchor=tk.W)
        
        tree.column('#0', width=100, minwidth=80)
        tree.column('ID', width=100, minwidth=80)
        tree.column('File', width=150, minwidth=120)
        tree.column('Data', width=400, minwidth=300)
        
        # Add conflicts to tree
        for conflict_id, items in self.idkey_conflicts.items():
            parent = tree.insert('', tk.END, text=f"ID: {conflict_id}", 
                               values=(conflict_id, f"{len(items)} files", "Multiple sources"),
                               tags=('conflict_group',))
            
            for i, item in enumerate(items):
                child = tree.insert(parent, tk.END, 
                                  text=f"Option {i+1}",
                                  values=("", item['file'], item['data']),
                                  tags=('option',))
                # Store mapping for later use
                tree.set(child, 'conflict_id', conflict_id)
                tree.set(child, 'option_index', i)
        
        tree.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        tree.bind('<Double-1>', lambda e: self.on_idkey_select(tree, e))
        
        self.idkey_tree = tree
        
    def create_text_conflicts_tab(self, notebook):
        """Create tab for text conflicts"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text=f"Text Conflicts ({len(self.text_conflicts)})")
        
        # Create treeview for conflicts
        columns = ('ID', 'File', 'Content')
        tree = ttk.Treeview(frame, columns=columns, show='tree headings', height=15)
        
        # Configure columns
        tree.heading('#0', text='Select', anchor=tk.W)
        tree.heading('ID', text='Text ID', anchor=tk.W)
        tree.heading('File', text='Source File', anchor=tk.W)
        tree.heading('Content', text='Text Content', anchor=tk.W)
        
        tree.column('#0', width=100, minwidth=80)
        tree.column('ID', width=100, minwidth=80)
        tree.column('File', width=150, minwidth=120)
        tree.column('Content', width=400, minwidth=300)
        
        # Add conflicts to tree
        for conflict_id, items in self.text_conflicts.items():
            parent = tree.insert('', tk.END, text=f"ID: {conflict_id}", 
                               values=(conflict_id, f"{len(items)} files", "Multiple sources"),
                               tags=('conflict_group',))
            
            for i, item in enumerate(items):
                child = tree.insert(parent, tk.END, 
                                  text=f"Option {i+1}",
                                  values=("", item['file'], item['content'][:100] + "..." if len(item['content']) > 100 else item['content']),
                                  tags=('option',))
                # Store mapping for later use
                tree.set(child, 'conflict_id', conflict_id)
                tree.set(child, 'option_index', i)
        
        tree.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        tree.bind('<Double-1>', lambda e: self.on_text_select(tree, e))
        
        self.text_tree = tree
        
    def on_idkey_select(self, tree, event):
        """Handle ID/Key option selection"""
        item = tree.selection()[0]
        if tree.get(item, 'conflict_id'):  # Is an option, not a group
            conflict_id = tree.get(item, 'conflict_id')
            option_index = int(tree.get(item, 'option_index'))
            
            # Store choice
            self.idkey_choices[conflict_id] = option_index
            
            # Update visual feedback
            self.update_tree_selection(tree, conflict_id, option_index)
            
    def on_text_select(self, tree, event):
        """Handle text option selection"""
        item = tree.selection()[0]
        if tree.get(item, 'conflict_id'):  # Is an option, not a group
            conflict_id = tree.get(item, 'conflict_id')
            option_index = int(tree.get(item, 'option_index'))
            
            # Store choice
            self.text_choices[conflict_id] = option_index
            
            # Update visual feedback
            self.update_tree_selection(tree, conflict_id, option_index)
            
    def update_tree_selection(self, tree, conflict_id, selected_index):
        """Update visual selection in tree"""
        # Find all items for this conflict
        for child in tree.get_children():
            if tree.item(child)['values'][0] == conflict_id:
                # This is the parent group
                for option in tree.get_children(child):
                    option_index = int(tree.get(option, 'option_index'))
                    if option_index == selected_index:
                        tree.set(option, '#0', '✅ SELECTED')
                        tree.item(option, tags=('selected',))
                    else:
                        tree.set(option, '#0', '')
                        tree.item(option, tags=('option',))
                        
    def choose_all_first(self):
        """Choose first option for all conflicts"""
        for conflict_id in self.idkey_conflicts:
            self.idkey_choices[conflict_id] = 0
            if hasattr(self, 'idkey_tree'):
                self.update_tree_selection(self.idkey_tree, conflict_id, 0)
                
        for conflict_id in self.text_conflicts:
            self.text_choices[conflict_id] = 0
            if hasattr(self, 'text_tree'):
                self.update_tree_selection(self.text_tree, conflict_id, 0)
                
    def choose_all_last(self):
        """Choose last option for all conflicts"""
        for conflict_id, items in self.idkey_conflicts.items():
            last_index = len(items) - 1
            self.idkey_choices[conflict_id] = last_index
            if hasattr(self, 'idkey_tree'):
                self.update_tree_selection(self.idkey_tree, conflict_id, last_index)
                
        for conflict_id, items in self.text_conflicts.items():
            last_index = len(items) - 1
            self.text_choices[conflict_id] = last_index
            if hasattr(self, 'text_tree'):
                self.update_tree_selection(self.text_tree, conflict_id, last_index)
                
    def use_system_default(self):
        """Use system default (first option) and close dialog"""
        self.result = 'system_default'
        self.dialog.destroy()
        
    def apply_choices(self):
        """Apply user choices"""
        # Check if all conflicts have been resolved
        unresolved_idkey = set(self.idkey_conflicts.keys()) - set(self.idkey_choices.keys())
        unresolved_text = set(self.text_conflicts.keys()) - set(self.text_choices.keys())
        
        if unresolved_idkey or unresolved_text:
            unresolved_count = len(unresolved_idkey) + len(unresolved_text)
            response = messagebox.askyesno(
                "Unresolved Conflicts", 
                f"There are {unresolved_count} IDs not selected. Use default (first option) for these IDs?")
            
            if response:
                # Auto-choose first option for unresolved
                for conflict_id in unresolved_idkey:
                    self.idkey_choices[conflict_id] = 0
                for conflict_id in unresolved_text:
                    self.text_choices[conflict_id] = 0
            else:
                return
        
        # Store result and close
        self.result = {
            'idkey_choices': self.idkey_choices,
            'text_choices': self.text_choices
        }
        self.dialog.destroy()
        
    def cancel(self):
        """Cancel conflict resolution"""
        self.result = None
        self.dialog.destroy()
        
    def show(self):
        """Show dialog and return result"""
        self.parent.wait_window(self.dialog)
        return self.result