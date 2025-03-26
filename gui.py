import sys
import os
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLabel, QSystemTrayIcon,
    QMenu, QStyle, QHeaderView, QMessageBox, QTextEdit, QSpinBox,
    QComboBox, QLineEdit, QTabWidget, QFrame, QProgressBar, QCheckBox,
    QGroupBox, QScrollArea, QSplashScreen
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtGui import QIcon, QTextCursor, QPalette, QColor, QFont, QPainter, QPixmap
import win32gui
import win32con
import win32process
import psutil
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis
from datetime import datetime
from loguru import logger

from main import HotkeyManager
from utils import get_config_manager
from theme import AuraTheme, AuraAnimation
from icons import AuraIconProvider
from license_manager import LicenseManager, check_license_and_activate
from license_tab import LicenseTab

class CustomTabWidget(QTabWidget):
    """Enhanced custom styled tab widget with animations"""
    def __init__(self):
        super().__init__()
        # Tab styling is now handled by the global stylesheet
        
        # Add shadow effect to the tab widget
        AuraTheme.apply_drop_shadow(self)
        
    def setCurrentIndex(self, index):
        """Override to add animation when changing tabs"""
        current = self.currentIndex()
        if current != index and current >= 0 and index >= 0:
            # Only animate if we're changing to a different valid tab
            current_widget = self.widget(current)
            next_widget = self.widget(index)
            
            if current_widget and next_widget:
                # Fade out current widget
                fade_out = AuraAnimation.fade_out(current_widget, duration=200)
                fade_out.start()
                
                # Call the parent implementation to change tabs
                super().setCurrentIndex(index)
                
                # Fade in next widget
                fade_in = AuraAnimation.fade_in(next_widget, duration=200)
                fade_in.start()
        else:
            # Just change tabs normally if no animation needed
            super().setCurrentIndex(index)

class StatusBar(QFrame):
    """Enhanced custom status bar with system metrics and visual styling"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
        # Add subtle animation to the status bar
        self.pulse_animation = AuraAnimation.pulse(self, b"minimumHeight", 
                                                 min_value=40, max_value=42, 
                                                 duration=2000)
        self.pulse_animation.start()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        
        # Status indicators with custom styling
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setStyleSheet(f"color: {AuraTheme.ERROR}; font-weight: bold;")
        
        self.executions_label = QLabel("Total Executions: 0")
        self.uptime_label = QLabel("Uptime: 0:00:00")
        
        # Add CPU/Memory usage progress bars with custom styling
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMaximumWidth(150)
        self.cpu_bar.setFormat("CPU: %p%")
        self.cpu_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {AuraTheme.SECONDARY}; }}")
        
        self.memory_bar = QProgressBar()
        self.memory_bar.setMaximumWidth(150)
        self.memory_bar.setFormat("Memory: %p%")
        self.memory_bar.setStyleSheet(f"QProgressBar::chunk {{ background-color: {AuraTheme.PRIMARY}; }}")
        
        # Create a logo label
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.svg").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        
        # Add all widgets to layout
        layout.addWidget(logo_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.executions_label)
        layout.addWidget(self.uptime_label)
        layout.addWidget(self.cpu_bar)
        layout.addWidget(self.memory_bar)
        layout.addStretch()
        
        # Apply shadow effect
        AuraTheme.apply_drop_shadow(self, QColor(0, 0, 0, 50), blur_radius=10)

class AnalyticsWidget(QWidget):
    """Enhanced widget for displaying analytics data with modern styling"""
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header with description
        header = QLabel("Analytics Dashboard")
        header.setStyleSheet(f"font-size: 16pt; font-weight: bold; color: {AuraTheme.SECONDARY};")
        layout.addWidget(header)
        
        description = QLabel("Track your hotkey usage and monitor application performance")
        description.setStyleSheet(f"color: {AuraTheme.TEXT_SECONDARY}; font-size: 10pt;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Create chart for hotkey usage with custom styling
        chart = QChart()
        chart.setTitle("Hotkey Usage Statistics")
        chart.setTitleFont(QFont(AuraTheme.FONT_FAMILY, 12, QFont.Bold))
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setBackgroundVisible(False)
        chart.setBackgroundBrush(QColor(AuraTheme.CARD_BACKGROUND))
        chart.setTitleBrush(QColor(AuraTheme.TEXT_PRIMARY))
        
        self.chart_view = QChartView(chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        AuraTheme.apply_drop_shadow(self.chart_view)
        layout.addWidget(self.chart_view)
        
        # Add error log section with header
        error_header = QLabel("Recent Errors")
        error_header.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {AuraTheme.ERROR};")
        layout.addWidget(error_header)
        
        # Add error log table with custom styling
        self.error_table = QTableWidget()
        self.error_table.setColumnCount(3)
        self.error_table.setHorizontalHeaderLabels(["Time", "Hotkey", "Error"])
        self.error_table.setAlternatingRowColors(True)
        header = self.error_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        AuraTheme.apply_drop_shadow(self.error_table, QColor(AuraTheme.ERROR).darker(150), blur_radius=10)
        layout.addWidget(self.error_table)
        
    def update_chart(self, analytics_data):
        """Update chart with new analytics data"""
        chart = self.chart_view.chart()
        chart.removeAllSeries()
        
        # Create bar series
        series = QBarSeries()
        
        # Add data
        hotkey_set = QBarSet("Usage Count")
        categories = []
        
        for hotkey, count in analytics_data['hotkey_usage'].items():
            hotkey_set.append(count)
            categories.append(hotkey)
        
        series.append(hotkey_set)
        chart.addSeries(series)
        
        # Set up axes
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
    def update_error_table(self, errors):
        """Update error table with new data"""
        self.error_table.setRowCount(len(errors))
        for i, error in enumerate(errors):
            self.error_table.setItem(i, 0, QTableWidgetItem(error['time']))
            self.error_table.setItem(i, 1, QTableWidgetItem(error['hotkey']))
            self.error_table.setItem(i, 2, QTableWidgetItem(error['error']))

class WindowSelectionWidget(QWidget):
    """Widget for selecting windows to send hotkey actions to"""
    def __init__(self, hotkey_manager):
        super().__init__()
        self.hotkey_manager = hotkey_manager
        self.window_list = []
        self.selected_windows = []
        self.setup_ui()
        self.refresh_window_list()
        
    def setup_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header with instructions
        header_label = QLabel(
            "Select windows to send hotkey actions to without moving the mouse. "
            "When windows are selected, hotkeys will send clicks directly to these windows."
        )
        header_label.setWordWrap(True)
        header_label.setStyleSheet("font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh Window List")
        refresh_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        refresh_button.clicked.connect(self.refresh_window_list)
        control_layout.addWidget(refresh_button)
        
        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all_windows)
        control_layout.addWidget(select_all_button)
        
        clear_button = QPushButton("Clear Selection")
        clear_button.clicked.connect(self.clear_selection)
        control_layout.addWidget(clear_button)
        
        apply_button = QPushButton("Apply Selection")
        apply_button.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        apply_button.clicked.connect(self.apply_selection)
        control_layout.addWidget(apply_button)
        
        layout.addLayout(control_layout)
        
        # Create scroll area for window list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.StyledPanel)
        
        # Container for checkboxes
        self.window_container = QWidget()
        self.window_layout = QVBoxLayout(self.window_container)
        self.window_layout.setSpacing(5)
        self.window_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(self.window_container)
        layout.addWidget(scroll_area)
        
        # Status label
        self.status_label = QLabel("No windows selected")
        layout.addWidget(self.status_label)
    
    def refresh_window_list(self):
        """Refresh the list of available windows"""
        try:
            # Clear existing window list
            self.window_list = []
            
            # Clear existing checkboxes
            while self.window_layout.count():
                item = self.window_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
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
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        process_name = "Unknown"
                    
                    # Add window to list
                    windows.append({
                        "hwnd": hwnd,
                        "title": title,
                        "process": process_name
                    })
                return True
            
            # Get all windows
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            # Sort windows by title
            windows.sort(key=lambda w: w["title"].lower())
            self.window_list = windows
            
            # Create checkboxes for each window
            for window in windows:
                group_box = QGroupBox()
                group_layout = QVBoxLayout(group_box)
                
                # Create checkbox with window title
                checkbox = QCheckBox(f"{window['title']} ({window['process']})")
                checkbox.setProperty("hwnd", window["hwnd"])
                checkbox.setProperty("window_data", window)
                
                # Check if this window was previously selected
                if any(w["hwnd"] == window["hwnd"] for w in self.selected_windows):
                    checkbox.setChecked(True)
                
                group_layout.addWidget(checkbox)
                
                # Add window info
                try:
                    left, top, right, bottom = win32gui.GetWindowRect(window["hwnd"])
                    info_label = QLabel(f"Position: ({left}, {top}) - Size: {right-left}×{bottom-top}")
                    info_label.setStyleSheet("color: #666; font-size: 10px;")
                    group_layout.addWidget(info_label)
                except:
                    pass
                
                self.window_layout.addWidget(group_box)
            
            # Update status label
            self.update_status_label()
            logger.info(f"Refreshed window list, found {len(windows)} windows")
            
        except Exception as e:
            logger.error(f"Error refreshing window list: {e}")
    
    def select_all_windows(self):
        """Select all windows in the list"""
        for i in range(self.window_layout.count()):
            item = self.window_layout.itemAt(i)
            if item and item.widget():
                group_box = item.widget()
                for j in range(group_box.layout().count()):
                    child_item = group_box.layout().itemAt(j)
                    if child_item and child_item.widget() and isinstance(child_item.widget(), QCheckBox):
                        child_item.widget().setChecked(True)
        
        self.update_status_label()
    
    def clear_selection(self):
        """Clear all window selections"""
        for i in range(self.window_layout.count()):
            item = self.window_layout.itemAt(i)
            if item and item.widget():
                group_box = item.widget()
                for j in range(group_box.layout().count()):
                    child_item = group_box.layout().itemAt(j)
                    if child_item and child_item.widget() and isinstance(child_item.widget(), QCheckBox):
                        child_item.widget().setChecked(False)
        
        self.selected_windows = []
        self.update_status_label()
    
    def apply_selection(self):
        """Apply the current window selection to the hotkey manager"""
        try:
            self.selected_windows = []
            
            # Get all selected windows
            for i in range(self.window_layout.count()):
                item = self.window_layout.itemAt(i)
                if item and item.widget():
                    group_box = item.widget()
                    for j in range(group_box.layout().count()):
                        child_item = group_box.layout().itemAt(j)
                        if child_item and child_item.widget() and isinstance(child_item.widget(), QCheckBox):
                            checkbox = child_item.widget()
                            if checkbox.isChecked():
                                window_data = checkbox.property("window_data")
                                if window_data:
                                    self.selected_windows.append(window_data)
            
            # Update hotkey manager
            self.hotkey_manager.set_selected_windows(self.selected_windows)
            
            # Update status label
            self.update_status_label()
            
            logger.info(f"Applied selection of {len(self.selected_windows)} windows")
            
        except Exception as e:
            logger.error(f"Error applying window selection: {e}")
    
    def update_status_label(self):
        """Update the status label with current selection info"""
        count = 0
        for i in range(self.window_layout.count()):
            item = self.window_layout.itemAt(i)
            if item and item.widget():
                group_box = item.widget()
                for j in range(group_box.layout().count()):
                    child_item = group_box.layout().itemAt(j)
                    if child_item and child_item.widget() and isinstance(child_item.widget(), QCheckBox):
                        if child_item.widget().isChecked():
                            count += 1
        
        if count == 0:
            self.status_label.setText("No windows selected")
            self.status_label.setStyleSheet("color: #f44336;")
        else:
            self.status_label.setText(f"{count} windows selected")
            self.status_label.setStyleSheet("color: #4caf50;")
    
    def get_selected_windows(self):
        """Return the list of selected windows"""
        return self.selected_windows

class LogDisplay(QTextEdit):
    """Enhanced log display with syntax highlighting, custom formatting and animations"""
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setMaximumHeight(150)
        
        # Set custom styling
        self.setStyleSheet(f"""
            QTextEdit {{  
                background-color: {AuraTheme.CARD_BACKGROUND};
                color: {AuraTheme.TEXT_PRIMARY};
                border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                selection-background-color: {AuraTheme.PRIMARY};
                selection-color: {AuraTheme.TEXT_PRIMARY};
            }}
        """)
        
        # Apply shadow effect
        AuraTheme.apply_drop_shadow(self)
        
    def append_log(self, message: str):
        """Append a log message with color formatting and scroll to bottom"""
        # Format message based on content
        formatted_message = message
        
        if "error" in message.lower() or "failed" in message.lower():
            formatted_message = f"<span style='color:{AuraTheme.ERROR};'>{message}</span>"
        elif "warning" in message.lower():
            formatted_message = f"<span style='color:{AuraTheme.WARNING};'>{message}</span>"
        elif "success" in message.lower() or "started" in message.lower():
            formatted_message = f"<span style='color:{AuraTheme.SUCCESS};'>{message}</span>"
        elif "config" in message.lower() or "loaded" in message.lower():
            formatted_message = f"<span style='color:{AuraTheme.SECONDARY};'>{message}</span>"
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"<span style='color:{AuraTheme.TEXT_SECONDARY};'>[{timestamp}]</span> {formatted_message}"
        
        # Append to log
        self.append(formatted_message)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

class MainWindow(QMainWindow):
    """Enhanced main window with modern UI, animations, and additional features"""
    def __init__(self):
        super().__init__()
        self.config_manager = get_config_manager()
        
        # Check license before initializing
        self.license_manager = check_license_and_activate()
        self.hotkey_manager = HotkeyManager()
        
        # Apply theme before setting up UI
        self.apply_theme()
        
        # Setup UI components
        self.setup_ui()
        
        # Setup status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # Update every second
    
    def apply_theme(self):
        """Apply the custom Aura theme to the application"""
        # Set application palette
        self.setPalette(AuraTheme.get_application_palette())
        
        # Set application stylesheet
        self.setStyleSheet(AuraTheme.get_application_stylesheet())
        
        # Set window icon
        self.setWindowIcon(QIcon("logo.svg"))
        
    def setup_ui(self):
        """Initialize the enhanced user interface with modern styling and animations"""
        # Set window properties with optimized size for improved layout
        self.setWindowTitle("AURA pro+ farm")
        self.setMinimumSize(1400, 900)  # Larger minimum size to accommodate wider tables
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Create header with logo and title
        header_layout = QHBoxLayout()
        
        # Add logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.svg").scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        header_layout.addWidget(logo_label)
        
        # Add title and subtitle
        title_layout = QVBoxLayout()
        title_label = QLabel("AURA pro+ farm")
        title_label.setStyleSheet(f"font-size: 24pt; font-weight: bold; color: {AuraTheme.PRIMARY};")
        subtitle_label = QLabel("Advanced Hotkey Automation Tool")
        subtitle_label.setStyleSheet(f"font-size: 12pt; color: {AuraTheme.SECONDARY};")
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        header_layout.addLayout(title_layout)
        
        # Add start button to header
        start_button = QPushButton("Start Listener")
        start_button.setObjectName("startButton")  # For special styling
        start_button.setIcon(AuraIconProvider.get_icon("start"))
        start_button.setIconSize(QSize(24, 24))
        start_button.setMinimumHeight(50)
        start_button.clicked.connect(self.toggle_listener)
        self.start_button = start_button
        header_layout.addStretch()
        header_layout.addWidget(start_button)
        
        layout.addLayout(header_layout)
        
        # Create tab widget with custom styling
        self.tabs = CustomTabWidget()
        
        # MultiClient tab
        from multiclient import MultiClientWidget
        self.multiclient_widget = MultiClientWidget(self.hotkey_manager)
        self.tabs.addTab(self.multiclient_widget, "MultiClient")
        
        # License tab
        self.license_tab = LicenseTab(self.license_manager)
        self.tabs.addTab(self.license_tab, "License")

        # Analytics tab
        self.analytics_widget = AnalyticsWidget()
        self.tabs.addTab(self.analytics_widget, "Analytics")
        
        # Add tab widget to main layout
        layout.addWidget(self.tabs)
        
        # Enhanced log display with title
        log_header = QLabel("Application Logs")
        log_header.setStyleSheet(f"font-size: 12pt; font-weight: bold; color: {AuraTheme.SECONDARY};")
        layout.addWidget(log_header)
        
        self.log_display = LogDisplay()
        self.log_display.setMaximumHeight(150)
        layout.addWidget(self.log_display)
        
        # Add status bar
        self.status_bar = StatusBar()
        layout.addWidget(self.status_bar)
        
        # Set up system tray
        self.setup_system_tray()
        
        # Load initial configuration
        self.load_config_to_table()
        
        # Log startup message
        self.log_display.append_log("Application started successfully")
        
    def on_profile_loaded(self, config):
        """Handle profile loaded event"""
        try:
            # Apply the loaded configuration to the hotkey manager
            self.hotkey_manager.config = config
            
            # Reload the UI with the new configuration
            self.load_config_to_table()
            
            # Log success message
            self.log_display.append_log(f"Successfully loaded profile configuration")
            
            # Apply animation to indicate successful profile change
            fade_animation = AuraAnimation.fade_in(self.tabs.currentWidget(), duration=300, start_value=0.8)
            fade_animation.start()
        except Exception as e:
            self.log_display.append_log(f"Error applying profile configuration: {e}")
            logger.error(f"Error in on_profile_loaded: {e}")
        
        
    def setup_system_tray(self):
        """Set up enhanced system tray with more options"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        
        # Create enhanced tray menu
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction(self.style().standardIcon(QStyle.SP_ComputerIcon), "Show Window")
        show_action.triggered.connect(self.show)
        
        toggle_action = tray_menu.addAction(self.style().standardIcon(QStyle.SP_MediaPlay), "Start Listener")
        toggle_action.triggered.connect(self.toggle_listener)
        self.tray_toggle_action = toggle_action
        
        reload_action = tray_menu.addAction(self.style().standardIcon(QStyle.SP_BrowserReload), "Reload Config")
        reload_action.triggered.connect(self.reload_config)
        
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction(self.style().standardIcon(QStyle.SP_DialogCloseButton), "Quit")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def load_config_to_table(self):
        """Load configuration"""
        try:
            # Just reload the config without table loading
            self.hotkey_manager.reload_config()
            self.log_display.append_log("Configuration loaded successfully")
        except Exception as e:
            self.log_display.append_log(f"Error loading configuration: {e}")

    def save_config(self):
        """Save configuration"""
        try:
            # Configuration is now saved directly through the hotkey manager
            self.log_display.append_log(f"Configuration saved successfully")
                
        except Exception as e:
            self.log_display.append_log(f"Error saving configuration: {e}")
            
    def reload_config(self):
        """Reload configuration from file"""
        try:
            self.hotkey_manager.reload_config()
            self.load_config_to_table()
            
            self.log_display.append_log("Configuration reloaded successfully")
        except Exception as e:
            self.log_display.append_log(f"Error reloading configuration: {e}")
            
    def toggle_listener(self):
        """Toggle the hotkey listener with enhanced feedback"""
        try:
            if self.hotkey_manager.running:
                self.hotkey_manager.stop()
                self.start_button.setText("Start Listener")
                self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                self.tray_toggle_action.setText("Start Listener")
                self.tray_toggle_action.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
                self.status_bar.status_label.setText("Status: Stopped")
                self.status_bar.status_label.setStyleSheet("color: #f44336;")
                self.log_display.append_log("Hotkey listener stopped")
            else:
                self.hotkey_manager.start()
                self.start_button.setText("Stop Listener")
                self.start_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
                self.tray_toggle_action.setText("Stop Listener")
                self.tray_toggle_action.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
                self.status_bar.status_label.setText("Status: Running")
                self.status_bar.status_label.setStyleSheet("color: #4caf50;")
                self.log_display.append_log("Hotkey listener started")
        except Exception as e:
            self.log_display.append_log(f"Error toggling listener: {e}")
            
    def quit_application(self):
        """Clean up and quit the application"""
        try:
            self.status_timer.stop()
            self.hotkey_manager.stop()
            self.tray_icon.hide()
            QApplication.quit()
        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")
            
    def update_status(self):
        """Update status bar information"""
        if hasattr(self, 'hotkey_manager'):
            self.status_bar.executions_label.setText(f"Total Executions: {self.hotkey_manager.analytics['total_executions']}")
            if self.hotkey_manager.running:
                uptime = datetime.now() - self.hotkey_manager.start_time
                self.status_bar.uptime_label.setText(f"Uptime: {str(uptime).split('.')[0]}")
            
            # Update system metrics (example values - implement actual monitoring)
            self.status_bar.cpu_bar.setValue(50)
            self.status_bar.memory_bar.setValue(30)
    
    def closeEvent(self, event):
        """Enhanced window close event handler"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Application Minimized",
            "The application is still running in the system tray.",
            QSystemTrayIcon.Information,
            2000
        )

def main():
    """Main entry point for the GUI application"""
    app = QApplication(sys.argv)
    
    # Set application-wide style
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
