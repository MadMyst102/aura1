import sys
import json
import uuid
import hashlib
import platform
import wmi
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from loguru import logger

import base64

# License System Configuration
LICENSE_SECRET = b'yXn8kp2lMqRtWvZaEoHgUjIcFbNdSxKp'  # 32-byte key for HMAC
# Generate base64-encoded Fernet key
ENCRYPTION_KEY = base64.urlsafe_b64encode(b'dR7mK9pL4nX2wS5vY8hB3gA6tU9jC1eQ'[:32])
LICENSE_FILE = 'license.acl'  # Aura Client License file

class LicenseManager:
    def __init__(self):
        self.fernet = Fernet(ENCRYPTION_KEY)
        self.machine_id = self.get_machine_id()
        self.is_licensed = False
        
    def get_machine_id(self):
        """Generate a unique machine identifier"""
        try:
            c = wmi.WMI()
            
            # Get system information
            system_info = {}
            
            # CPU info
            for processor in c.Win32_Processor():
                system_info['processor'] = processor.ProcessorId.strip()
                break
            
            # Motherboard info
            for board in c.Win32_BaseBoard():
                system_info['motherboard'] = board.SerialNumber.strip()
                break
                
            # BIOS info
            for bios in c.Win32_BIOS():
                system_info['bios'] = bios.SerialNumber.strip()
                break
            
            # Disk info
            for disk in c.Win32_DiskDrive():
                if disk.SerialNumber:
                    system_info['disk'] = disk.SerialNumber.strip()
                    break
            
            # Additional system info
            system_info['node'] = str(uuid.getnode())  # MAC address
            system_info['platform'] = platform.platform()
            
            # Create string of hardware info and hash it
            hardware_str = json.dumps(system_info, sort_keys=True)
            return hashlib.sha256(hardware_str.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Error getting machine ID: {e}")
            # Fallback to basic MAC address if WMI fails
            return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()
    
    def generate_license(self, expiration_days=30):
        """Create a license key valid for X days"""
        expiration = datetime.now() + timedelta(days=expiration_days)
        payload = {
            'machine_id': self.machine_id,
            'expiration': expiration.isoformat(),
            'signature': self._generate_signature(expiration)
        }
        return self.fernet.encrypt(json.dumps(payload).encode()).decode()
    
    def _generate_signature(self, expiration):
        """Create HMAC signature for license validation"""
        h = hashlib.sha256()
        h.update(self.machine_id.encode())
        h.update(expiration.isoformat().encode())
        h.update(LICENSE_SECRET)
        return h.hexdigest()
    
    def validate_license(self, license_key):
        """Validate a license key"""
        try:
            decrypted = self.fernet.decrypt(license_key.encode()).decode()
            data = json.loads(decrypted)
            
            # Verify signature
            expected_sig = self._generate_signature(datetime.fromisoformat(data['expiration']))
            if data['signature'] != expected_sig:
                logger.warning("License signature verification failed")
                return False
                
            # Check machine ID
            if data['machine_id'] != self.machine_id:
                logger.warning("License machine ID mismatch")
                return False
                
            # Check expiration
            expiration = datetime.fromisoformat(data['expiration'])
            if expiration < datetime.now():
                logger.warning("License has expired")
                return False
                
            self.is_licensed = True
            return True
            
        except Exception as e:
            logger.error(f"License validation error: {e}")
            return False
    
    def check_license(self):
        """Check for existing license"""
        try:
            with open(LICENSE_FILE, 'r') as f:
                encrypted_key = f.read().strip()
                return self.validate_license(encrypted_key)
        except FileNotFoundError:
            logger.info("No license file found")
            return False
        except Exception as e:
            logger.error(f"Error checking license: {e}")
            return False

class LicenseDialog(QDialog):
    def __init__(self, license_manager):
        super().__init__()
        self.license_manager = license_manager
        self.init_ui()
        
    def init_ui(self):
        """Initialize the license activation dialog"""
        self.setWindowTitle("AURA pro+ farm License Activation")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()
        
        # Add descriptive text
        desc_label = QLabel(
            "Welcome to AURA pro+ farm! Please enter your license key to activate the software.\n"
            "Contact the vendor to purchase a license key."
        )
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # License key input
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter your license key")
        layout.addWidget(self.key_input)
        
        # Activate button
        activate_btn = QPushButton("Activate License")
        activate_btn.clicked.connect(self.validate_and_save)
        layout.addWidget(activate_btn)
        
        self.setLayout(layout)
    
    def validate_and_save(self):
        """Validate and store license key"""
        license_key = self.key_input.text().strip()
        if not license_key:
            QMessageBox.warning(self, "Error", "Please enter a license key")
            return
            
        if self.license_manager.validate_license(license_key):
            try:
                with open(LICENSE_FILE, 'w') as f:
                    f.write(license_key)
                QMessageBox.information(self, "Success", "License activated successfully!")
                self.accept()
            except Exception as e:
                logger.error(f"Error saving license: {e}")
                QMessageBox.critical(self, "Error", "Could not save license file")
        else:
            QMessageBox.critical(self, "Error", "Invalid license key!")
    

def check_license_and_activate():
    """Check license and show activation dialog if needed"""
    license_manager = LicenseManager()
    if not license_manager.check_license():
        dialog = LicenseDialog(license_manager)
        if dialog.exec_() != QDialog.Accepted:
            logger.warning("License activation cancelled")
            sys.exit(1)
    return license_manager
