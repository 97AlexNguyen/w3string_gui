# setup_working.py - Phiên bản hoạt động được
from cx_Freeze import setup, Executable
import sys
import os

# Nếu bạn dùng tkinter thì phải dùng base="Win32GUI" để tránh bật console
base = "Win32GUI" if sys.platform == "win32" else None

# Build options tối giản
build_exe_options = {
    # Packages cần thiết
    "packages": [
        "tkinter", 
        "sv_ttk", 
        "os", 
        "subprocess", 
        "threading", 
        "platform", 
        "pathlib", 
        "webbrowser", 
        "re",
        "sys",
        # Thêm packages từ project
        "src",
        "src.core",
        "src.gui", 
        "src.gui.tabs",
        "src.dialogs",
        "src.processors"
    ],
    
    # Không include files phức tạp
    "include_files": [],
    
    # Exclude mạnh mẽ các packages gây lỗi
    "excludes": [
        "tkinterdnd2",
        "sv_ttk", 
        "unittest", 
        "distutils", 
        "email",
        "pydoc",
        "doctest",
        "test",
        "xmlrpc",
        "urllib3",
        "pip",
        "setuptools",
        "numpy",
        "pandas",
        "matplotlib"
    ],
    
    # Silent mode
    "silent": True,
    "optimize": 1,  # Giảm optimize level
}

setup(
    name="W3StringsGUI",
    version="1.0.0",
    description="Witcher 3 Strings Tool GUI",
    author="Vincent",
    
    options={
        "build_exe": build_exe_options
    },
    
    executables=[
        Executable(
            script="main.py",
            base=base,
            target_name="W3StringsGUI.exe"
        )
    ]
)

"""
HƯỚNG DẪN:
1. python setup_working.py build
2. Exe sẽ được tạo trong build/
3. Copy w3strings_tool/ vào cùng thư mục với exe
"""