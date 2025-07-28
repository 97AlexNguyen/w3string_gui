"""
Read‑only Information tab for **W3StringsGUI**
Displays project metadata stored in **pyproject.toml → [tool.w3strings_gui]**
as static labels and provides one‑click links. No editing or saving.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from pathlib import Path
from typing import Any, Dict

# -----------------------------------------------------------------------------
# TOML loader (tomllib ≥ 3.11, fallback to toml package)
# -----------------------------------------------------------------------------
try:
    import tomllib as _toml  # Python 3.11+
except ModuleNotFoundError:
    import toml as _toml  # type: ignore


class InfoTab:
    """Static tab that *shows* project info (no edits)."""

    def __init__(self, parent: tk.Misc, notebook: ttk.Notebook) -> None:
        self.repo_root = Path(__file__).resolve().parents[3]
        self.pyproject_path = self.repo_root / "pyproject.toml"

        self._create_tab(notebook)
        self._load_info()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _create_tab(self, notebook: ttk.Notebook) -> None:
        self.frame = ttk.Frame(notebook, padding=10)
        notebook.add(self.frame, text="ℹ Info")

        self.frame.columnconfigure(1, weight=1)

        # Repository ---------------------------------------------------
        ttk.Label(self.frame, text="Repository:").grid(row=0, column=0, sticky=tk.W)
        self.repo_label = ttk.Label(self.frame, text="", cursor="hand2", foreground="#0A72DA")
        self.repo_label.grid(row=0, column=1, sticky=tk.W)
        self.repo_label.bind("<Button-1>", lambda _e: self._open_repo())

        # Contact ---------------------------------------------------
        ttk.Label(self.frame, text="Contact:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.contact_label = ttk.Label(self.frame, text="", cursor="hand2", foreground="#0A72DA")
        self.contact_label.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        self.contact_label.bind("<Button-1>", lambda _e: self._open_contact())

        # Author -------------------------------------------------------
        ttk.Label(self.frame, text="Author:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.author_label = ttk.Label(self.frame, text="")
        self.author_label.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))

        # Credits ------------------------------------------------------
        ttk.Label(self.frame, text="Credits:").grid(row=3, column=0, sticky=tk.NW, pady=(5, 0))
        self.credits_box = scrolledtext.ScrolledText(
            self.frame, width=42, height=6, wrap=tk.WORD, state="disabled"
        )
        self.credits_box.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(5, 0))

    # ------------------------------------------------------------------
    # Data handling
    # ------------------------------------------------------------------
    def _load_pyproject(self) -> Dict[str, Any]:
        if self.pyproject_path.exists():
            with open(self.pyproject_path, "rb") as f:
                return _toml.load(f)
        return {}

    def _load_info(self) -> None:
        try:
            data = (
                self._load_pyproject()
                .get("tool", {})
                .get("w3strings_gui", {})
            )
            repo = data.get("repository", "https://github.com/97AlexNguyen/w3string_gui")
            self.repo_label.config(text=repo)
            self._repo_url: str = repo

            contact = data.get("contact", "97nguyenvuquocan@gmail.com")
            self.contact_label.config(text=contact)
            self._contact_email: str = contact

            self.author_label.config(text=data.get("author", "Vincent"))

            credits = data.get("credits", "Thank you to:\n"
                                "- CD Projekt Red\n"
                                "- Nexus Mods community\n"
                                "- rmemr for w3strings encoder tool")
            self.credits_box.configure(state="normal")
            self.credits_box.delete("1.0", tk.END)
            self.credits_box.insert(tk.END, credits)
            self.credits_box.configure(state="disabled")
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Error", f"Could not read pyproject.toml: {exc}")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def _open_repo(self) -> None:
        if getattr(self, "_repo_url", ""):
            import webbrowser
            webbrowser.open(self._repo_url)
        else:
            messagebox.showinfo("Information", "No repository URL defined.")

    def _open_contact(self) -> None:
        if getattr(self, "_contact_email", ""):
            import webbrowser
            webbrowser.open(f"mailto:{self._contact_email}")
        else:
            messagebox.showinfo("Information", "No contact email defined.")
