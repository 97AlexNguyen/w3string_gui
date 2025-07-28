🧰 W3StringsGUI - Advanced Tool for Witcher 3 Modding
W3StringsGUI is an advanced graphical tool specifically designed for modders and translators working with .w3strings files in The Witcher 3. These files contain all the in-game text such as quests, UI, dialogue, and more.

Instead of using complex command-line tools, this app provides a modern UI with dedicated tabs for each task.

✨ Key Features
🔓 Decode Tab - Decode Files
Decode multiple .w3strings files into CSV at once

Supports drag-and-drop directly into the interface

Verbose option to show detailed processing logs

Context menu for each file (open, copy path, remove from list)

🔒 Encode Tab - Encode Files
Encode multiple CSV files into .w3strings

ID Space option for custom mods

Force ignore ID space check for special cases

Multiple verbosity levels (None, Verbose, Very Verbose)

🛠️ CSV Tools Tab - Advanced CSV Utilities
🔪 Advanced Split - 5 Powerful Splitting Modes:
🔄 Basic Split: Traditional split into ID/Key + Text

🔢 By ID Range: Split by numeric ID ranges (great for team collaboration)

Split by number of entries (e.g., 500 entries per file)

Limit max number of output files

Separate handling of numeric vs. text-based IDs

📏 By Text Length: Split by text length

Separate long/short texts with a customizable threshold

Useful for prioritizing complex translations

📊 By Count: Evenly split by number of entries

Balanced workload distribution

Automatically calculates required file count

🔍 By Pattern: Split by regex pattern

Filter content (e.g., dialogues vs UI text)

Supports case sensitivity toggle

Example patterns: dialog|quest, ^Hello

🔗 Priority-based Merge - Merge with Priority Handling
Merge one ID/Key file with multiple Text files

Priority System: Higher-priority files override lower ones when IDs conflict

Auto-detect format: Recognizes both ID:content and ID|content

Conflict resolution: Automatically handles duplicate IDs based on order

Move Up/Down: Easily reorder files to adjust priority

🎯 Advanced Team Workflow
Basic Workflow:
Decode .w3strings → CSV

Split CSV with preferred method

Distribute files to translation team

Merge translated files with priority system

Encode back to .w3strings

Professional Team Workflow:
By ID Range: Split by game area (each person gets a region)

By Text Length: Experts handle longer texts, newcomers handle shorter ones

By Pattern: Split by content type (dialogue, UI, quest descriptions)

Priority Merge: Lead translator has highest priority to review and override

🔧 Technical Features
User Interface:
Drag & Drop powered by tkinterdnd2

Scrollable interface for CSV Tools tab

Real-time feedback with detailed output logs

File Handling:
Batch processing for multiple files simultaneously

Robust error handling with clear feedback

Output folder tracking for quick access to results

🚀 Advantages Over Old Tools
Team collaboration: Multiple split modes designed for team efficiency

Conflict management: Auto conflict resolution via priority handling

Flexible splitting: 5 splitting modes to match all use cases

Professional workflow: Complete pipeline from split → distribute → merge with control

User-friendly: Drag & drop, context menus, tooltips, real-time output