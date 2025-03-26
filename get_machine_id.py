import sys
import uuid
import hashlib
import platform
import wmi
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QPushButton, QLabel, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

def get_system_info():
    """Get unique system information"""
    c = wmi.WMI()
    
    # Get CPU info
    processor_id = ""
    for processor in c.Win32_Processor():
        processor_id = processor.ProcessorId.strip()
        break
    
    # Get motherboard info
    board_id = ""
    for board in c.Win32_BaseBoard():
        board_id = board.SerialNumber.strip()
        break
        
    # Get BIOS info
    bios_id = ""
    for bios in c.Win32_BIOS():
        bios_id = bios.SerialNumber.strip()
        break
    
    # Get disk info
    disk_id = ""
    for disk in c.Win32_DiskDrive():
        if disk.SerialNumber:
            disk_id = disk.SerialNumber.strip()
            break
            
    system_info = {
        'processor': processor_id,
        'motherboard': board_id,
        'bios': bios_id,
        'disk': disk_id,
        'node': str(uuid.getnode()),  # MAC address
        'platform': platform.platform()
    }
    
    return system_info

def generate_machine_id(system_info):
    """Generate a unique machine ID from system information"""
    # Create a string of all hardware info
    hardware_str = json.dumps(system_info, sort_keys=True)
    
    # Generate SHA-256 hash
    return hashlib.sha256(hardware_str.encode()).hexdigest()

class MachineIDWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.generate_id()
        
    def setup_ui(self):
        self.setWindowTitle("AURA pro+ farm Machine ID")
        self.setMinimumWidth(600)
        self.setMinimumHeight(300)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("System Machine ID")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "This is your unique Machine ID. Send this to your vendor\n"
            "to get a license key for this specific computer."
        )
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)
        
        # ID display
        self.id_display = QTextEdit()
        self.id_display.setReadOnly(True)
        self.id_display.setMinimumHeight(100)
        layout.addWidget(self.id_display)
        
        # Copy button
        copy_btn = QPushButton("Copy Machine ID")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        copy_btn.setMinimumHeight(40)
        layout.addWidget(copy_btn)
        
        # Save button
        save_btn = QPushButton("Save to File")
        save_btn.clicked.connect(self.save_to_file)
        layout.addWidget(save_btn)
        
        # System info (collapsed by default)
        self.system_info = None
        info_btn = QPushButton("Show System Information")
        info_btn.clicked.connect(self.show_system_info)
        layout.addWidget(info_btn)
    
    def generate_id(self):
        """Generate and display the machine ID"""
        try:
            self.system_info = get_system_info()
            machine_id = generate_machine_id(self.system_info)
            self.id_display.setText(machine_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generating Machine ID: {e}")
    
    def copy_to_clipboard(self):
        """Copy the machine ID to clipboard"""
        cb = QApplication.clipboard()
        cb.setText(self.id_display.toPlainText())
        QMessageBox.information(self, "Success", "Machine ID copied to clipboard!")
    
    def save_to_file(self):
        """Save the machine ID to a file"""
        try:
            with open("machine_id.txt", "w") as f:
                f.write(f"AURA pro+ farm Machine ID\n")
                f.write(f"Generated: {platform.node()}\n")
                f.write(f"=" * 50 + "\n")
                f.write(self.id_display.toPlainText())
            QMessageBox.information(self, "Success", "Machine ID saved to machine_id.txt")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving file: {e}")
    
    def show_system_info(self):
        """Show the system information used to generate the ID"""
        if self.system_info:
            info = "System Information Used for Machine ID:\n\n"
            for key, value in self.system_info.items():
                if value:  # Only show non-empty values
                    info += f"{key.title()}: {value}\n"
            QMessageBox.information(self, "System Information", info)

def main():
    app = QApplication(sys.argv)
    window = MachineIDWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
