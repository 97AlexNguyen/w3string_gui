from cx_Freeze import setup, Executable
from pathlib import Path
import sys

base = "Win32GUI" if sys.platform == "win32" else None

include_files = [
    ("pyproject.toml", "pyproject.toml"),
    ("README.md", "README.md"),
]

build_exe_options = {
    "packages": ["tkinter", "sv_ttk", "tkinterdnd2", "src"],
    "include_files": include_files,
    "excludes": [
        "unittest", "pydoc", "doctest", "test", "email", "xmlrpc",
        "distutils", "urllib3", "pip", "setuptools", "numpy", "pandas",
        "matplotlib","tomllib"
    ],
    "optimize": 2,
    "silent": True
}

setup(
    name="W3StringsGUI",
    version="1.0.0.1",
    description="Witcher 3 Strings Tool GUI",
    author="Vincent",
    options={"build_exe": build_exe_options},
    executables=[
        Executable("main.py", base=base, target_name="W3StringsGUI.exe")
    ]
)
