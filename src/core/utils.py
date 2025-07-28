"""
Utility functions for the W3Strings GUI application
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from tkinter import messagebox


def get_exe_directory():
    """
    Get the directory containing the actual exe file
    Tương thích với cả script và exe build
    """
    if getattr(sys, 'frozen', False):
        # Khi chạy từ exe được build (PyInstaller, cx_Freeze, etc.)
        return Path(sys.executable).parent
    else:
        # Khi chạy từ Python script
        # Lấy thư mục chứa main.py (project root)
        if __name__ == '__main__':
            # Nếu chạy utils.py trực tiếp
            return Path(__file__).parent.parent.parent
        else:
            # Nếu import từ module khác
            # Tìm thư mục chứa main.py
            current = Path(__file__).parent
            while current.parent != current:  # Không phải root
                if (current / "main.py").exists():
                    return current
                current = current.parent
            
            # Fallback: sử dụng thư mục hiện tại
            return Path.cwd()


def get_w3strings_path():
    """
    Lấy đường dẫn đến w3strings.exe
    Cấu trúc: project_root/w3strings_tool/w3strings.exe
    """
    base_dir = get_exe_directory()
    return base_dir / "w3strings_tool" / "w3strings.exe"


def check_drag_drop_support():
    """Check if drag and drop support is available"""
    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
        return True, DND_FILES, TkinterDnD
    except ImportError:
        print("Warning: tkinterdnd2 not installed. Drag & drop feature disabled.")
        print("Install with: pip install tkinterdnd2")
        return False, None, None


def open_folder(path):
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


def open_file_with_system(file_path):
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


def copy_to_clipboard(root, text):
    """Copy text to clipboard"""
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        return True
    except Exception:
        return False


def parse_drop_files(data):
    """Parse dropped files data"""
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


def validate_file_extension(file_path, expected_extension):
    """Validate if file has expected extension"""
    return file_path.lower().endswith(expected_extension.lower().replace('*', ''))


def log_message(output_widget, message):
    """Log message to output widget"""
    output_widget.insert('end', message + "\n")
    output_widget.see('end')
    output_widget.update_idletasks()


def debug_paths():
    print("=== PATH DEBUG INFO ===")
    print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
    print(f"sys.executable: {sys.executable}")
    print(f"__file__: {__file__}")
    print(f"get_exe_directory(): {get_exe_directory()}")
    print(f"get_w3strings_path(): {get_w3strings_path()}")
    print(f"w3strings.exe exists: {get_w3strings_path().exists()}")
    print("======================")


if __name__ == "__main__":
    debug_paths()