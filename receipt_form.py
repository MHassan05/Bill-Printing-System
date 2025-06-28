import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QFormLayout, QLineEdit, QPushButton, 
                             QTextEdit, QListWidget, QLabel, QDoubleSpinBox, 
                             QMessageBox, QListWidgetItem, QFrame, QSplitter,
                             QComboBox, QFileDialog, QCheckBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextDocument
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog
from datetime import datetime
import win32print
import json
import path_utilis
from PyQt5.QtCore import QSizeF

class Item:
    def __init__(self, name, quantity, price):
        self.name = name
        self.quantity = quantity
        self.price = price
        self.total = quantity * price

class SerialNumberManager:
    def __init__(self, shop_folder_path):
        self.shop_folder_path = shop_folder_path
        self.serial_file = os.path.join(shop_folder_path, 'serial_numbers.txt')
        self.current_serial = self.load_serial_number()
        
    
    def load_serial_number(self):
        try:
            if os.path.exists(self.serial_file):
                with open(self.serial_file, 'r') as f:
                    return int(f.read().strip())
            else:
                # Initialize with serial number 0 (first receipt will be 0001)
                self.save_serial_number(0)
                return 0
        except:
            return 0
    
    def save_serial_number(self, serial):
        try:
            # Ensure the shop folder exists
            os.makedirs(self.shop_folder_path, exist_ok=True)
            with open(self.serial_file, 'w') as f:
                f.write(str(serial))
        except Exception as e:
            print(f"Error saving serial number: {e}")
    
    def get_next_serial(self):
        # Increment the counter first, then return the formatted number
        self.current_serial += 1
        self.save_serial_number(self.current_serial)
        return str(self.current_serial).zfill(6)  # Pad with zeros to make 6 digits (000001, 0002, etc.)

class ReceiptFormApp(QMainWindow):
    def __init__(self, shop_folder=None):
        super().__init__()
        self.base_path = path_utilis.get_base_path()
        self.shop_folder = shop_folder
        self.shop_info = self.load_shop_info()
        
        # Set up serial number manager with shop-specific path
        if shop_folder:
            shop_folder_path = os.path.join(self.base_path, 'data', shop_folder)
        else:
            shop_folder_path = self.base_path
        
        self.serial_manager = SerialNumberManager(shop_folder_path)
        self.receipt_serial = self.serial_manager.get_next_serial()
        self.items = []
        self.available_printers = self.get_available_printers()
        self.init_ui()
    
    def load_shop_info(self):
        """Load shop information from shop_info.json"""
        if not self.shop_folder:
            return {
                "shop_name": "Default Shop",
                "owner_name": "N/A",
                "address": "N/A",
                "mobile_numbers": []
            }
        
        try:
            shop_path = os.path.join(self.base_path, 'data', self.shop_folder)
            info_path = os.path.join(shop_path, 'shop_info.json')
            
            if os.path.exists(info_path):
                with open(info_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading shop info: {e}")
        
        # Return default if loading fails
        return {
            "shop_name": "Unknown Shop",
            "owner_name": "N/A",
            "address": "N/A",
            "mobile_numbers": []
        }
        
    def get_available_printers(self):
        """Get list of available printers on the system"""
        try:
            printers = []
            printer_info = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
            for printer in printer_info:
                printers.append(printer[2])  # Printer name is at index 2
            return printers
        except Exception as e:
            print(f"Error getting printers: {e}")
            return ["Default Printer"]
        
    def init_ui(self):
        # Update window title to include shop name
        self.setWindowTitle(f"Receipt Form - {self.shop_info['shop_name']}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create splitter for resizable panes
        splitter = QSplitter(Qt.Horizontal)
        central_widget_layout = QHBoxLayout(central_widget)
        central_widget_layout.addWidget(splitter)
        
        # Left side widget
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Right side widget (Receipt preview)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 600])  # Equal sizes initially
        
        # === LEFT SIDE - SHOP INFO AND FORM ===
        
        # Shop info section
        shop_info_frame = QFrame()
        shop_info_frame.setFrameStyle(QFrame.Box)
        shop_info_frame.setStyleSheet("QFrame { background-color: #f0f8ff; border: 2px solid #4682b4; }")
        shop_info_layout = QVBoxLayout(shop_info_frame)
        
        # Shop info title
        shop_title = QLabel("SHOP INFORMATION")
        shop_title.setFont(QFont("Arial", 12, QFont.Bold))
        shop_title.setAlignment(Qt.AlignCenter)
        shop_title.setStyleSheet("QLabel { color: #2c3e50; background-color: transparent; }")
        shop_info_layout.addWidget(shop_title)
        
        # Shop details
        shop_name_label = QLabel(f"Shop Name: {self.shop_info['shop_name']}")
        shop_name_label.setFont(QFont("Arial", 10, QFont.Bold))
        shop_name_label.setStyleSheet("QLabel { color: #2c3e50; background-color: transparent; }")
        
        owner_label = QLabel(f"Owner: {self.shop_info['owner_name']}")
        owner_label.setStyleSheet("QLabel { color: #2c3e50; background-color: transparent; }")
        
        address_label = QLabel(f"Address: {self.shop_info['address']}")
        address_label.setStyleSheet("QLabel { color: #2c3e50; background-color: transparent; }")
        
        mobile_numbers = " | ".join(self.shop_info.get('mobile_numbers', []))
        mobile_label = QLabel(f"Mobile: {mobile_numbers}")
        mobile_label.setStyleSheet("QLabel { color: #2c3e50; background-color: transparent; }")
        
        shop_info_layout.addWidget(shop_name_label)
        shop_info_layout.addWidget(owner_label)
        shop_info_layout.addWidget(address_label)
        shop_info_layout.addWidget(mobile_label)
        
        left_layout.addWidget(shop_info_frame)
        
        # Form section
        form_frame = QFrame()
        form_frame.setFrameStyle(QFrame.Box)
        form_layout = QVBoxLayout(form_frame)
        
        # Form title
        form_title = QLabel("Add Item Details")
        form_title.setFont(QFont("Arial", 14, QFont.Bold))
        form_title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(form_title)
        
        # Form fields
        fields_layout = QFormLayout()
        
        self.item_name_input = QLineEdit()
        self.item_name_input.setPlaceholderText("Enter item name")
        fields_layout.addRow("Item Name:", self.item_name_input)
        
        self.buyer_name_input = QLineEdit()
        self.buyer_name_input.setPlaceholderText("Enter buyer name")
        fields_layout.addRow("Buyer Name:", self.buyer_name_input)
        
        self.quantity_input = QDoubleSpinBox()
        self.quantity_input.setMinimum(0.01)
        self.quantity_input.setMaximum(999999.99)
        self.quantity_input.setDecimals(2)
        self.quantity_input.setValue(1.00)
        fields_layout.addRow("Quantity:", self.quantity_input)
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0.01)
        self.price_input.setMaximum(999999.99)
        self.price_input.setDecimals(2)
        self.price_input.setValue(0.00)
        fields_layout.addRow("Price (RS):", self.price_input)
        
        form_layout.addLayout(fields_layout)
        
        # Form buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Item")
        self.add_button.clicked.connect(self.add_item)
        self.add_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
        
        self.clear_button = QPushButton("Clear Form")
        self.clear_button.clicked.connect(self.clear_form)
        self.clear_button.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 8px; }")
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.clear_button)
        form_layout.addLayout(button_layout)
        
        # Items list section
        items_frame = QFrame()
        items_frame.setFrameStyle(QFrame.Box)
        items_layout = QVBoxLayout(items_frame)
        
        items_title = QLabel("Added Items")
        items_title.setFont(QFont("Arial", 12, QFont.Bold))
        items_title.setAlignment(Qt.AlignCenter)
        items_layout.addWidget(items_title)
        
        self.items_list = QListWidget()
        self.items_list.itemClicked.connect(self.edit_item)
        items_layout.addWidget(self.items_list)
        
        # List buttons
        list_button_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.clicked.connect(self.edit_selected_item)
        self.edit_button.setEnabled(False)
        
        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected_item)
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
        
        list_button_layout.addWidget(self.edit_button)
        list_button_layout.addWidget(self.delete_button)
        items_layout.addLayout(list_button_layout)
        
        # Add form and items list to left layout
        left_layout.addWidget(form_frame)
        left_layout.addWidget(items_frame)
        
        # === RIGHT SIDE - RECEIPT PREVIEW ===
        
        receipt_title = QLabel("Receipt Preview")
        receipt_title.setFont(QFont("Arial", 14, QFont.Bold))
        receipt_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(receipt_title)
        
        self.receipt_preview = QTextEdit()
        self.receipt_preview.setReadOnly(True)
        self.receipt_preview.setFont(QFont("Courier", 9))
        right_layout.addWidget(self.receipt_preview)
        
        # Print settings group
        print_group = QGroupBox("Print & Save Settings")
        print_layout = QVBoxLayout(print_group)
        
        # Printer selection
        printer_layout = QHBoxLayout()
        printer_layout.addWidget(QLabel("Printer:"))
        self.printer_combo = QComboBox()
        self.printer_combo.addItems(self.available_printers)
        printer_layout.addWidget(self.printer_combo)
        print_layout.addLayout(printer_layout)
        
        # PDF save location - default to shop folder
        pdf_layout = QHBoxLayout()
        pdf_layout.addWidget(QLabel("PDF Save Location:"))
        self.pdf_path_input = QLineEdit()
        self.pdf_path_input.setPlaceholderText("Choose folder to save PDF")
        
        # Set default PDF save location to shop folder or Documents
        if self.shop_folder:
            default_pdf_path = os.path.join(self.base_path, 'data', self.shop_folder)
        else:
            default_pdf_path = os.path.expanduser("~/Documents")
        self.pdf_path_input.setText(default_pdf_path)
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_pdf_location)
        pdf_layout.addWidget(self.pdf_path_input)
        pdf_layout.addWidget(self.browse_button)
        print_layout.addLayout(pdf_layout)
        
        right_layout.addWidget(print_group)
        
        # Receipt buttons
        receipt_button_layout = QHBoxLayout()
        
        self.print_button = QPushButton("Print Receipt")
        self.print_button.clicked.connect(self.print_receipt)
        self.print_button.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 8px; }")
        
        self.save_pdf_button = QPushButton("Save as PDF")
        self.save_pdf_button.clicked.connect(self.save_as_pdf)
        self.save_pdf_button.setStyleSheet("QPushButton { background-color: #9C27B0; color: white; font-weight: bold; padding: 8px; }")
        
        self.clear_receipt_button = QPushButton("Clear All Items")
        self.clear_receipt_button.clicked.connect(self.clear_all_items)
        self.clear_receipt_button.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-weight: bold; padding: 8px; }")

        self.update_serial_button = QPushButton("Update Serial #")
        self.update_serial_button.clicked.connect(self.update_serial_number)
        self.update_serial_button.setStyleSheet("QPushButton { background-color: #607D8B; color: white; font-weight: bold; padding: 8px; }")
        
        receipt_button_layout.addWidget(self.print_button)
        receipt_button_layout.addWidget(self.save_pdf_button)
        receipt_button_layout.addWidget(self.clear_receipt_button)
        receipt_button_layout.addWidget(self.update_serial_button)
        right_layout.addLayout(receipt_button_layout)
        
        # Connect list selection change
        self.items_list.itemSelectionChanged.connect(self.on_selection_changed)

        self.update_receipt_preview()

    def update_serial_number(self):
        """Update receipt serial number"""
        from PyQt5.QtWidgets import QInputDialog, QMessageBox
        
        current_serial = self.serial_manager.current_serial
        new_serial, ok = QInputDialog.getInt(
            self, 
            "Update Serial Number", 
            f"Current serial: {current_serial:06d} (Next: {(current_serial + 1):06d})\n\n"
            f"Set new base serial number:",
            value=current_serial,
            min=0,
            max=999999
        )
        
        if ok:
            # Update the serial manager
            self.serial_manager.current_serial = new_serial
            self.serial_manager.save_serial_number(new_serial)
            
            # Update current receipt display
            self.receipt_serial = str(new_serial + 1).zfill(6)
            self.update_receipt_preview()
            
            QMessageBox.information(self, "Serial Updated", 
                                f"Serial number updated!\n"
                                f"Next receipt will be: {self.receipt_serial}")
        
    def add_item(self):
        # Validate inputs
        if not self.item_name_input.text().strip():
            QMessageBox.warning(self, "Error", "Please enter an item name.")
            return
            
        if not self.buyer_name_input.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a buyer name.")
            return
            
        if self.price_input.value() <= 0:
            QMessageBox.warning(self, "Error", "Please enter a valid price.")
            return
        
        # Create item
        item = Item(
            name=self.item_name_input.text().strip(),
            quantity=self.quantity_input.value(),
            price=self.price_input.value()
        )
        
        self.items.append(item)
        self.update_items_list()
        self.update_receipt_preview()
        self.clear_form()
        
    def clear_form(self):
        self.item_name_input.clear()
        self.quantity_input.setValue(1.00)
        self.price_input.setValue(0.00)
        
    def update_items_list(self):
        self.items_list.clear()
        for i, item in enumerate(self.items):
            item_text = f"{item.name} - Qty: {item.quantity} - RS{item.total:.2f}"
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.UserRole, i)  # Store index
            self.items_list.addItem(list_item)
            
    def edit_item(self, item):
        self.edit_selected_item()
        
    def edit_selected_item(self):
        current_item = self.items_list.currentItem()
        if current_item:
            index = current_item.data(Qt.UserRole)
            item = self.items[index]
            
            # Populate form with selected item data
            self.item_name_input.setText(item.name)
            self.quantity_input.setValue(item.quantity)
            self.price_input.setValue(item.price)
            
            # Remove item from list (will be re-added when form is submitted)
            self.items.pop(index)
            self.update_items_list()
            self.update_receipt_preview()
            
    def delete_selected_item(self):
        current_item = self.items_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, "Confirm Delete", 
                                       "Are you sure you want to delete this item?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                index = current_item.data(Qt.UserRole)
                self.items.pop(index)
                self.update_items_list()
                self.update_receipt_preview()
                
    def on_selection_changed(self):
        has_selection = bool(self.items_list.currentItem())
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        
    def update_receipt_preview(self):
        if not self.items:
            self.receipt_preview.setPlainText("No items added yet.")
            return
    
        def wrap_text(text, width):
            """Wrap text to fit within specified width"""
            if len(text) <= width:
                return [text]
            
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= width:
                    current_line += (" " + word) if current_line else word
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            return lines
        
        def center_text(text, width):
                """Center text within specified width"""
                return text.center(width)
            
        def format_long_text(text, width, center=False):
                """Format long text with wrapping and optional centering"""
                lines = wrap_text(text, width)
                if center:
                    return [center_text(line, width) for line in lines]
                return lines
                
        receipt_text = "=" * 32 + "\n"
            
        # Shop name - centered and wrapped
        shop_name_lines = format_long_text(self.shop_info['shop_name'].upper(), 32, center=True)
        for line in shop_name_lines:
            receipt_text += line + "\n"
        
        receipt_text += "=" * 32 + "\n"
        
        # Owner - wrapped if too long
        owner_lines = format_long_text(f"Owner: {self.shop_info['owner_name']}", 32)
        for line in owner_lines:
            receipt_text += line + "\n"
        
        # Address - wrapped if too long
        address_lines = format_long_text(f"Address: {self.shop_info['address']}", 32)
        for line in address_lines:
            receipt_text += line + "\n"
        
        # Mobile numbers - wrapped if too long
        mobile_numbers = " | ".join(self.shop_info.get('mobile_numbers', []))
        if mobile_numbers:
            mobile_lines = format_long_text(f"Mobile: {mobile_numbers}", 32)
            for line in mobile_lines:
                receipt_text += line + "\n"
        
        receipt_text += "=" * 32 + "\n"
        
        # Buyer - wrapped if too long
        buyer_lines = format_long_text(f"Buyer: {self.buyer_name_input.text().strip()}", 32)
        for line in buyer_lines:
            receipt_text += line + "\n"
        
        receipt_text += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        receipt_text += f"Receipt #: {self.receipt_serial}\n"
        receipt_text += "-" * 32 + "\n\n"
        
        # Table header
        receipt_text += f"{'Item Name':<18} {'Qty':<4} {'Price'}\n"
        receipt_text += "-" * 32 + "\n"
        
        total_amount = 0
        for item in self.items:
            # Handle long item names
            item_name_lines = wrap_text(item.name, 12)
            
            # First line with quantity and price
            receipt_text += f"{item_name_lines[0]:<18} {item.quantity:<4} {item.total}\n"
            
            # Additional lines for long item names (if any)
            for line in item_name_lines[1:]:
                receipt_text += f"{line:<18} {'':<4} {''}\n"
            
            total_amount += item.total
            
        receipt_text += "-" * 32 + "\n"
        receipt_text += f"GRAND TOTAL:\tRS{total_amount:.2f}\n"
        receipt_text += "=" * 32 + "\n"
        
        # Thank you message - centered
        thank_you_lines = format_long_text("Thank you for your purchase!", 32, center=True)
        for line in thank_you_lines:
            receipt_text += line + "\n"
        
        receipt_text += "=" * 32 + "\n\n\n\f"
        
        self.receipt_preview.setPlainText(receipt_text)
        
    def browse_pdf_location(self):
        """Browse for PDF save location"""
        folder = QFileDialog.getExistingDirectory(self, "Select PDF Save Location", 
                                                 self.pdf_path_input.text())
        if folder:
            self.pdf_path_input.setText(folder)
    
    def get_receipt_html(self):
        """Generate HTML version of receipt for printing/PDF"""
        if not self.items:
            return "<html><body><p>No items to print.</p></body></html>"
        
        mobile_numbers = " | ".join(self.shop_info.get('mobile_numbers', []))
        
        html = """
        <html>
        <head>
            <style>
                body { font-family: 'Courier New', monospace; font-size: 12px; margin: 10px; }
                .shop-header { text-align: center; font-weight: bold; border-bottom: 2px solid black; padding-bottom: 10px; margin-bottom: 10px; }
                .shop-info { text-align: center; margin-bottom: 10px; }
                .receipt-info { text-align: center; margin-bottom: 15px; border-bottom: 1px solid #ccc; padding-bottom: 10px; }
                .items-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
                .items-table th, .items-table td { border: 1px solid #ccc; padding: 5px; text-align: left; }
                .items-table th { background-color: #f0f0f0; font-weight: bold; }
                .total { font-weight: bold; font-size: 14px; text-align: right; margin-top: 20px; }
                .footer { text-align: center; margin-top: 20px; border-top: 2px solid black; padding-top: 10px; }
            </style>
        </head>
        <body>
        """
        
        html += f"""
        <div class="shop-header">
            <h2>{self.shop_info['shop_name'].upper()}</h2>
        </div>
        <div class="shop-info">
            <p><strong>Owner:</strong> {self.shop_info['owner_name']}</p>
            <p><strong>Address:</strong> {self.shop_info['address']}</p>"""
        
        if mobile_numbers:
            html += f"<p><strong>Mobile:</strong> {mobile_numbers}</p>"
        
        html += f"""
        </div>
        <div class="receipt-info">
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Receipt #:</strong> {self.receipt_serial}</p>
        </div>
        
        <table class="items-table">
            <tr>
                <th>Item Name</th>
                <th>Quantity</th>
                <th>Price</th>
            </tr>
        """
        
        total_amount = 0
        for item in self.items:
            html += f"""
            <tr>
                <td>{item.name}</td>
                <td>{item.quantity}</td>
                <td>RS{item.total:.2f}</td>
            </tr>
            """
            total_amount += item.total
        
        html += f"""
        </table>
        <div class="total">
            <h3>GRAND TOTAL: RS{total_amount:.2f}</h3>
        </div>
        <div class="footer">
            <p>Thank you for your purchase!</p>
        </div>
        </body>
        </html>
        """
        
        return html
    
    def print_receipt(self):
        """Print receipt optimized for thermal printers"""
        if not self.items:
            QMessageBox.information(self, "Info", "No items to print.")
            return

        try:
            # Get the plain text version (what you see in preview)
            receipt_text = self.receipt_preview.toPlainText()
            
            printer = QPrinter()
            
            # Set printer name if selected
            if self.printer_combo.currentText() != "Default Printer":
                printer.setPrinterName(self.printer_combo.currentText())
            
            # Configure printer settings BEFORE print dialog
            printer.setPaperSize(QPrinter.Custom)
            printer.setPaperSize(QSizeF(80, 150), QPrinter.Millimeter)  # Fixed height
            printer.setOrientation(QPrinter.Portrait)  # Changed from setPageOrientation
            printer.setFullPage(True)  # Use full page area
            printer.setPageMargins(2, 2, 2, 2, QPrinter.Millimeter)
            
            # Show print dialog
            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec_() == QPrintDialog.Accepted:
                # Use plain text instead of HTML
                document = QTextDocument()
                document.setPlainText(receipt_text)
                
                # Set monospace font for proper alignment
                font = QFont("Courier New", 5)  # Larger font for better readability
                font.setWeight(QFont.Bold)  # Make text bolder
                font.setStyleHint(QFont.TypeWriter)  # Better for thermal printers
                document.setDefaultFont(font)

                printer.setResolution(300)

                # Set document page size to match printer
                document.setPageSize(QSizeF(80 * 2.83465, 150 * 2.83465))  # Convert mm to points
                document.setDocumentMargin(1.0)
                
                document.print_(printer)
                
                # Send cut command for thermal printers
                if "thermal" in self.printer_combo.currentText().lower() or "pos" in self.printer_combo.currentText().lower():
                    self.send_cut_command(self.printer_combo.currentText())
                
                # Save PDF
                self.save_as_pdf(auto_save=True)
                
                QMessageBox.information(self, "Success", "Receipt printed successfully!")
                
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Print failed: {str(e)}")



    def send_cut_command(self, printer_name):
        """Send cut command to thermal printer"""
        try:
            import win32print
            
            # ESC/POS cut command
            cut_command = b'\x1D\x56\x00'  # Full cut command
            
            # Open printer and send command
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                hJob = win32print.StartDocPrinter(hPrinter, 1, ("Cut Command", None, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, cut_command)
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
        except Exception as e:
            print(f"Could not send cut command: {e}")
    
    def save_as_pdf(self, auto_save=False):
        """Save receipt as PDF"""
        if not self.items:
            QMessageBox.information(self, "Info", "No items to save.")
            return
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"Receipt_{timestamp}_{self.receipt_serial}.pdf"
        
        if auto_save:
            # Use the specified folder for auto-save
            file_path = os.path.join(self.pdf_path_input.text(), filename)
        else:
            # Let user choose location
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Receipt as PDF", 
                os.path.join(self.pdf_path_input.text(), filename),
                "PDF Files (*.pdf)"
            )
        
        if file_path:
            try:
                # Create printer for PDF
                printer = QPrinter(QPrinter.HighResolution)
                printer.setOutputFormat(QPrinter.PdfFormat)
                printer.setOutputFileName(file_path)
                
                # Set custom paper size (80mm x 210mm)
                width_points = 80 * 2.83465
                height_points = 210 * 2.83465
                custome_size = QSizeF(width_points, height_points)
                printer.setPaperSize(custome_size, QPrinter.Point)
                printer.setPageMargins(10, 10, 10, 10, QPrinter.Point)
                
                # Create document and save
                document = QTextDocument()
                document.setHtml(self.get_receipt_html())
                document.setPageSize(custome_size)
                document.print_(printer)
                
                if not auto_save:
                    QMessageBox.information(self, "Success", f"PDF saved successfully!\n{file_path}")
                    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save PDF: {str(e)}")
        
    def clear_all_items(self):
        if self.items:
            reply = QMessageBox.question(self, "Confirm Clear", 
                                       "Are you sure you want to clear all items?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.items.clear()
                self.update_items_list()
                self.update_receipt_preview()

def main():
    app = QApplication(sys.argv)
    
    # Check if path_utilis is available
    try:
        import path_utilis
    except ImportError:
        QMessageBox.critical(None, "Error", "path_utilis.py not found!\nPlease make sure path_utilis.py is in the same directory.")
        sys.exit(1)
    
    # For testing purposes - you can pass a shop folder name
    window = ReceiptFormApp(shop_folder=None)  # Change to actual shop folder when calling from main_window
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()