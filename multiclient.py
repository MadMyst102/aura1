import sys
from typing import Dict, Any, List, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QHeaderView,
    QCheckBox, QGroupBox, QScrollArea, QFrame, QLineEdit, QRadioButton,
    QButtonGroup, QSpinBox, QDoubleSpinBox, QStyle, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QIcon, QColor, QFont, QPainter, QPixmap
import win32gui
import win32con
import win32process
import psutil
from loguru import logger

# Import theme and icons
from theme import AuraTheme, AuraAnimation
from icons import AuraIconProvider

class ClientTableWidget(QTableWidget):
    """Enhanced table widget for displaying client windows with modern styling"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Apply shadow effect
        AuraTheme.apply_drop_shadow(self)
        
    def setup_ui(self):
        # Set up table properties
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Select", "Client Window"])
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Set column widths
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.setColumnWidth(0, 60)  # Make checkbox column slightly wider
        
        # Enhanced header styling
        header_font = QFont(AuraTheme.FONT_FAMILY, AuraTheme.FONT_SIZE_NORMAL)
        header_font.setBold(True)
        self.horizontalHeader().setFont(header_font)
        self.horizontalHeader().setStyleSheet(f"""
            QHeaderView::section {{
                background-color: {AuraTheme.CARD_BACKGROUND};
                color: {AuraTheme.TEXT_PRIMARY};
                padding: 5px;
                border: none;
                border-bottom: 2px solid {AuraTheme.PRIMARY};
            }}
        """)
        
        # Add hover effect and alternating row colors
        self.setStyleSheet(f"""
            QTableWidget {{
                gridline-color: {AuraTheme.PRIMARY}30;
                alternate-background-color: {AuraTheme.CARD_BACKGROUND};
            }}
            QTableWidget::item:hover {{
                background-color: {AuraTheme.PRIMARY}20;
            }}
            QTableWidget::item:selected {{
                background-color: {AuraTheme.PRIMARY}40;
            }}
        """)
        
        # Add tooltips to headers
        self.horizontalHeaderItem(0).setToolTip("Select/deselect this client")
        self.horizontalHeaderItem(1).setToolTip("Game client window title")

class MultiClientWidget(QWidget):
    """Widget for managing multiple client windows"""
    
    # Signal emitted when client selection changes
    selection_changed = pyqtSignal(list)
    
    def __init__(self, hotkey_manager):
        super().__init__()
        self.hotkey_manager = hotkey_manager
        self.window_list = []
        self.selected_windows = []
        self.captured_windows = []
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface with modern styling and animations"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with title and instructions
        header_layout = QVBoxLayout()
        
        title_label = QLabel("Client Window Management")
        title_label.setStyleSheet(f"font-size: 18pt; font-weight: bold; color: {AuraTheme.SECONDARY};")
        header_layout.addWidget(title_label)
        
        header_label = QLabel(
            "Select game client windows to send hotkey actions to. "
            "You can select multiple clients to control them simultaneously."
        )
        header_label.setWordWrap(True)
        header_label.setStyleSheet(f"font-size: 10pt; color: {AuraTheme.TEXT_SECONDARY}; margin-bottom: 10px;")
        header_layout.addWidget(header_label)
        
        main_layout.addLayout(header_layout)
        
        # Control buttons frame with improved styling
        control_frame = QFrame()
        control_frame.setFrameShape(QFrame.StyledPanel)
        control_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AuraTheme.CARD_BACKGROUND};
                border-radius: 5px;
                padding: 5px;
            }}
        """)
        control_layout = QHBoxLayout(control_frame)
        control_layout.setSpacing(15)
        control_layout.setContentsMargins(15, 8, 15, 8)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(AuraIconProvider.get_icon("refresh"))
        refresh_button.setIconSize(QSize(16, 16))
        refresh_button.clicked.connect(self.refresh_window_list)
        control_layout.addWidget(refresh_button)
        
        pause_button = QPushButton("Pause")
        pause_button.setIcon(AuraIconProvider.get_icon("pause"))
        pause_button.setIconSize(QSize(16, 16))
        pause_button.clicked.connect(self.toggle_pause)
        self.pause_button = pause_button
        control_layout.addWidget(pause_button)
        
        select_all_button = QPushButton("Select All")
        select_all_button.setIcon(AuraIconProvider.get_icon("add"))
        select_all_button.setIconSize(QSize(16, 16))
        select_all_button.clicked.connect(self.select_all_clients)
        control_layout.addWidget(select_all_button)
        
        deselect_all_button = QPushButton("Deselect All")
        deselect_all_button.setIcon(AuraIconProvider.get_icon("delete"))
        deselect_all_button.setIconSize(QSize(16, 16))
        deselect_all_button.clicked.connect(self.deselect_all_clients)
        control_layout.addWidget(deselect_all_button)
        
        control_layout.addStretch()
        
        # Apply shadow effect to the control frame
        AuraTheme.apply_drop_shadow(control_frame)
        main_layout.addWidget(control_frame)
        
        # Create tables section with improved layout
        tables_section = QFrame()
        tables_section.setFrameShape(QFrame.NoFrame)
        tables_section.setContentsMargins(0, 0, 0, 0)
        tables_layout = QHBoxLayout(tables_section)
        tables_layout.setSpacing(30)  # Increased spacing between tables
        
        # Create left side (Running Clients)
        running_section = QFrame()
        running_section.setFrameShape(QFrame.NoFrame)
        running_layout = QVBoxLayout(running_section)
        running_layout.setSpacing(10)
        
        # Running Clients header with section number and improved styling
        running_header = QLabel("1. Running Clients")
        running_header.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {AuraTheme.PRIMARY};
            padding: 5px 0;
            border-bottom: 2px solid {AuraTheme.PRIMARY};
            margin-bottom: 5px;
        """)
        running_layout.addWidget(running_header)
        
        self.running_table = ClientTableWidget()
        self.running_table.setMinimumHeight(450)  # Taller table
        self.running_table.setMinimumWidth(450)   # Wider table
        running_layout.addWidget(self.running_table)
        
        # Capture button with improved styling
        capture_button = QPushButton("Capture Selected →")
        capture_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        capture_button.clicked.connect(self.capture_selected_clients)
        capture_button.setMinimumHeight(35)
        capture_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AuraTheme.PRIMARY};
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {QColor(AuraTheme.PRIMARY).darker(110).name()};
            }}
        """)
        running_layout.addWidget(capture_button)
        
        tables_layout.addWidget(running_section)
        
        # Create right side (Captured Clients)
        captured_section = QFrame()
        captured_section.setFrameShape(QFrame.NoFrame)
        captured_layout = QVBoxLayout(captured_section)
        captured_layout.setSpacing(10)
        
        # Captured Clients header with section number and improved styling
        captured_header = QLabel("2. Captured Clients")
        captured_header.setStyleSheet(f"""
            font-size: 14pt;
            font-weight: bold;
            color: {AuraTheme.SECONDARY};
            padding: 5px 0;
            border-bottom: 2px solid {AuraTheme.SECONDARY};
            margin-bottom: 5px;
        """)
        captured_layout.addWidget(captured_header)
        
        self.captured_table = ClientTableWidget()
        self.captured_table.setMinimumHeight(450)  # Taller table
        self.captured_table.setMinimumWidth(450)   # Wider table
        captured_layout.addWidget(self.captured_table)
        
        # Release button with improved styling
        release_button = QPushButton("← Release Selected")
        release_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        release_button.clicked.connect(self.release_selected_clients)
        release_button.setMinimumHeight(35)
        release_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AuraTheme.SECONDARY};
                color: white;
                border-radius: 5px;
                padding: 5px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {QColor(AuraTheme.SECONDARY).darker(110).name()};
            }}
        """)
        captured_layout.addWidget(release_button)
        
        tables_layout.addWidget(captured_section)
        
        main_layout.addWidget(tables_section)
        
        # Key delay section as a compact control
        delay_frame = QFrame()
        delay_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AuraTheme.CARD_BACKGROUND};
                border-radius: 3px;
                padding: 5px;
            }}
        """)
        delay_layout = QHBoxLayout(delay_frame)
        delay_layout.setContentsMargins(10, 5, 10, 5)
        delay_layout.setSpacing(5)
        
        delay_label = QLabel("Key Delay (s):")
        delay_label.setStyleSheet("color: #666;")
        delay_layout.addWidget(delay_label)
        
        self.delay_input = QDoubleSpinBox()
        self.delay_input.setDecimals(2)
        self.delay_input.setMinimum(0.01)
        self.delay_input.setMaximum(5.0)
        self.delay_input.setSingleStep(0.01)
        self.delay_input.setValue(0.05)
        self.delay_input.setMaximumWidth(60)
        self.delay_input.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {AuraTheme.CARD_BACKGROUND};
                color: {AuraTheme.TEXT_PRIMARY};
                border: 1px solid {AuraTheme.PRIMARY}40;
                padding: 2px 5px;
                border-radius: 2px;
            }}
            QDoubleSpinBox:focus {{
                border: 1px solid {AuraTheme.PRIMARY};
            }}
        """)
        delay_layout.addWidget(self.delay_input)
        
        set_delay_button = QPushButton("Set")
        set_delay_button.clicked.connect(self.set_key_delay)
        set_delay_button.setMaximumWidth(60)
        set_delay_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {AuraTheme.SUCCESS};
                color: white;
                border-radius: 2px;
                padding: 3px 8px;
            }}
            QPushButton:hover {{
                background-color: {QColor(AuraTheme.SUCCESS).darker(110).name()};
            }}
        """)
        delay_layout.addWidget(set_delay_button)
        
        delay_layout.addStretch()
        
        # Add delay control to top control frame
        control_layout.addWidget(delay_frame)
        
        # Make tables fill available space
        self.running_table.setMinimumHeight(500)   # Even taller now
        self.captured_table.setMinimumHeight(500)  # Even taller now

        # Add stretch to push everything up
        main_layout.addStretch()
        
        # Connect signals
        self.running_table.itemChanged.connect(self.on_item_changed)
        self.captured_table.itemChanged.connect(self.on_captured_item_changed)
        
        # Add tooltips to control buttons
        refresh_button.setToolTip("Refresh the list of available client windows")
        pause_button.setToolTip("Pause/Resume hotkey actions to all clients")
        select_all_button.setToolTip("Select all visible client windows")
        deselect_all_button.setToolTip("Deselect all client windows")
        
        # Add tooltip to delay control
        self.delay_input.setToolTip("Delay between hotkey actions (in seconds)")
        set_delay_button.setToolTip("Apply the new delay setting")
        
        # Initial refresh
        self.refresh_window_list()
        
    def add_log_message(self, message):
        """Just log to logger instead of displaying in UI"""
        logger.info(message)
    
    def refresh_window_list(self):
        """Refresh the list of available game client windows"""
        try:
            # Clear existing window list
            self.window_list = []
            
            # Clear running clients table
            self.running_table.setRowCount(0)
            
            # Enumerate all windows
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    # Get window title
                    title = win32gui.GetWindowText(hwnd)
                    
                    # Skip windows with empty titles or system windows
                    if not title or title == "Program Manager":
                        return True
                    
                    # Get process name
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        process = psutil.Process(pid)
                        process_name = process.name()
                        
                        # Filter for game client windows
                        # Only include TRose.exe or windows with aura/rose in the title
                        if (process_name.lower() == "trose.exe" or 
                            any(game_name in title.lower() for game_name in ["aura", "rose"])):
                            windows.append({
                                "hwnd": hwnd,
                                "title": title,
                                "process": process_name
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                return True
            
            # Get all windows
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            # Sort windows by title
            windows.sort(key=lambda w: w["title"].lower())
            self.window_list = windows
            
            # Populate running clients table
            self.running_table.setRowCount(len(windows))
            for i, window in enumerate(windows):
                # Checkbox column
                checkbox = QTableWidgetItem()
                checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox.setCheckState(Qt.Unchecked)
                
                # Check if this window was previously selected
                if any(w["hwnd"] == window["hwnd"] for w in self.selected_windows):
                    checkbox.setCheckState(Qt.Checked)
                
                self.running_table.setItem(i, 0, checkbox)
                
                # Window title column
                title_item = QTableWidgetItem(window["title"])
                title_item.setData(Qt.UserRole, window)  # Store window data
                self.running_table.setItem(i, 1, title_item)
            
            self.add_log_message(f"Found {len(windows)} client windows")
            
        except Exception as e:
            logger.error(f"Error refreshing window list: {e}")
            self.add_log_message(f"Error: {str(e)}")
    
    def on_item_changed(self, item):
        """Handle checkbox state changes in running clients table"""
        if item.column() == 0:  # Checkbox column
            row = item.row()
            title_item = self.running_table.item(row, 1)
            
            # Check if title_item exists before accessing its data
            if title_item is None:
                logger.error(f"Title item at row {row} is None")
                self.add_log_message(f"Error: Could not find window data for row {row}")
                return
                
            window_data = title_item.data(Qt.UserRole)
            
            if item.checkState() == Qt.Checked:
                # Add to selected windows if not already there
                if not any(w["hwnd"] == window_data["hwnd"] for w in self.selected_windows):
                    self.selected_windows.append(window_data)
            else:
                # Remove from selected windows
                self.selected_windows = [w for w in self.selected_windows if w["hwnd"] != window_data["hwnd"]]
            
            # Update hotkey manager with selected windows
            self.hotkey_manager.set_selected_windows(self.selected_windows)
            self.selection_changed.emit(self.selected_windows)
            
            # Update log
            if item.checkState() == Qt.Checked:
                self.add_log_message(f"Selected client: {window_data['title']}")
            else:
                self.add_log_message(f"Deselected client: {window_data['title']}")
                
    def on_captured_item_changed(self, item):
        """Handle checkbox state changes in captured clients table"""
        if item.column() == 0:  # Checkbox column
            row = item.row()
            title_item = self.captured_table.item(row, 1)
            
            # Check if title_item exists before accessing its data
            if title_item is None:
                logger.error(f"Title item at row {row} is None")
                self.add_log_message(f"Error: Could not find window data for row {row}")
                return
                
            window_data = title_item.data(Qt.UserRole)
            
            if item.checkState() == Qt.Checked:
                # Add to selected windows if not already there
                if not any(w["hwnd"] == window_data["hwnd"] for w in self.selected_windows):
                    self.selected_windows.append(window_data)
            else:
                # Remove from selected windows
                self.selected_windows = [w for w in self.selected_windows if w["hwnd"] != window_data["hwnd"]]
            
            # Update hotkey manager with selected windows
            self.hotkey_manager.set_selected_windows(self.selected_windows)
            self.selection_changed.emit(self.selected_windows)
            
            # Update log
            if item.checkState() == Qt.Checked:
                self.add_log_message(f"Selected captured client: {window_data['title']}")
            else:
                self.add_log_message(f"Deselected captured client: {window_data['title']}")
    
    def toggle_pause(self):
        """Toggle pause state for hotkey actions with animation"""
        try:
            # Create button animation
            animation = QPropertyAnimation(self.pause_button, b"minimumHeight")
            animation.setDuration(150)
            animation.setStartValue(self.pause_button.height())
            animation.setEndValue(self.pause_button.height() + 5)  # Slightly larger
            animation.setEasingCurve(QEasingCurve.OutQuad)
            
            # Create reverse animation
            reverse_animation = QPropertyAnimation(self.pause_button, b"minimumHeight")
            reverse_animation.setDuration(150)
            reverse_animation.setStartValue(self.pause_button.height() + 5)
            reverse_animation.setEndValue(self.pause_button.height())
            reverse_animation.setEasingCurve(QEasingCurve.InQuad)
            
            # Connect animations
            animation.finished.connect(reverse_animation.start)
            
            if self.pause_button.text() == "Pause":
                self.pause_button.setText("Resume")
                self.pause_button.setIcon(AuraIconProvider.get_icon("start"))
                self.pause_button.setStyleSheet(f"background-color: {AuraTheme.SUCCESS};")
                self.add_log_message("Paused client actions")
                self.hotkey_manager.set_pause_state(True)
            else:
                self.pause_button.setText("Pause")
                self.pause_button.setIcon(AuraIconProvider.get_icon("pause"))
                self.pause_button.setStyleSheet(f"background-color: {AuraTheme.PRIMARY};")
                self.add_log_message("Resumed client actions")
                self.hotkey_manager.set_pause_state(False)
                
            # Start animation
            animation.start()
            
        except Exception as e:
            logger.error(f"Error toggling pause state: {e}")
    
    def set_key_delay(self):
        """Set the key delay value"""
        delay = self.delay_input.value()
        self.hotkey_manager.set_key_delay(delay)
        self.add_log_message(f"Set key delay to {delay} seconds")
        
    def capture_selected_clients(self):
        """Move selected clients from running to captured list"""
        # Get selected rows from running table
        selected_rows = []
        for row in range(self.running_table.rowCount()):
            checkbox = self.running_table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.Checked:
                selected_rows.append(row)
        
        # Process in reverse order to avoid index shifting
        for row in sorted(selected_rows, reverse=True):
            # Get window data
            title_item = self.running_table.item(row, 1)
            if title_item is None:
                continue
                
            window_data = title_item.data(Qt.UserRole)
            
            # Add to captured windows list if not already there
            if not any(w["hwnd"] == window_data["hwnd"] for w in self.captured_windows):
                self.captured_windows.append(window_data)
                
                # Add to captured table
                row_position = self.captured_table.rowCount()
                self.captured_table.insertRow(row_position)
                
                # Checkbox column
                checkbox = QTableWidgetItem()
                checkbox.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                checkbox.setCheckState(Qt.Checked if any(w["hwnd"] == window_data["hwnd"] for w in self.selected_windows) else Qt.Unchecked)
                self.captured_table.setItem(row_position, 0, checkbox)
                
                # Window title column
                title_item = QTableWidgetItem(window_data["title"])
                title_item.setData(Qt.UserRole, window_data)  # Store window data
                self.captured_table.setItem(row_position, 1, title_item)
                
                self.add_log_message(f"Captured client: {window_data['title']}")
        
        # Refresh running clients list to remove captured ones
        self.refresh_window_list()
    
    def release_selected_clients(self):
        """Move selected clients from captured back to running list"""
        # Get selected rows from captured table
        selected_rows = []
        for row in range(self.captured_table.rowCount()):
            checkbox = self.captured_table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.Checked:
                selected_rows.append(row)
        
        # Process in reverse order to avoid index shifting
        for row in sorted(selected_rows, reverse=True):
            # Get window data
            title_item = self.captured_table.item(row, 1)
            if title_item is None:
                continue
                
            window_data = title_item.data(Qt.UserRole)
            
            # Remove from captured windows
            self.captured_windows = [w for w in self.captured_windows if w["hwnd"] != window_data["hwnd"]]
            
            # Remove from captured table
            self.captured_table.removeRow(row)
            
            self.add_log_message(f"Released client: {window_data['title']}")
        
        # Refresh running clients list to include released ones
        self.refresh_window_list()
    
    def select_all_clients(self):
        """Select all clients in both running and captured tables"""
        # Select all running clients
        for row in range(self.running_table.rowCount()):
            checkbox = self.running_table.item(row, 0)
            if checkbox and checkbox.checkState() != Qt.Checked:
                checkbox.setCheckState(Qt.Checked)
        
        # Select all captured clients
        for row in range(self.captured_table.rowCount()):
            checkbox = self.captured_table.item(row, 0)
            if checkbox and checkbox.checkState() != Qt.Checked:
                checkbox.setCheckState(Qt.Checked)
        
        self.add_log_message("Selected all clients")
    
    def deselect_all_clients(self):
        """Deselect all clients in both running and captured tables"""
        # Deselect all running clients
        for row in range(self.running_table.rowCount()):
            checkbox = self.running_table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.Checked:
                checkbox.setCheckState(Qt.Unchecked)
        
        # Deselect all captured clients
        for row in range(self.captured_table.rowCount()):
            checkbox = self.captured_table.item(row, 0)
            if checkbox and checkbox.checkState() == Qt.Checked:
                checkbox.setCheckState(Qt.Unchecked)
        
        self.add_log_message("Deselected all clients")
    
    def add_log_message(self, message):
        """Log message using logger"""
        logger.info(message)

# For testing as standalone
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Mock hotkey manager for testing
    class MockHotkeyManager:
        def __init__(self):
            self.key_delay = 0.1
            self.paused = False
            
        def set_selected_windows(self, windows):
            print(f"Set {len(windows)} selected windows")
            
        def set_key_delay(self, delay):
            self.key_delay = delay
            print(f"Set key delay to {delay} seconds")
            
        def set_pause_state(self, paused):
            self.paused = paused
            print(f"{'Paused' if paused else 'Resumed'} client actions")
    
    window = QMainWindow()
    window.setWindowTitle("MultiClient Test")
    window.setMinimumSize(800, 600)
    
    widget = MultiClientWidget(MockHotkeyManager())
    window.setCentralWidget(widget)
    
    window.show()
    sys.exit(app.exec_())
