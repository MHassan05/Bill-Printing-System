# BillManager

BillManager is a Windows desktop billing application built with PyQt5 for small businesses that need:

- Shop profile management
- Fast receipt generation and preview
- Thermal printing support
- PDF export
- Per-shop serial number tracking

## Project Review (Architecture + Behavior)

This repository is a single-process desktop GUI app with file-based persistence.

### Core flow

1. App starts from `main.py`.
2. `MainWindow` (`main_window.py`) loads shop folders from `data/`.
3. User can create, edit, delete, or open a shop.
4. `ReceiptFormApp` (`receipt_form.py`) handles item entry, receipt preview, print, and PDF export.
5. Serial numbers are tracked per shop in `serial_numbers.txt`.

### Module-by-module summary

- `main.py`

  - App entry point.
  - Creates `QApplication`, opens `MainWindow`.
- `main_window.py`

  - Shop selection dashboard.
  - Reads `shop_info.json` from each shop directory.
  - Supports create/edit/delete/open actions.
  - Uses `ClickableWidget` to support row selection and hover effects.
- `create_shop_window.py`

  - Create and edit form for shop metadata.
  - Validates required fields.
  - Enforces up to 3 mobile numbers; each must be numeric and 11 digits.
  - Renames shop folder when shop name changes in edit mode.
- `receipt_form.py`

  - Main billing UI (item input, list, receipt preview).
  - Manages per-shop serial numbers through `SerialNumberManager`.
  - Prints receipts via Qt printer APIs.
  - Uses Windows printer APIs (`win32print`) for printer discovery and optional cut command.
  - Exports receipt to PDF and stores PDF save path in `shop_info.json`.
- `path_utilis.py`

  - Centralized base path resolver.
  - In source mode: uses repository directory.
  - In PyInstaller-frozen mode: uses `%LOCALAPPDATA%/BillManager` and copies bundled `data` on first run.
- `BillManager.spec`

  - PyInstaller spec.
  - Bundles `data/` and `ui/` folders into distribution.

### Data model and storage

Per shop directory structure:

```text
data/<shop_name>/
	shop_info.json
	serial_numbers.txt 
```

`shop_info.json` keys used by code:

- `shop_name`
- `owner_name`
- `address`
- `mobile_numbers` (list)
- `pdf_path` (optional, added/updated from receipt form)

`serial_numbers.txt`:

- Stores current committed serial as an integer.
- Next shown serial in UI is `current + 1`, zero-padded to 6 digits.

### Platform notes

- This project is Windows-oriented because of `pywin32` and `win32print` usage.
- Linux/macOS may require code changes for printer enumeration and cut-command handling.

## Requirements

Runtime dependencies are listed in `requirements.txt`.

- Python 3.10+ recommended
- PyQt5
- pywin32

## Setup

1. Create and activate a virtual environment (recommended).

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install project dependencies from `requirements.txt`:

```powershell
pip install -r requirements.txt
```

3. Run the app:

```powershell
python main.py
```

## How to use the app

1. Launch the app.
2. Click `+ Create New Shop` to create a shop profile.
3. Fill shop details and save.
4. Select a shop from `Recent Shops`.
5. Add item name, buyer, quantity, and price.
6. Use:
   - `Add Item` to build receipt lines
   - `Print Receipt` to print
   - `Save as PDF` to export
   - `Update Serial #` to adjust base serial when needed

## Build executable (optional, no .spec file required)

Install PyInstaller and build directly from `main.py`:

```powershell
pip install pyinstaller
pyinstaller --name BillManager --windowed --onedir --add-data "data;data" --add-data "ui;ui" main.py
```

Generated executable output is placed in `dist/BillManager/`.

## Current strengths

- Clear separation between shop selection, shop management, and receipt operations.
- Per-shop serial tracking is simple and understandable.
- File-based persistence makes backups straightforward.
- Works both in source mode and packaged mode through `get_base_path()`.

## Known limitations

- No automated tests yet.
- Data validation is UI-driven; no schema layer.
- Concurrent/multi-user writes to the same shop files are not handled.
- Some import/style cleanup opportunities exist (non-blocking).
