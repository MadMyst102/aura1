from PyQt5.QtGui import QColor, QPalette, QFont, QIcon, QPixmap, QPainter, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtWidgets import QStyleFactory, QProxyStyle, QStyle, QGraphicsDropShadowEffect
import os

class AuraTheme:
    """
    Custom theme for Aura application with unique visual styling and enhanced modern aesthetics
    """
    # Main color palette - enhanced with more vibrant and modern colors
    PRIMARY = "#5D36D0"  # Refined deep purple
    SECONDARY = "#00C2E0"  # Brighter cyan
    ACCENT = "#FF3D7F"  # Vibrant pink
    BACKGROUND = "#0F0F13"  # Darker, richer background
    CARD_BACKGROUND = "#1A1A22"  # Slightly blue-tinted dark background
    TEXT_PRIMARY = "#FFFFFF"  # White text
    TEXT_SECONDARY = "#B8C4D9"  # Slightly blue-tinted light text
    SUCCESS = "#00D06C"  # Brighter green
    WARNING = "#FFCC00"  # Richer yellow
    ERROR = "#FF2D55"  # Brighter red
    
    # Additional colors for gradients and accents
    GRADIENT_START = "#5D36D0"  # Start of primary gradient
    GRADIENT_END = "#00C2E0"  # End of primary gradient
    ACCENT_GRADIENT_START = "#FF3D7F"  # Start of accent gradient
    ACCENT_GRADIENT_END = "#FF9E80"  # End of accent gradient
    SURFACE_OVERLAY = "rgba(255, 255, 255, 0.05)"  # Subtle overlay for depth
    DIVIDER = "rgba(255, 255, 255, 0.1)"  # Subtle divider color
    
    # Font settings - improved readability
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_NORMAL = 9
    FONT_SIZE_LARGE = 12
    FONT_SIZE_SMALL = 8
    FONT_SIZE_TITLE = 18
    FONT_SIZE_SUBTITLE = 14
    
    # Spacing and sizing constants
    BORDER_RADIUS = "4px"
    BORDER_RADIUS_LARGE = "8px"
    SPACING_SMALL = "5px"
    SPACING_NORMAL = "10px"
    SPACING_LARGE = "15px"
    SHADOW_NORMAL = "0 2px 10px rgba(0, 0, 0, 0.2)"
    SHADOW_LARGE = "0 4px 20px rgba(0, 0, 0, 0.3)"
    
    @staticmethod
    def get_application_palette():
        """Create a custom dark palette with accent colors"""
        palette = QPalette()
        
        # Set colors for different roles
        palette.setColor(QPalette.Window, QColor(AuraTheme.BACKGROUND))
        palette.setColor(QPalette.WindowText, QColor(AuraTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.Base, QColor(AuraTheme.CARD_BACKGROUND))
        palette.setColor(QPalette.AlternateBase, QColor(AuraTheme.BACKGROUND).lighter(110))
        palette.setColor(QPalette.ToolTipBase, QColor(AuraTheme.PRIMARY))
        palette.setColor(QPalette.ToolTipText, QColor(AuraTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.Text, QColor(AuraTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.Button, QColor(AuraTheme.CARD_BACKGROUND))
        palette.setColor(QPalette.ButtonText, QColor(AuraTheme.TEXT_PRIMARY))
        palette.setColor(QPalette.BrightText, QColor(AuraTheme.ACCENT))
        palette.setColor(QPalette.Link, QColor(AuraTheme.SECONDARY))
        palette.setColor(QPalette.Highlight, QColor(AuraTheme.PRIMARY))
        palette.setColor(QPalette.HighlightedText, QColor(AuraTheme.TEXT_PRIMARY))
        
        # Disabled colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(AuraTheme.TEXT_SECONDARY))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(AuraTheme.TEXT_SECONDARY))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(AuraTheme.TEXT_SECONDARY))
        
        return palette
    
    @staticmethod
    def get_application_stylesheet():
        """Create a comprehensive stylesheet for the application with modern styling"""
        return f"""
        /* Global styles */
        QWidget {{  
            background-color: {AuraTheme.BACKGROUND};
            color: {AuraTheme.TEXT_PRIMARY};
            font-family: '{AuraTheme.FONT_FAMILY}';
            font-size: {AuraTheme.FONT_SIZE_NORMAL}pt;
        }}
        
        /* Main window with subtle gradient background */
        QMainWindow {{  
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {AuraTheme.BACKGROUND}, 
                                stop:1 {QColor(AuraTheme.BACKGROUND).lighter(110).name()});
            border: none;
        }}
        
        /* Modern buttons with gradient, hover effects and shadows */
        QPushButton {{  
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {AuraTheme.PRIMARY}, 
                                stop:1 {QColor(AuraTheme.PRIMARY).darker(110).name()});
            color: {AuraTheme.TEXT_PRIMARY};
            border: none;
            border-radius: {AuraTheme.BORDER_RADIUS};
            padding: 8px 16px;
            font-weight: bold;
            min-width: 100px;
            text-transform: uppercase;
            margin: {AuraTheme.SPACING_SMALL};
        }}
        
        QPushButton:hover {{  
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                stop:0 {QColor(AuraTheme.PRIMARY).lighter(110).name()}, 
                                stop:1 {AuraTheme.PRIMARY});
            border-bottom: 2px solid {AuraTheme.ACCENT};
        }}
        
        QPushButton:pressed {{  
            background-color: {QColor(AuraTheme.PRIMARY).darker(120).name()};
            padding-top: 10px;
            padding-bottom: 6px;
        }}
        
        QPushButton:disabled {{  
            background-color: {AuraTheme.CARD_BACKGROUND};
            color: {AuraTheme.TEXT_SECONDARY};
            border-bottom: none;
        }}
        
        /* Special buttons */
        QPushButton#startButton {{  
            background-color: {AuraTheme.SUCCESS};
            font-size: {AuraTheme.FONT_SIZE_LARGE}pt;
        }}
        
        QPushButton#startButton:hover {{  
            background-color: {QColor(AuraTheme.SUCCESS).lighter(120).name()};
        }}
        
        QPushButton#deleteButton {{  
            background-color: {AuraTheme.ERROR};
        }}
        
        QPushButton#deleteButton:hover {{  
            background-color: {QColor(AuraTheme.ERROR).lighter(120).name()};
        }}
        
        /* Tables */
        QTableWidget {{  
            background-color: {AuraTheme.CARD_BACKGROUND};
            alternate-background-color: {QColor(AuraTheme.CARD_BACKGROUND).lighter(110).name()};
            border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            border-radius: 4px;
            gridline-color: {QColor(AuraTheme.CARD_BACKGROUND).lighter(120).name()};
        }}
        
        QTableWidget::item {{  
            padding: 4px;
            border-bottom: 1px solid {QColor(AuraTheme.CARD_BACKGROUND).lighter(120).name()};
        }}
        
        QTableWidget::item:selected {{  
            background-color: {AuraTheme.PRIMARY};
            color: {AuraTheme.TEXT_PRIMARY};
        }}
        
        QHeaderView::section {{  
            background-color: {AuraTheme.CARD_BACKGROUND};
            color: {AuraTheme.SECONDARY};
            padding: 8px;
            border: none;
            border-bottom: 2px solid {AuraTheme.PRIMARY};
            font-weight: bold;
        }}
        
        /* Tabs */
        QTabWidget::pane {{  
            border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            border-radius: 4px;
            background: {AuraTheme.CARD_BACKGROUND};
            top: -1px;
        }}
        
        QTabBar::tab {{  
            background: {AuraTheme.BACKGROUND};
            border: 1px solid {QColor(AuraTheme.CARD_BACKGROUND).lighter(120).name()};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            padding: 8px 12px;
            margin-right: 2px;
            color: {AuraTheme.TEXT_SECONDARY};
        }}
        
        QTabBar::tab:selected {{  
            background: {AuraTheme.PRIMARY};
            color: {AuraTheme.TEXT_PRIMARY};
            border-bottom: none;
        }}
        
        QTabBar::tab:hover:!selected {{  
            background: {QColor(AuraTheme.CARD_BACKGROUND).lighter(120).name()};
            color: {AuraTheme.TEXT_PRIMARY};
        }}
        
        /* Text displays */
        QTextEdit {{  
            background-color: {AuraTheme.CARD_BACKGROUND};
            color: {AuraTheme.TEXT_PRIMARY};
            border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            selection-background-color: {AuraTheme.PRIMARY};
            selection-color: {AuraTheme.TEXT_PRIMARY};
        }}
        
        /* Progress bars */
        QProgressBar {{  
            border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            border-radius: 2px;
            text-align: center;
            background-color: {AuraTheme.CARD_BACKGROUND};
            color: {AuraTheme.TEXT_PRIMARY};
        }}
        
        QProgressBar::chunk {{  
            background-color: {AuraTheme.SECONDARY};
            border-radius: 2px;
        }}
        
        /* Group boxes */
        QGroupBox {{  
            border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            border-radius: 4px;
            margin-top: 20px;
            font-weight: bold;
            color: {AuraTheme.SECONDARY};
        }}
        
        QGroupBox::title {{  
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
            background-color: {AuraTheme.BACKGROUND};
        }}
        
        /* Combo boxes */
        QComboBox {{  
            background-color: {AuraTheme.CARD_BACKGROUND};
            border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            border-radius: 4px;
            padding: 4px 8px;
            min-width: 6em;
        }}
        
        QComboBox:hover {{  
            border: 1px solid {AuraTheme.SECONDARY};
        }}
        
        QComboBox::drop-down {{  
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }}
        
        QComboBox QAbstractItemView {{  
            background-color: {AuraTheme.CARD_BACKGROUND};
            border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            selection-background-color: {AuraTheme.PRIMARY};
            selection-color: {AuraTheme.TEXT_PRIMARY};
        }}
        
        /* Spin boxes */
        QSpinBox, QDoubleSpinBox {{  
            background-color: {AuraTheme.CARD_BACKGROUND};
            border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            border-radius: 4px;
            padding: 4px 8px;
        }}
        
        QSpinBox:hover, QDoubleSpinBox:hover {{  
            border: 1px solid {AuraTheme.SECONDARY};
        }}
        
        /* Line edits */
        QLineEdit {{  
            background-color: {AuraTheme.CARD_BACKGROUND};
            border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            border-radius: 4px;
            padding: 4px 8px;
            selection-background-color: {AuraTheme.PRIMARY};
            selection-color: {AuraTheme.TEXT_PRIMARY};
        }}
        
        QLineEdit:hover {{  
            border: 1px solid {AuraTheme.SECONDARY};
        }}
        
        QLineEdit:focus {{  
            border: 1px solid {AuraTheme.ACCENT};
        }}
        
        /* Checkboxes */
        QCheckBox {{  
            spacing: 5px;
        }}
        
        QCheckBox::indicator {{  
            width: 18px;
            height: 18px;
            border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            border-radius: 3px;
        }}
        
        QCheckBox::indicator:unchecked {{  
            background-color: {AuraTheme.CARD_BACKGROUND};
        }}
        
        QCheckBox::indicator:checked {{  
            background-color: {AuraTheme.PRIMARY};
            image: url(check.png);
        }}
        
        QCheckBox::indicator:hover {{  
            border: 1px solid {AuraTheme.SECONDARY};
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{  
            background: {AuraTheme.BACKGROUND};
            width: 12px;
            margin: 12px 0 12px 0;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{  
            background: {QColor(AuraTheme.PRIMARY).darker(120).name()};
            min-height: 20px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical:hover {{  
            background: {AuraTheme.PRIMARY};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{  
            background: none;
            height: 12px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }}
        
        QScrollBar:horizontal {{  
            background: {AuraTheme.BACKGROUND};
            height: 12px;
            margin: 0 12px 0 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal {{  
            background: {QColor(AuraTheme.PRIMARY).darker(120).name()};
            min-width: 20px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal:hover {{  
            background: {AuraTheme.PRIMARY};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{  
            background: none;
            width: 12px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }}
        
        /* Status bar */
        QStatusBar {{  
            background-color: {AuraTheme.CARD_BACKGROUND};
            color: {AuraTheme.TEXT_PRIMARY};
            border-top: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
        }}
        
        /* Menu and menu items */
        QMenu {{  
            background-color: {AuraTheme.CARD_BACKGROUND};
            border: 1px solid {QColor(AuraTheme.PRIMARY).darker(120).name()};
            border-radius: 4px;
        }}
        
        QMenu::item {{  
            padding: 5px 20px 5px 20px;
        }}
        
        QMenu::item:selected {{  
            background-color: {AuraTheme.PRIMARY};
            color: {AuraTheme.TEXT_PRIMARY};
        }}
        
        QMenu::separator {{  
            height: 1px;
            background-color: {QColor(AuraTheme.PRIMARY).darker(120).name()};
            margin: 5px 0px 5px 0px;
        }}
        """
    
    @staticmethod
    def apply_drop_shadow(widget, color=None, blur_radius=15, x_offset=0, y_offset=3):
        """Apply drop shadow effect to a widget"""
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(blur_radius)
        shadow.setXOffset(x_offset)
        shadow.setYOffset(y_offset)
        
        if color is None:
            color = QColor(AuraTheme.PRIMARY)
            color.setAlpha(80)  # Semi-transparent
        
        shadow.setColor(color)
        widget.setGraphicsEffect(shadow)
    
    @staticmethod
    def create_gradient_background(start_color, end_color, width, height):
        """Create a gradient background pixmap"""
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor(start_color))
        gradient.setColorAt(1, QColor(end_color))
        painter.fillRect(QRect(0, 0, int(width), int(height)), QBrush(gradient))
        painter.end()
        
        return pixmap

class AuraAnimation:
    """Helper class for creating animations in the Aura application"""
    
    @staticmethod
    def fade_in(widget, duration=300, start_value=0.0, end_value=1.0):
        """Create a fade-in animation for a widget"""
        widget.setWindowOpacity(start_value)
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.InOutCubic)
        return animation
    
    @staticmethod
    def fade_out(widget, duration=300, start_value=1.0, end_value=0.0):
        """Create a fade-out animation for a widget"""
        widget.setWindowOpacity(start_value)
        animation = QPropertyAnimation(widget, b"windowOpacity")
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.InOutCubic)
        return animation
    
    @staticmethod
    def slide_in(widget, direction="right", duration=300):
        """Create a slide-in animation for a widget"""
        animation = QPropertyAnimation(widget, b"geometry")
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        
        start_rect = widget.geometry()
        end_rect = widget.geometry()
        
        if direction == "right":
            start_rect.setX(widget.width())
        elif direction == "left":
            start_rect.setX(-widget.width())
        elif direction == "up":
            start_rect.setY(-widget.height())
        elif direction == "down":
            start_rect.setY(widget.height())
        
        animation.setStartValue(start_rect)
        animation.setEndValue(end_rect)
        
        return animation
    
    @staticmethod
    def pulse(widget, property_name, duration=500, min_value=0.8, max_value=1.0):
        """Create a pulsing animation for a widget property"""
        animation = QPropertyAnimation(widget, property_name)
        animation.setDuration(duration)
        animation.setStartValue(min_value)
        animation.setEndValue(max_value)
        animation.setLoopCount(-1)  # Infinite loop
        animation.setEasingCurve(QEasingCurve.InOutSine)
        return animation

class AuraIcons:
    """Custom icon provider for Aura application"""
    
    @staticmethod
    def get_icon(name):
        """Get a themed icon by name"""
        # Standard icons with custom styling
        if name == "start":
            return QIcon.fromTheme("media-playback-start")
        elif name == "stop":
            return QIcon.fromTheme("media-playback-stop")
        elif name == "pause":
            return QIcon.fromTheme("media-playback-pause")
        elif name == "refresh":
            return QIcon.fromTheme("view-refresh")
        elif name == "save":
            return QIcon.fromTheme("document-save")
        elif name == "open":
            return QIcon.fromTheme("document-open")
        elif name == "delete":
            return QIcon.fromTheme("edit-delete")
        elif name == "add":
            return QIcon.fromTheme("list-add")
        elif name == "settings":
            return QIcon.fromTheme("preferences-system")
        elif name == "info":
            return QIcon.fromTheme("dialog-information")
        elif name == "warning":
            return QIcon.fromTheme("dialog-warning")
        elif name == "error":
            return QIcon.fromTheme("dialog-error")
        elif name == "question":
            return QIcon.fromTheme("dialog-question")
        
        # Fallback to system icon
        return QIcon.fromTheme(name)