# Mimic Python Obfuscator

A professional AST-based Python code obfuscation extension for Visual Studio Code. Protect your Python source code, IP, and proprietary algorithms from reverse engineering with advanced obfuscation techniques.

---

## Features

- **AST-Based Obfuscation:** Safely parses and modifies Python Abstract Syntax Trees (AST) rather than simple regex or string replacement, ensuring syntactical correctness.
- **Multiple Obfuscation Levels:** Choose from Basic (stripping documentation) to Extreme (control-flow flattening and anti-AI renaming).
- **Custom Identifier Renaming Styles:** Rename variables, functions, and classes with confusing, hexadecimal, or Chinese/English mixed characters.
- **Flexible Scope:** Obfuscate a single Python file or an entire project directory recursively.
- **Visual Studio Code Context Menu Integration:** Trigger obfuscation directly from the explorer tree or editor window.

---

## How to Use

### 1. Obfuscating a Single File
You can obfuscate any open Python (`.py`) file:

1. **Open a Python file** in your VS Code editor.
2. **Right-click** anywhere in the editor window or on the file in the Explorer panel.
3. Select **`Mimic: Obfuscate File...`** from the context menu.
4. **Choose your Obfuscation Level** (see details below).
5. **Choose your Identifier Renaming Style** (see details below).
6. A dialog box will prompt you to select where to save the obfuscated file. By default, it suggests saving it as `<filename>_obf.py` in the same directory.

---

### 2. Obfuscating an Entire Project Folder
To protect a complete module or folder structure recursively:

1. Locate the folder you want to obfuscate in the VS Code **Explorer panel**.
2. **Right-click** on the folder.
3. Select **`Mimic: Obfuscate Project Folder...`** from the context menu.
4. Select your desired **Obfuscation Level** and **Renaming Style**.
5. Enter the path for the destination folder when prompted. By default, it suggests `<foldername>_obf` at the same hierarchy level.

---

## Obfuscation Options

### Obfuscation Levels

| Level | Name | Description |
|---|---|---|
| **1** | **Basic** | Strips comments and docstrings. Keeps identifiers unchanged. |
| **2** | **Medium** | Strips comments/docstrings, renames local variables, and escapes string literals. |
| **3** | **Strong** | Strips comments/docstrings, renames both global and local identifiers, and XOR encrypts string literals. |
| **4** | **Extreme** | strong + control flow flattening + math obfuscation + builtin function hiding (anti-decompiler & anti-AI analysis). |

### Renaming Styles

- **Hexadecimal:** Renames identifiers into hexadecimal representations (e.g., `_0x1a3b`).
- **Confusing:** Uses lookalike characters like `l`, `1`, `O`, `0`, and `I` to make variable names indistinguishable (e.g., `lO1lIO`).
- **Mixed Chinese/English:** Blends Chinese characters with English characters (e.g., `极_l1O`) to disrupt readability and confuse AI analysis models.

---

## Extension Settings

Mimic allows you to customize the Python interpreter path if it differs from the system default.

To configure this:
1. Open VS Code Settings (`Ctrl+,` or `Cmd+,`).
2. Search for `Mimic` or go to `Extensions` > `Mimic Python Obfuscator`.
3. Configure the following setting:
   - **`mimic.pythonPath`**: Specify the absolute path to your Python executable (e.g., `/usr/bin/python3`, `C:\Python39\python.exe`, or a path to a virtual environment python). If left empty, it defaults to the `python` command in your system PATH.
