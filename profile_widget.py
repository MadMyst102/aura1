from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QLineEdit, QMessageBox, QInputDialog, QFrame,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QIcon, QColor, QFont, QPainter, QPixmap
from loguru import logger

from profiles import get_profile_manager
from theme import AuraTheme, AuraAnimation
from icons import AuraIconProvider

class ProfileWidget(QWidget):
    """Widget for managing configuration profiles"""
    
    # Signal emitted when a profile is loaded
    profile_loaded = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.profile_manager = get_profile_manager()
        self.setup_ui()
        self.refresh_profiles()
    
    def setup_ui(self):
        """Initialize the user interface with modern styling"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header with title and instructions
        header_layout = QVBoxLayout()
        
        title_label = QLabel("Profile Management")
        title_label.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {AuraTheme.SECONDARY};")
        header_layout.addWidget(title_label)
        
        header_label = QLabel(
            "Create and manage configuration profiles for different games or applications. "
            "Each profile stores a complete set of hotkey configurations."
        )
        header_label.setWordWrap(True)
        header_label.setStyleSheet(f"font-size: 10pt; color: {AuraTheme.TEXT_SECONDARY}; margin-bottom: 10px;")
        header_layout.addWidget(header_label)
        
        layout.addLayout(header_layout)
        
        # Profile selection area with enhanced styling
        selection_frame = QFrame()
        selection_frame.setFrameShape(QFrame.StyledPanel)
        selection_layout = QVBoxLayout(selection_frame)
        
        # Add icon and title to the frame
        selection_header = QHBoxLayout()
        icon_label = QLabel()
        icon_pixmap = AuraIconProvider.get_icon("profile", AuraTheme.SECONDARY, 24).pixmap(24, 24)
        icon_label.setPixmap(icon_pixmap)
        selection_header.addWidget(icon_label)
        
        selection_title = QLabel("Current Profile")
        selection_title.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {AuraTheme.SECONDARY};")
        selection_header.addWidget(selection_title)
        selection_header.addStretch()
        
        selection_layout.addLayout(selection_header)
        
        # Current profile display with enhanced styling
        current_layout = QHBoxLayout()
        
        self.current_profile_label = QLabel("default")
        self.current_profile_label.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {AuraTheme.PRIMARY}; padding: 10px;")
        current_layout.addWidget(self.current_profile_label)
        current_layout.addStretch()
        
        selection_layout.addLayout(current_layout)
        
        # Profile selector with enhanced styling
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select Profile:"))
        
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(250)
        self.profile_combo.setMinimumHeight(30)
        selector_layout.addWidget(self.profile_combo)
        
        self.load_button = QPushButton("Load")
        self.load_button.setIcon(AuraIconProvider.get_icon("open"))
        self.load_button.setIconSize(QSize(16, 16))
        self.load_button.clicked.connect(self.load_selected_profile)
        selector_layout.addWidget(self.load_button)
        
        selector_layout.addStretch()
        selection_layout.addLayout(selector_layout)
        
        # Apply shadow effect to the frame
        AuraTheme.apply_drop_shadow(selection_frame)
        layout.addWidget(selection_frame)
        
        # Profile management area with enhanced styling
        management_frame = QFrame()
        management_frame.setFrameShape(QFrame.StyledPanel)
        management_layout = QVBoxLayout(management_frame)
        
        # Add icon and title to the frame
        management_header = QHBoxLayout()
        mgmt_icon_label = QLabel()
        mgmt_icon_pixmap = AuraIconProvider.get_icon("settings", AuraTheme.SECONDARY, 24).pixmap(24, 24)
        mgmt_icon_label.setPixmap(mgmt_icon_pixmap)
        management_header.addWidget(mgmt_icon_label)
        
        management_title = QLabel("Profile Management")
        management_title.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {AuraTheme.SECONDARY};")
        management_header.addWidget(management_title)
        management_header.addStretch()
        
        management_layout.addLayout(management_header)
        
        # New profile with enhanced styling
        new_layout = QHBoxLayout()
        new_layout.addWidget(QLabel("New Profile Name:"))
        
        self.new_profile_input = QLineEdit()
        self.new_profile_input.setPlaceholderText("Enter profile name...")
        self.new_profile_input.setMinimumHeight(30)
        new_layout.addWidget(self.new_profile_input)
        
        self.save_button = QPushButton("Save As Profile")
        self.save_button.setIcon(AuraIconProvider.get_icon("save"))
        self.save_button.setIconSize(QSize(16, 16))
        self.save_button.clicked.connect(self.save_new_profile)
        new_layout.addWidget(self.save_button)
        
        management_layout.addLayout(new_layout)
        
        # Profile actions with enhanced styling
        actions_layout = QHBoxLayout()
        
        self.rename_button = QPushButton("Rename")
        self.rename_button.setIcon(AuraIconProvider.get_icon("settings"))
        self.rename_button.setIconSize(QSize(16, 16))
        self.rename_button.clicked.connect(self.rename_profile)
        actions_layout.addWidget(self.rename_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("deleteButton")  # For special styling
        self.delete_button.setIcon(AuraIconProvider.get_icon("delete", AuraTheme.ERROR))
        self.delete_button.setIconSize(QSize(16, 16))
        self.delete_button.clicked.connect(self.delete_profile)
        actions_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setIcon(AuraIconProvider.get_icon("refresh"))
        self.refresh_button.setIconSize(QSize(16, 16))
        self.refresh_button.clicked.connect(self.refresh_profiles)
        actions_layout.addWidget(self.refresh_button)
        
        management_layout.addLayout(actions_layout)
        
        # Apply shadow effect to the frame
        AuraTheme.apply_drop_shadow(management_frame)
        layout.addWidget(management_frame)
        layout.addStretch()
    
    def refresh_profiles(self):
        """Refresh the list of available profiles"""
        try:
            # Get current profile
            current_profile = self.profile_manager.get_current_profile()
            self.current_profile_label.setText(current_profile)
            
            # Get all profiles
            profiles = self.profile_manager.get_profiles()
            
            # Update combo box
            self.profile_combo.clear()
            self.profile_combo.addItems(profiles)
            
            # Set current profile as selected
            index = self.profile_combo.findText(current_profile)
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)
                
            logger.debug(f"Refreshed profiles list, found {len(profiles)} profiles")
            
        except Exception as e:
            logger.error(f"Error refreshing profiles: {e}")
    
    def load_selected_profile(self):
        """Load the selected profile with animation"""
        try:
            profile_name = self.profile_combo.currentText()
            if not profile_name:
                return
                
            # Load the profile
            config = self.profile_manager.load_profile(profile_name)
            if config:
                # Create fade animation for profile label
                fade_out = AuraAnimation.fade_out(self.current_profile_label, duration=150, start_value=1.0, end_value=0.3)
                fade_out.start()
                
                # Update current profile display after animation
                def update_label():
                    self.current_profile_label.setText(profile_name)
                    fade_in = AuraAnimation.fade_in(self.current_profile_label, duration=300, start_value=0.3, end_value=1.0)
                    fade_in.start()
                    
                    # Emit signal with loaded config
                    self.profile_loaded.emit(config)
                
                # Connect animation finished signal to update function
                fade_out.finished.connect(update_label)
                
                # Show success message with custom styling
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Profile Loaded")
                msg.setText(f"<h3 style='color: {AuraTheme.SUCCESS};'>Success!</h3>")
                msg.setInformativeText(f"Profile <b>{profile_name}</b> loaded successfully.")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setStyleSheet(f"""
                    QMessageBox {{  
                        background-color: {AuraTheme.CARD_BACKGROUND};
                        color: {AuraTheme.TEXT_PRIMARY};
                    }}
                    QPushButton {{  
                        background-color: {AuraTheme.PRIMARY};
                        color: {AuraTheme.TEXT_PRIMARY};
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-weight: bold;
                        min-width: 80px;
                    }}
                    QPushButton:hover {{  
                        background-color: {QColor(AuraTheme.PRIMARY).lighter(120).name()};
                    }}
                """)
                msg.exec_()
            else:
                # Show warning message with custom styling
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Load Failed")
                msg.setText(f"<h3 style='color: {AuraTheme.WARNING};'>Warning!</h3>")
                msg.setInformativeText(f"Failed to load profile <b>{profile_name}</b>.")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setStyleSheet(f"""
                    QMessageBox {{  
                        background-color: {AuraTheme.CARD_BACKGROUND};
                        color: {AuraTheme.TEXT_PRIMARY};
                    }}
                    QPushButton {{  
                        background-color: {AuraTheme.PRIMARY};
                        color: {AuraTheme.TEXT_PRIMARY};
                        border: none;
                        border-radius: 4px;
                        padding: 6px 12px;
                        font-weight: bold;
                        min-width: 80px;
                    }}
                    QPushButton:hover {{  
                        background-color: {QColor(AuraTheme.PRIMARY).lighter(120).name()};
                    }}
                """)
                msg.exec_()
                
        except Exception as e:
            logger.error(f"Error loading profile: {e}")
            
            # Show error message with custom styling
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"<h3 style='color: {AuraTheme.ERROR};'>Error!</h3>")
            msg.setInformativeText(f"Error loading profile: {str(e)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet(f"""
                QMessageBox {{  
                    background-color: {AuraTheme.CARD_BACKGROUND};
                    color: {AuraTheme.TEXT_PRIMARY};
                }}
                QPushButton {{  
                    background-color: {AuraTheme.PRIMARY};
                    color: {AuraTheme.TEXT_PRIMARY};
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                    min-width: 80px;
                }}
                QPushButton:hover {{  
                    background-color: {QColor(AuraTheme.PRIMARY).lighter(120).name()};
                }}
            """)
            msg.exec_()
    
    def save_new_profile(self):
        """Save current configuration as a new profile"""
        try:
            profile_name = self.new_profile_input.text().strip()
            if not profile_name:
                QMessageBox.warning(
                    self,
                    "Invalid Name",
                    "Please enter a valid profile name."
                )
                return
                
            # Check if profile already exists
            profiles = self.profile_manager.get_profiles()
            if profile_name in profiles:
                confirm = QMessageBox.question(
                    self,
                    "Confirm Overwrite",
                    f"Profile '{profile_name}' already exists. Overwrite?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if confirm != QMessageBox.Yes:
                    return
            
            # Get current config from main window
            # This will be provided by the main window when connecting to save_profile signal
            # For now, we'll emit a signal that the main window will handle
            self.request_save_profile(profile_name)
                
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error saving profile: {str(e)}"
            )
    
    def request_save_profile(self, profile_name):
        """Request the main window to save the current config as a profile"""
        # This method will be overridden by the main window
        pass
    
    def save_profile_with_config(self, profile_name, config):
        """Save a profile with the provided configuration"""
        try:
            success = self.profile_manager.save_profile(profile_name, config)
            
            if success:
                # Clear input field
                self.new_profile_input.clear()
                
                # Refresh profiles list
                self.refresh_profiles()
                
                # Update current profile display
                self.current_profile_label.setText(profile_name)
                
                QMessageBox.information(
                    self,
                    "Profile Saved",
                    f"Profile '{profile_name}' saved successfully."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Save Failed",
                    f"Failed to save profile '{profile_name}'."
                )
                
        except Exception as e:
            logger.error(f"Error saving profile with config: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error saving profile: {str(e)}"
            )
    
    def rename_profile(self):
        """Rename the selected profile"""
        try:
            profile_name = self.profile_combo.currentText()
            if not profile_name:
                return
                
            if profile_name == "default":
                QMessageBox.warning(
                    self,
                    "Cannot Rename",
                    "The default profile cannot be renamed."
                )
                return
                
            # Get new name
            new_name, ok = QInputDialog.getText(
                self,
                "Rename Profile",
                f"Enter new name for profile '{profile_name}':",
                QLineEdit.Normal
            )
            
            if not ok or not new_name.strip():
                return
                
            new_name = new_name.strip()
            
            # Check if new name already exists
            profiles = self.profile_manager.get_profiles()
            if new_name in profiles:
                QMessageBox.warning(
                    self,
                    "Name Exists",
                    f"Profile name '{new_name}' already exists."
                )
                return
                
            # Rename profile
            success = self.profile_manager.rename_profile(profile_name, new_name)
            
            if success:
                # Refresh profiles list
                self.refresh_profiles()
                
                QMessageBox.information(
                    self,
                    "Profile Renamed",
                    f"Profile renamed from '{profile_name}' to '{new_name}'."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Rename Failed",
                    f"Failed to rename profile '{profile_name}'."
                )
                
        except Exception as e:
            logger.error(f"Error renaming profile: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error renaming profile: {str(e)}"
            )
    
    def delete_profile(self):
        """Delete the selected profile"""
        try:
            profile_name = self.profile_combo.currentText()
            if not profile_name:
                return
                
            if profile_name == "default":
                QMessageBox.warning(
                    self,
                    "Cannot Delete",
                    "The default profile cannot be deleted."
                )
                return
                
            # Confirm deletion
            confirm = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete profile '{profile_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm != QMessageBox.Yes:
                return
                
            # Delete profile
            success = self.profile_manager.delete_profile(profile_name)
            
            if success:
                # Refresh profiles list
                self.refresh_profiles()
                
                QMessageBox.information(
                    self,
                    "Profile Deleted",
                    f"Profile '{profile_name}' deleted successfully."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Delete Failed",
                    f"Failed to delete profile '{profile_name}'."
                )
                
        except Exception as e:
            logger.error(f"Error deleting profile: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error deleting profile: {str(e)}"
            )