import sys
import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
import hashlib
import base64
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QTextEdit, QMessageBox,
    QFileDialog
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

# Use the same encryption configuration as the main application
LICENSE_SECRET = b'yXn8kp2lMqRtWvZaEoHgUjIcFbNdSxKp'
ENCRYPTION_KEY = base64.urlsafe_b64encode(b'dR7mK9pL4nX2wS5vY8hB3gA6tU9jC1eQ'[:32])

class KeyGenWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("AURA pro+ farm License Key Generator")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("AURA pro+ farm License Key Generator")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Machine ID input
        id_layout = QHBoxLayout()
        id_label = QLabel("Machine ID:")
        id_label.setMinimumWidth(100)
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Enter customer's machine ID")
        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)
        layout.addLayout(id_layout)
        
        # Duration input
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Duration (days):")
        duration_label.setMinimumWidth(100)
        self.duration_input = QSpinBox()
        self.duration_input.setRange(1, 3650)  # 1 day to 10 years
        self.duration_input.setValue(365)
        duration_layout.addWidget(duration_label)
        duration_layout.addWidget(self.duration_input)
        layout.addLayout(duration_layout)
        
        # Generate button
        generate_btn = QPushButton("Generate License Key")
        generate_btn.clicked.connect(self.generate_key)
        generate_btn.setMinimumHeight(40)
        layout.addWidget(generate_btn)
        
        # Result display
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setPlaceholderText("Generated license key will appear here")
        layout.addWidget(self.result_text)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        buttons_layout.addWidget(copy_btn)
        
        save_btn = QPushButton("Save to File")
        save_btn.clicked.connect(self.save_to_file)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
    def generate_key(self):
        machine_id = self.id_input.text().strip()
        if not machine_id:
            QMessageBox.warning(self, "Error", "Please enter a machine ID")
            return
            
        days = self.duration_input.value()
        
        try:
            # Create Fernet cipher
            fernet = Fernet(ENCRYPTION_KEY)
            
            # Set expiration date
            expiration = datetime.now() + timedelta(days=days)
            
            # Generate signature
            h = hashlib.sha256()
            h.update(machine_id.encode())
            h.update(expiration.isoformat().encode())
            h.update(LICENSE_SECRET)
            signature = h.hexdigest()
            
            # Create license payload
            payload = {
                'machine_id': machine_id,
                'expiration': expiration.isoformat(),
                'signature': signature
            }
            
            # Generate license key
            license_key = fernet.encrypt(json.dumps(payload).encode()).decode()
            
            # Display result
            result_text = f"""License Key Generated Successfully!
--------------------------------------------------
Machine ID: {machine_id}
Duration: {days} days
Expiration: {expiration.strftime('%Y-%m-%d')}
--------------------------------------------------
License Key:
{license_key}
"""
            self.result_text.setText(result_text)
            self.generated_key = license_key
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating license key: {e}")
    
    def copy_to_clipboard(self):
        if hasattr(self, 'generated_key'):
            cb = QApplication.clipboard()
            cb.setText(self.generated_key)
            QMessageBox.information(self, "Success", "License key copied to clipboard!")
        else:
            QMessageBox.warning(self, "Error", "Generate a license key first")
    
    def save_to_file(self):
        if not hasattr(self, 'generated_key'):
            QMessageBox.warning(self, "Error", "Generate a license key first")
            return
            
        machine_id = self.id_input.text().strip()
        days = self.duration_input.value()
        
        # Get save location
        filename = f"license_{machine_id[:8]}_{days}days.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save License Key",
            filename,
            "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(self.result_text.toPlainText())
                QMessageBox.information(self, "Success", f"License key saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error saving file: {e}")

def main():
    app = QApplication(sys.argv)
    window = KeyGenWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
