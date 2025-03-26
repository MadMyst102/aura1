import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer
from loguru import logger
from license_manager import LicenseDialog

class LicenseStatusWidget(QFrame):
    """Widget displaying current license status"""
    def __init__(self, license_manager):
        super().__init__()
        self.license_manager = license_manager
        self.setup_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(60000)  # Update every minute
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Status section
        status_layout = QHBoxLayout()
        
        # Status indicator
        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        # Activate button
        self.activate_btn = QPushButton("Change License")
        self.activate_btn.clicked.connect(self.show_activation_dialog)
        status_layout.addWidget(self.activate_btn)
        
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        # Details section
        details_frame = QFrame()
        details_frame.setFrameStyle(QFrame.StyledPanel)
        details_layout = QVBoxLayout(details_frame)
        
        # Machine ID
        machine_id_label = QLabel(f"Machine ID: {self.license_manager.machine_id[:16]}...")
        machine_id_label.setStyleSheet("color: #666;")
        details_layout.addWidget(machine_id_label)
        
        # Expiration progress
        self.days_left_label = QLabel()
        details_layout.addWidget(self.days_left_label)
        
        self.expiration_progress = QProgressBar()
        self.expiration_progress.setTextVisible(True)
        details_layout.addWidget(self.expiration_progress)
        
        layout.addWidget(details_frame)
        layout.addStretch()
        
        # Initial update
        self.update_status()
        
    def update_status(self):
        """Update the license status display"""
        try:
            if not self.license_manager.check_license():
                self.status_label.setText("⚠️ License Required")
                self.status_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #f44336;")
                self.days_left_label.setText("No valid license found")
                self.expiration_progress.setValue(0)
                return
            
            # Get license info from file
            with open('license.acl', 'r') as f:
                license_key = f.read().strip()
                
            # Decrypt and parse license data
            decrypted = self.license_manager.fernet.decrypt(license_key.encode()).decode()
            data = json.loads(decrypted)
            
            expiration = datetime.fromisoformat(data['expiration'])
            days_left = (expiration - datetime.now()).days
            
            if days_left <= 0:
                self.status_label.setText("⚠️ License Expired")
                self.status_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #f44336;")
                self.days_left_label.setText("License has expired")
                self.expiration_progress.setValue(0)
            else:
                self.status_label.setText("✓ Licensed")
                self.status_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #4caf50;")
                
                # Show days remaining
                if days_left <= 7:
                    self.days_left_label.setText(f"⚠️ License expires in {days_left} days")
                    self.days_left_label.setStyleSheet("color: #ff9800;")
                else:
                    self.days_left_label.setText(f"Valid for {days_left} more days")
                    self.days_left_label.setStyleSheet("")
                
                # Update progress bar
                total_days = 30 if days_left <= 30 else days_left
                progress = int((days_left / total_days) * 100)
                self.expiration_progress.setValue(progress)
                
        except Exception as e:
            logger.error(f"Error updating license status: {e}")
            self.status_label.setText("⚠️ Error")
            self.status_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #f44336;")
            self.days_left_label.setText("Could not verify license status")
            self.expiration_progress.setValue(0)
    
    def show_activation_dialog(self):
        """Show the license activation dialog"""
        dialog = LicenseDialog(self.license_manager)
        if dialog.exec_():
            self.update_status()

class LicenseTab(QWidget):
    """Tab for managing software license"""
    def __init__(self, license_manager):
        super().__init__()
        self.license_manager = license_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the license tab interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header_label = QLabel("License Management")
        header_label.setStyleSheet("font-size: 24pt; font-weight: bold;")
        layout.addWidget(header_label)
        
        description = QLabel(
            "Manage your AURA pro+ farm software license. A valid license is required to use this software. "
            "Your license is tied to your machine's hardware ID for security."
        )
        description.setWordWrap(True)
        description.setStyleSheet("font-size: 11pt; color: #666;")
        layout.addWidget(description)
        
        # Add status widget
        self.status_widget = LicenseStatusWidget(self.license_manager)
        layout.addWidget(self.status_widget)
        
        layout.addStretch()
