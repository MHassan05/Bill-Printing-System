from PyQt5.QtWidgets import QPushButton, QListWidget

def create_shop_button(callback):
    button = QPushButton("+ Create New Shop")
    button.setFixedSize(200, 100)
    button.setStyleSheet("""
        QPushButton {
            font-size: 16px;
            background-color: #f0f0f0;
            border: 2px dashed #888;
            border-radius: 8px;
        }
        QPushButton:hover {
            background-color: #e0e0ff;
            border: 2px dashed #666;
        }
    """)
    button.clicked.connect(callback)
    return button

def shop_list_widget():
     list_widget = QListWidget()
     list_widget.setStyleSheet("""
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
     
     return list_widget