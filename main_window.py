from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
import os
import json
import shutil
import sys
import create_shop_window
from path_utilis import get_base_path
from receipt_form import ReceiptFormApp

DATA_DIR = os.path.join(get_base_path(), 'data')

class ClickableWidget(QWidget):
    clicked = pyqtSignal()

    def __init__(self, shop_folder=None):
        super().__init__()
        self.is_selected = False
        self.is_hovering = False
        self.shop_folder = shop_folder
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        widget_width = self.width()
        click_x = event.pos().x()
        if click_x < widget_width - 120:
            self.clicked.emit()

    def enterEvent(self, event):
        self.is_hovering = True
        self.update_style()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovering = False
        self.update_style()
        super().leaveEvent(event)

    def set_selected(self, selected):
        self.is_selected = selected
        self.update_style()

    def update_style(self):
        if self.is_selected:
            self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e6f2ff, stop:1 #d9ecff
                    );
                    border: 1px solid #99ccff;
                    border-radius: 6px;
                }
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: transparent;
                }
            """)
        elif self.is_hovering:
            self.setStyleSheet("""
                QWidget {
                    background: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f0f8ff, stop:1 #e0f0ff
                    );
                    border: 1px solid #b3d9ff;
                    border-radius: 6px;
                }
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: transparent;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border: none;
                    border-radius: 6px;
                }
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: transparent;
                }
            """)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System - Shop Selection")
        self.setMinimumSize(450, 450)
        self.showMaximized()
        self.selected_widget = None  # Track currently selected widget

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout()
        central_widget.setLayout(self.main_layout)

        # Add New Shop Button
        add_shop_btn = QPushButton("+ Create New Shop")
        add_shop_btn.setFixedSize(200, 100)
        add_shop_btn.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                border: 2px dashed #888;
                background-color: #f0f0f0;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #e0e0ff;
                border: 2px dashed #666;
            }
        """)
        add_shop_btn.clicked.connect(self.create_new_shop)
        self.main_layout.addWidget(add_shop_btn, alignment=Qt.AlignCenter)

        # Recent Shops Label
        recent_label = QLabel("Recent Shops")
        recent_label.setStyleSheet("font-size: 18px; margin-top: 20px; font-weight: bold;")
        self.main_layout.addWidget(recent_label)

        # Shop List
        self.shop_list_widget = QListWidget()
        self.shop_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QListWidget::item {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: transparent;
                border: none;
            }
            QListWidget::item:hover {
                background-color: transparent;
            }
        """)
        
        self.main_layout.addWidget(self.shop_list_widget)
        self.load_recent_shops()

    def clear_selection(self):
        """Clear the current selection"""
        if self.selected_widget:
            self.selected_widget.set_selected(False)
            self.selected_widget = None

    def set_selection(self, widget):
        """Set a new selection"""
        self.clear_selection()
        self.selected_widget = widget
        widget.set_selected(True)

    def load_recent_shops(self):
        self.shop_list_widget.clear()
        self.selected_widget = None  # Clear selection when reloading
        data_dir = DATA_DIR  # Use absolute path instead of relative "data"
        os.makedirs(data_dir, exist_ok=True)

        for shop_folder in os.listdir(data_dir):
            shop_path = os.path.join(data_dir, shop_folder)
            info_path = os.path.join(shop_path, "shop_info.json")

            if os.path.isdir(shop_path) and os.path.isfile(info_path):
                with open(info_path, "r") as f:
                    try:
                        data = json.load(f)
                        shop_name = data.get("shop_name", "N/A")
                        owner = data.get("owner_name", "N/A")
                        address = data.get("address", "N/A")
                        mobiles = " | ".join(data.get("mobile_numbers", []))

                        # Create main horizontal layout for the item
                        item_widget = ClickableWidget(shop_folder)  # Pass shop_folder to constructor
                        main_layout = QHBoxLayout()
                        main_layout.setContentsMargins(15, 15, 15, 15)
                        
                        # Left side - shop information
                        info_layout = QVBoxLayout()
                        info_layout.setSpacing(5)
                        
                        # Create labels with better styling
                        name_label = QLabel(f"<b>Shop Name:</b> {shop_name}")
                        owner_label = QLabel(f"<b>Owner:</b> {owner}")
                        address_label = QLabel(f"<b>Address:</b> {address}")
                        mobile_label = QLabel(f"<b>Mobile:</b> {mobiles}")
                        
                        info_layout.addWidget(name_label)
                        info_layout.addWidget(owner_label)
                        info_layout.addWidget(address_label)
                        info_layout.addWidget(mobile_label)
                        
                        info_widget = QWidget()
                        info_widget.setLayout(info_layout)
                        
                        # Right side - action buttons
                        buttons_layout = QVBoxLayout()
                        buttons_layout.setSpacing(8)
                        
                        # Edit button
                        edit_btn = QPushButton("✏️ Edit")
                        edit_btn.setFixedSize(100, 35)
                        edit_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #4CAF50;
                                color: white;
                                border: none;
                                border-radius: 6px;
                                font-size: 12px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #45a049;
                            }
                            QPushButton:pressed {
                                background-color: #3d8b40;
                            }
                        """)
                        edit_btn.clicked.connect(lambda checked, shop=shop_folder: self.edit_shop(shop))
                        
                        # Delete button
                        delete_btn = QPushButton("🗑️ Delete")
                        delete_btn.setFixedSize(100, 35)
                        delete_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #f44336;
                                color: white;
                                border: none;
                                border-radius: 6px;
                                font-size: 12px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #da190b;
                            }
                            QPushButton:pressed {
                                background-color: #c41411;
                            }
                        """)
                        delete_btn.clicked.connect(lambda checked, shop=shop_folder: self.delete_shop(shop))
                        
                        buttons_layout.addWidget(edit_btn)
                        buttons_layout.addWidget(delete_btn)
                        buttons_layout.addStretch()  # Push buttons to top
                        
                        buttons_widget = QWidget()
                        buttons_widget.setLayout(buttons_layout)
                        buttons_widget.setFixedWidth(120)
                        
                        # Add both widgets to main layout
                        main_layout.addWidget(info_widget)
                        main_layout.addWidget(buttons_widget)
                        
                        item_widget.setLayout(main_layout)
                        item_widget.update_style()  # Apply initial styling

                        list_item = QListWidgetItem()
                        list_item.setSizeHint(item_widget.sizeHint())

                        # Connect click signal for entering shop and selection
                        # Use a more reliable way to capture the widget reference
                        def make_click_handler(widget_ref, shop_ref):
                            return lambda: self.select_and_enter_shop(widget_ref, shop_ref)
                        
                        item_widget.clicked.connect(make_click_handler(item_widget, shop_folder))

                        self.shop_list_widget.addItem(list_item)
                        self.shop_list_widget.setItemWidget(list_item, item_widget)

                    except Exception as e:
                        print("Failed to load shop:", shop_folder, e)

    def select_and_enter_shop(self, widget, shop_folder):
        """Handle selection and entering shop"""
        # Debug print to verify correct widget is being selected
        print(f"Selecting shop: {shop_folder}, Widget shop: {widget.shop_folder}")
        self.set_selection(widget)
        self.enter_shop_by_name(shop_folder)

    def create_new_shop(self):
        self.new_shop_window = create_shop_window.CreateShop()
        self.new_shop_window.shop_created.connect(self.load_recent_shops)  # Refresh list when new shop is created
        self.new_shop_window.show()

    def edit_shop(self, shop_folder):
        """Open the shop for editing"""
        try:
            # You can either open the create_new_shop window in edit mode
            # or create a separate edit window
            self.edit_shop_window = create_shop_window.CreateShop(edit_mode=True, shop_folder=shop_folder)
            self.edit_shop_window.shop_created.connect(self.load_recent_shops)  # Refresh list after edit
            self.edit_shop_window.show()
        except Exception as e:
            QMessageBox.warning(self, "Edit Error", f"Could not open shop for editing: {str(e)}")

    def delete_shop(self, shop_folder):
        """Delete the selected shop after confirmation"""
        # Get shop name for confirmation dialog
        shop_path = os.path.join(DATA_DIR, shop_folder)  # Use absolute path
        info_path = os.path.join(shop_path, "shop_info.json")
        
        shop_name = shop_folder  # Default to folder name
        try:
            if os.path.isfile(info_path):
                with open(info_path, "r") as f:
                    data = json.load(f)
                    shop_name = data.get("shop_name", shop_folder)
        except:
            pass
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self, 
            "Delete Shop", 
            f"Are you sure you want to delete the shop '{shop_name}'?\n\nThis action cannot be undone and will delete all shop data.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete the entire shop folder
                if os.path.exists(shop_path):
                    shutil.rmtree(shop_path)
                    QMessageBox.information(self, "Success", f"Shop '{shop_name}' has been deleted successfully.")
                    self.load_recent_shops()  # Refresh the list
                else:
                    QMessageBox.warning(self, "Error", "Shop folder not found.")
            except Exception as e:
                QMessageBox.critical(self, "Delete Error", f"Failed to delete shop: {str(e)}")

    def enter_shop_by_name(self, shop_folder):
        try:
            self.receipt_form = ReceiptFormApp(shop_folder)
            self.receipt_form.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open receipt form: {str(e)}")

def main():
    app = QApplication(sys.argv)
    entrance_form = MainWindow()
    entrance_form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()