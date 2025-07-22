import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os

def split_csv(filepath):
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
        text_path = base_name + "_text.csv"

        with open(idkey_path, 'w', encoding='utf-8') as f1:
            for meta in meta_lines:
                f1.write(meta)
            for line in ids_keys:
                f1.write(line + '\n')

        with open(text_path, 'w', encoding='utf-8') as f2:
            for text in texts:
                f2.write(text + '\n')

        messagebox.showinfo("Success", f"Split complete!\nSaved:\n{idkey_path}\n{text_path}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def merge_csv(idkey_file, text_file):
    try:
        with open(idkey_file, encoding='utf-8') as f1:
            lines = f1.readlines()

        meta_lines = [line for line in lines if line.startswith(';')]
        data_lines = [line for line in lines if not line.startswith(';')]

        with open(text_file, encoding='utf-8') as f2:
            texts = [line.strip() for line in f2.readlines()]

        if len(data_lines) != len(texts):
            messagebox.showerror("Error", "Mismatch in number of lines between ID/Key and Text files.")
            return

        merged_lines = []
        for idline, text in zip(data_lines, texts):
            merged = idline.strip() + '|' + text
            merged_lines.append(merged)

        output_path = os.path.splitext(idkey_file)[0] + "_merged.csv"
        with open(output_path, 'w', encoding='utf-8') as f:
            for meta in meta_lines:
                f.write(meta)
            for line in merged_lines:
                f.write(line + '\n')

        messagebox.showinfo("Success", f"Merged file saved to:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

def select_file_split():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if file_path:
        split_csv(file_path)

def select_files_merge():
    idkey_path = filedialog.askopenfilename(title="Select ID/Key File", filetypes=[("CSV Files", "*.csv")])
    if not idkey_path:
        return
    text_path = filedialog.askopenfilename(title="Select Text File", filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv")])
    if not text_path:
        return
    merge_csv(idkey_path, text_path)

# GUI
root = tk.Tk()
root.title("W3Strings CSV Split/Merge Tool")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

split_btn = tk.Button(frame, text="🔪 Split CSV into ID/Key + Text", command=select_file_split, width=40)
split_btn.pack(pady=10)

merge_btn = tk.Button(frame, text="🔗 Merge ID/Key + Text into CSV", command=select_files_merge, width=40)
merge_btn.pack(pady=10)

root.mainloop()
