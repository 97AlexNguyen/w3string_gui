"""
Dialog implementations package for W3Strings GUI

This package contains all dialog window implementations:
- MissingExeDialog: Dialog shown when w3strings.exe is not found
- ConflictResolutionDialog: Dialog for resolving ID conflicts during merge
"""

from .missing_exe_dialog import MissingExeDialog
from .conflict_resolution_dialog import ConflictResolutionDialog

__all__ = ['MissingExeDialog', 'ConflictResolutionDialog']