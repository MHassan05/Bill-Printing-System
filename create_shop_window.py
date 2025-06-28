from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox
)
from PyQt5.QtCore import pyqtSignal
import sys
import json
import os
import shutil
from path_utilis import get_base_path  

DATA_DIR = os.path.join(get_base_path(), 'data')

class CreateShop(QMainWindow):
    # Signal to notify when shop is created/updated
    shop_created = pyqtSignal()
    
    def __init__(self, edit_mode=False, shop_folder=None):
        super().__init__()
        self.edit_mode = edit_mode
        self.shop_folder = shop_folder
        self.original_shop_name = None
        
        # Set window title based on mode
        if edit_mode:
            self.setWindowTitle("Edit Shop")
        else:
            self.setWindowTitle("Create New Shop")
            
        # Set initial window size - will be adjusted dynamically
        self.setMinimumSize(550, 450)
        self.base_height = 450  # Base height for window

        self.mobile_inputs = []  # list to hold all mobile number fields

        self.initUI()
        
        # Load existing data if in edit mode
        if self.edit_mode and self.shop_folder:
            self.load_shop_data()

    def initUI(self):
        # Styling
        self.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                padding: 4px;
            }
            QLineEdit {
                font-size: 14px;
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-height: 20px;
            }
            QPushButton#ADDNewMobile {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: #4CAF50;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
                max-width: 40px;
                min-height: 30px;
            }
            QPushButton#ADDNewMobile:hover {
                background-color: #45a049;
            }
            QPushButton#RemoveMobile {
                font-size: 12px;
                color: white;
                background-color: #f44336;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                max-width: 70px;
                min-height: 25px;
            }
            QPushButton#RemoveMobile:hover {
                background-color: #da190b;
            }
            QPushButton#SaveButton {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color: #2196F3;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                margin-top: 10px;
                min-height: 35px;
            }
            QPushButton#SaveButton:hover {
                background-color: #1976D2;
            }
        """)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        # Shop Name
        self.layout.addWidget(QLabel("Shop Name:"))
        self.shop_name_input = QLineEdit()
        self.layout.addWidget(self.shop_name_input)

        # Shop Owner
        self.layout.addWidget(QLabel("Shop Owner:"))
        self.owner_name_input = QLineEdit()
        self.layout.addWidget(self.owner_name_input)

        # Shop Address
        self.layout.addWidget(QLabel("Shop Address:"))
        self.address_input = QLineEdit()
        self.layout.addWidget(self.address_input)

        # Mobile No. section
        self.layout.addWidget(QLabel("Mobile No.:"))
        self.mobile_layout = QVBoxLayout()
        self.add_mobile_input()  # add the first one

        self.add_new_mobile = QPushButton("+")
        self.add_new_mobile.setObjectName("ADDNewMobile")
        self.add_new_mobile.clicked.connect(self.on_click_add_new_mobile)

        self.layout.addLayout(self.mobile_layout)
        self.layout.addWidget(self.add_new_mobile)
        
        # Save button
        button_text = "Update Shop Info" if self.edit_mode else "Save Shop Info"
        self.save_button = QPushButton(button_text)
        self.save_button.setObjectName("SaveButton")
        self.save_button.clicked.connect(self.fetch_and_store_data)
        self.layout.addWidget(self.save_button)

    def adjust_window_size(self):
        """Dynamically adjust window size based on number of mobile inputs"""
        # Calculate additional height needed for extra mobile inputs
        extra_mobile_fields = len(self.mobile_inputs) - 1
        additional_height = extra_mobile_fields * 45  # 45 pixels per additional mobile field
        
        new_height = self.base_height + additional_height
        new_width = 550
        
        # Set the new size
        self.setFixedSize(new_width, new_height)

    def add_mobile_input(self, phone_number=""):
        # Create horizontal layout for mobile input and remove button
        mobile_row = QHBoxLayout()
        
        line_edit = QLineEdit()
        line_edit.setText(phone_number)
        self.mobile_inputs.append(line_edit)
        
        # Remove button (only show if more than 1 mobile input exists)
        remove_btn = QPushButton("Remove")
        remove_btn.setObjectName("RemoveMobile")
        remove_btn.clicked.connect(lambda: self.remove_mobile_input(mobile_row, line_edit))
        
        mobile_row.addWidget(line_edit)
        mobile_row.addWidget(remove_btn)
        
        # Hide remove button if it's the first (and only) mobile input
        if len(self.mobile_inputs) == 1:
            remove_btn.hide()
        else:
            # Show remove buttons for all inputs when there are multiple
            for i in range(self.mobile_layout.count()):
                layout_item = self.mobile_layout.itemAt(i)
                if layout_item and layout_item.layout():
                    btn = layout_item.layout().itemAt(1).widget()
                    if btn:
                        btn.show()
        
        self.mobile_layout.addLayout(mobile_row)
        
        # Adjust window size after adding mobile input
        self.adjust_window_size()

    def remove_mobile_input(self, mobile_row, line_edit):
        # Remove from mobile_inputs list
        if line_edit in self.mobile_inputs:
            self.mobile_inputs.remove(line_edit)
        
        # Remove the layout and its widgets
        while mobile_row.count():
            child = mobile_row.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Remove the layout from parent
        self.mobile_layout.removeItem(mobile_row)
        mobile_row.deleteLater()
        
        # Hide remove buttons if only one mobile input remains
        if len(self.mobile_inputs) == 1:
            for i in range(self.mobile_layout.count()):
                layout_item = self.mobile_layout.itemAt(i)
                if layout_item and layout_item.layout():
                    btn = layout_item.layout().itemAt(1).widget()
                    if btn:
                        btn.hide()
        
        # Adjust window size after removing mobile input
        self.adjust_window_size()

    def on_click_add_new_mobile(self):
        if len(self.mobile_inputs) >= 3:
            QMessageBox.warning(self, "Limit Reached", "You can add up to 3 mobile numbers only.")
            return
        self.add_mobile_input()

    def load_shop_data(self):
        """Load existing shop data for editing"""
        try:
            shop_path = os.path.join(DATA_DIR, self.shop_folder)  # Use absolute path
            info_path = os.path.join(shop_path, "shop_info.json")
            
            if os.path.isfile(info_path):
                with open(info_path, "r") as f:
                    data = json.load(f)
                    
                # Load basic info
                self.shop_name_input.setText(data.get("shop_name", ""))
                self.owner_name_input.setText(data.get("owner_name", ""))
                self.address_input.setText(data.get("address", ""))
                
                # Store original shop name for folder renaming logic
                self.original_shop_name = data.get("shop_name", "")
                
                # Load mobile numbers
                mobile_numbers = data.get("mobile_numbers", [])
                
                # Clear existing mobile inputs and add loaded ones
                self.mobile_inputs.clear()
                # Clear the mobile layout
                while self.mobile_layout.count():
                    child = self.mobile_layout.takeAt(0)
                    if child.layout():
                        while child.layout().count():
                            grandchild = child.layout().takeAt(0)
                            if grandchild.widget():
                                grandchild.widget().deleteLater()
                        child.layout().deleteLater()
                
                # Add mobile numbers
                if mobile_numbers:
                    for number in mobile_numbers:
                        self.add_mobile_input(number)
                else:
                    self.add_mobile_input()  # Add at least one empty input
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load shop data: {str(e)}")
    
    def fetch_and_store_data(self):   
        if not self.validate_data():
            return      

        shop_name = self.shop_name_input.text().strip()
        owner_name = self.owner_name_input.text().strip()
        address = self.address_input.text().strip()
        mobile_numbers = [field.text().strip() for field in self.mobile_inputs if field.text().strip()]

        # Create the main data directory if it doesn't exist
        data_dir = DATA_DIR  # Use absolute path instead of relative "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Handle directory logic
        if self.edit_mode:
            old_shop_dir = os.path.join(data_dir, self.shop_folder)
            new_shop_dir = os.path.join(data_dir, shop_name)
            
            # If shop name changed, rename the directory
            if self.original_shop_name != shop_name:
                if os.path.exists(new_shop_dir) and new_shop_dir != old_shop_dir:
                    QMessageBox.warning(self, "Shop Exists", "A shop with this name already exists.")
                    return
                
                try:
                    if old_shop_dir != new_shop_dir:
                        shutil.move(old_shop_dir, new_shop_dir)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to rename shop folder: {str(e)}")
                    return
            
            shop_dir = new_shop_dir
        else:
            # Creating new shop
            shop_dir = os.path.join(data_dir, shop_name)
            if os.path.exists(shop_dir):
                QMessageBox.warning(self, "Shop Exists", "A shop with this name already exists.")
                return
            os.makedirs(shop_dir)

        # Prepare data to store
        shop_data = {
            "shop_name": shop_name,
            "owner_name": owner_name,
            "address": address,
            "mobile_numbers": mobile_numbers
        }

        # Save JSON
        json_path = os.path.join(shop_dir, "shop_info.json")
        try:
            with open(json_path, "w") as f:
                json.dump(shop_data, f, indent=4)
            
            success_message = "Shop data updated successfully." if self.edit_mode else "Shop data saved successfully."
            QMessageBox.information(self, "Success", success_message)
            
            # Emit signal to refresh the main window
            self.shop_created.emit()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save shop data:\n{e}")
        
    def validate_data(self):
        shop_name = self.shop_name_input.text().strip()
        owner_name = self.owner_name_input.text().strip()
        address = self.address_input.text().strip()
        mobile_numbers = [field.text().strip() for field in self.mobile_inputs if field.text().strip()]

        # Check non-empty fields
        if not shop_name or not owner_name or not address:
            QMessageBox.warning(self, "Validation Error", "Shop Name, Owner Name, and Address must be filled.")
            return False
        
        # Check if at least one mobile number is provided
        if not mobile_numbers:
            QMessageBox.warning(self, "Validation Error", "At least one mobile number must be provided.")
            return False

        # Validate each mobile number
        for number in mobile_numbers:
            if not number.isdigit():
                QMessageBox.warning(self, "Validation Error", f"Phone number '{number}' contains non-numeric characters.")
                return False
            if len(number) != 11:
                QMessageBox.warning(self, "Validation Error", f"Phone number '{number}' should be 11 digits long.")
                return False

        # Validation passed
        return True

def main():
    app = QApplication(sys.argv)
    window = CreateShop()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()