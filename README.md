# BillManager

BillManager is a Windows desktop billing system built with PyQt5. It is designed for small shops that need to keep shop details, generate receipts, and maintain separate receipt numbers for each shop.

## What it does

- Creates and stores shop profiles with name, owner, address, and mobile numbers
- Opens a receipt window for the selected shop
- Adds item details, buyer details, date, quantity, and price
- Generates printable receipts
- Supports receipt numbers in the format `FixedSerial_CustomNumber`
- Keeps receipt serial numbers separately for each shop

## How it works

1. Launch the app from `main.py`.
2. The main window lists recent shops from the `data/` folder.
3. Create a new shop or edit/delete an existing one.
4. Open a shop to use the receipt form.
5. The receipt form loads shop info and increments that shop's serial number.

## Main files

- `main.py` starts the application
- `main_window.py` shows the shop selection screen
- `create_shop_window.py` creates and edits shop profiles
- `receipt_form.py` handles receipt entry and printing
- `path_utilis.py` manages the app data path
- `BillManager.spec` is the PyInstaller build file

## Data storage

- Shop data is saved in `data/<shop name>/shop_info.json`
- Each shop also has `serial_numbers.txt` for receipt numbering
- When packaged as an EXE, data is stored in the user's local AppData folder

## Requirements

- Python 3
- PyQt5
- pywin32

## Run

```bash
python main.py
```

## Build

Use `BillManager.spec` with PyInstaller if you want to create a Windows executable.
