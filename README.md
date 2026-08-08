# 🎭 Mimic Python Obfuscator

[![VS Code Extension](https://img.shields.io/badge/VS_Code-Extension-blue?logo=visual-studio-code&logoColor=white)](https://code.visualstudio.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python Support](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Downloads](https://img.shields.io/badge/downloads-v1.0.2-orange)](https://github.com/w4simg/mimic/releases/latest)

A professional, AST-based Python code obfuscation extension for Visual Studio Code. Protect your Python source code, proprietary algorithms, and IP from reverse engineering with advanced obfuscation techniques.

---

### [📦 Download the Latest VSIX Extension (v1.0.2)](https://github.com/w4simg/mimic/releases/download/v1.0.2/mimic-obfuscator-1.0.2.vsix)

---

## ✨ Features

- **AST-Based Obfuscation:** Safely parses and modifies Python Abstract Syntax Trees (AST) rather than simple regex or string replacement, ensuring syntactical correctness.
- **Multiple Obfuscation Levels:** Choose from Basic (stripping documentation) to Extreme (control-flow flattening and anti-AI renaming).
- **Custom Identifier Renaming Styles:** Rename variables, functions, and classes with confusing, hexadecimal, or Chinese/English mixed characters.
- **Flexible Scope:** Obfuscate a single Python file or an entire project directory recursively.
- **VS Code Context Menu Integration:** Trigger obfuscation directly from the explorer tree or editor window.
- **100% Offline & Secure:** All obfuscation runs entirely locally on your machine. Your source code never leaves your computer.

---

## 🚀 How to Install

You can install the `.vsix` file in either of two ways:

### Option A: Via VS Code UI (Recommended)
1. Open Visual Studio Code.
2. Open the Extensions View (`Ctrl+Shift+X` or `Cmd+Shift+X`).
3. Click the `...` (More Actions) button in the top-right corner of the Extensions panel.
4. Select **Install from VSIX...** from the dropdown menu.
5. Choose the downloaded `mimic-obfuscator-1.0.0.vsix` file and click **Install**.

### Option B: Via Command Line
Run the following command in your terminal:
```bash
code --install-extension mimic-obfuscator-1.0.0.vsix
```

---

## 📖 How to Use

### 1. Obfuscating a Single File
1. **Open any Python file (`.py`)** in your VS Code editor.
2. **Right-click** anywhere in the editor window (or on the file in the Explorer panel).
3. Select **`Mimic: Obfuscate File...`** from the context menu.
4. Choose your desired **Obfuscation Level** and **Renaming Style**.
5. Select the destination file path when prompted (suggests `<filename>_obf.py` by default).

### 2. Obfuscating an Entire Project Folder
1. Locate the folder you want to obfuscate in the VS Code **Explorer panel**.
2. **Right-click** on the folder.
3. Select **`Mimic: Obfuscate Project Folder...`** from the context menu.
4. Select your **Obfuscation Level** and **Renaming Style**.
5. Enter the destination folder path (suggests `<foldername>_obf` by default).

---

## ⚙️ Extension Settings

Mimic allows you to customize the Python interpreter path if it differs from the system default.

1. Open VS Code Settings (`Ctrl+,` or `Cmd+,`).
2. Search for `Mimic` or go to `Extensions` > `Mimic Python Obfuscator`.
3. Configure:
   - **`mimic.pythonPath`**: Specify the absolute path to your Python executable (e.g., `/usr/bin/python3`, `C:\Python39\python.exe`, or a path to a virtual environment python). Defaults to the standard `python` command in your system PATH.

---

## 🛠️ Obfuscation Options

### Obfuscation Levels

| Level | Name | Description |
|---|---|---|
| **1** | **Basic** | Strips comments and docstrings. Keeps identifiers unchanged. |
| **2** | **Medium** | Strips comments/docstrings, renames local variables, and escapes string literals. |
| **3** | **Strong** | Strips comments/docstrings, renames both global and local identifiers, and XOR encrypts string literals. |
| **4** | **Extreme** | Strong + control flow flattening + math obfuscation + builtin function hiding (anti-decompiler & anti-AI analysis). |

### Renaming Styles

- **Hexadecimal:** Renames identifiers into hexadecimal representations (e.g., `_0x1a3b`).
- **Confusing:** Uses lookalike characters like `l`, `1`, `O`, `0`, and `I` to make variable names indistinguishable (e.g., `lO1lIO`).
- **Mixed Chinese/English:** Blends Chinese characters with English characters (e.g., `极_l1O`) to disrupt readability and confuse AI analysis models.

---

## 📝 Example Comparison (Confusing Style)

### Original Code
```python
def calculate_area(width, height):
    """Calculates the area of a rectangle."""
    # Multiply width and height
    area = width * height
    return area
```

### Obfuscated Code
```python
def lO1lIO(lOIIlO, lIlIlO):
    lO11IO = lOIIlO * lIlIlO
    return lO11IO
```

---

## 📄 License

This extension is released under the [MIT License](LICENSE).
