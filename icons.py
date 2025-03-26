from PyQt5.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QColor, QBrush, QPen, QFont, QFontMetrics
from PyQt5.QtCore import Qt, QSize, QRect, QPoint
import os
import math

class AuraIconProvider:
    """
    Custom icon provider for Aura application that creates unique, modern icons
    """
    
    # Icon cache to avoid recreating icons
    _icon_cache = {}
    
    @staticmethod
    def get_icon(name, color=None, size=None):
        """Get a custom icon by name"""
        # Use cached icon if available
        cache_key = f"{name}_{color}_{size}"
        if cache_key in AuraIconProvider._icon_cache:
            return AuraIconProvider._icon_cache[cache_key]
            
        # Create icon
        icon = AuraIconProvider._create_icon(name, color, size)
        
        # Cache the icon
        AuraIconProvider._icon_cache[cache_key] = icon
        
        return icon
    
    @staticmethod
    def _create_icon(name, color=None, size=None, with_effects=True):
        """Create a custom vector icon with modern effects"""
        # Default size
        if size is None:
            size = QSize(24, 24)
        elif isinstance(size, int):
            size = QSize(size, size)
            
        # Default color from theme
        from theme import AuraTheme
        if color is None:
            color = QColor(AuraTheme.SECONDARY)
        elif isinstance(color, str):
            color = QColor(color)
        
        # Create pixmap
        pixmap = QPixmap(size)
        pixmap.fill(Qt.transparent)
        
        # Create painter
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # Draw icon based on name
        if name == "start":
            AuraIconProvider._draw_start_icon(painter, size, color)
        elif name == "stop":
            AuraIconProvider._draw_stop_icon(painter, size, color)
        elif name == "pause":
            AuraIconProvider._draw_pause_icon(painter, size, color)
        elif name == "refresh":
            AuraIconProvider._draw_refresh_icon(painter, size, color)
        elif name == "save":
            AuraIconProvider._draw_save_icon(painter, size, color)
        elif name == "open":
            AuraIconProvider._draw_open_icon(painter, size, color)
        elif name == "delete":
            AuraIconProvider._draw_delete_icon(painter, size, color)
        elif name == "add":
            AuraIconProvider._draw_add_icon(painter, size, color)
        elif name == "settings":
            AuraIconProvider._draw_settings_icon(painter, size, color)
        elif name == "profile":
            AuraIconProvider._draw_profile_icon(painter, size, color)
        elif name == "window":
            AuraIconProvider._draw_window_icon(painter, size, color)
        elif name == "hotkey":
            AuraIconProvider._draw_hotkey_icon(painter, size, color)
        elif name == "analytics":
            AuraIconProvider._draw_analytics_icon(painter, size, color)
        elif name == "info":
            AuraIconProvider._draw_info_icon(painter, size, color)
        elif name == "warning":
            AuraIconProvider._draw_warning_icon(painter, size, color)
        elif name == "error":
            AuraIconProvider._draw_error_icon(painter, size, color)
        elif name == "logo":
            AuraIconProvider._draw_logo_icon(painter, size, color)
        else:
            # Fallback: draw text icon
            AuraIconProvider._draw_text_icon(painter, size, name[0].upper(), color)
        
        painter.end()
        
        return QIcon(pixmap)
    
    @staticmethod
    def _draw_start_icon(painter, size, color):
        """Draw a unique play icon"""
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        
        # Create a triangular play shape
        path = QPainterPath()
        path.moveTo(size.width() * 0.25, size.height() * 0.2)
        path.lineTo(size.width() * 0.25, size.height() * 0.8)
        path.lineTo(size.width() * 0.8, size.height() * 0.5)
        path.closeSubpath()
        
        painter.drawPath(path)
    
    @staticmethod
    def _draw_stop_icon(painter, size, color):
        """Draw a unique stop icon"""
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        
        # Create a rounded square
        rect = QRect(int(size.width() * 0.25), int(size.height() * 0.25), 
                     int(size.width() * 0.5), int(size.height() * 0.5))
        painter.drawRoundedRect(rect, 2, 2)
    
    @staticmethod
    def _draw_pause_icon(painter, size, color):
        """Draw a unique pause icon"""
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(color))
        
        # Create two rounded rectangles
        rect1 = QRect(int(size.width() * 0.25), int(size.height() * 0.2), 
                      int(size.width() * 0.2), int(size.height() * 0.6))
        rect2 = QRect(int(size.width() * 0.55), int(size.height() * 0.2), 
                      int(size.width() * 0.2), int(size.height() * 0.6))
        
        painter.drawRoundedRect(rect1, 2, 2)
        painter.drawRoundedRect(rect2, 2, 2)
    
    @staticmethod
    def _draw_refresh_icon(painter, size, color):
        """Draw a unique refresh icon"""
        pen = QPen(color, size.width() * 0.1)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        
        # Create a circular arrow
        rect = QRect(int(size.width() * 0.2), int(size.height() * 0.2), 
                     int(size.width() * 0.6), int(size.height() * 0.6))
        
        # Draw 3/4 of a circle
        painter.drawArc(rect, 0, 270 * 16)
        
        # Draw arrowhead
        path = QPainterPath()
        path.moveTo(size.width() * 0.2, size.height() * 0.5)
        path.lineTo(size.width() * 0.3, size.height() * 0.3)
        path.lineTo(size.width() * 0.4, size.height() * 0.5)
        
        painter.drawPath(path)
    
    @staticmethod
    def _draw_save_icon(painter, size, color):
        """Draw a unique save icon"""
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        
        # Draw floppy disk outline
        rect = QRect(int(size.width() * 0.2), int(size.height() * 0.2), 
                     int(size.width() * 0.6), int(size.height() * 0.6))
        painter.drawRect(rect)
        
        # Draw label area
        label_rect = QRect(int(size.width() * 0.3), int(size.height() * 0.3), 
                          int(size.width() * 0.4), int(size.height() * 0.2))
        painter.drawRect(label_rect)
        
        # Draw bottom notch
        notch_rect = QRect(int(size.width() * 0.35), int(size.height() * 0.6), 
                          int(size.width() * 0.3), int(size.height() * 0.1))
        painter.drawRect(notch_rect)
    
    @staticmethod
    def _draw_open_icon(painter, size, color):
        """Draw a unique open folder icon"""
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        
        # Draw folder base
        path = QPainterPath()
        path.moveTo(size.width() * 0.2, size.height() * 0.3)
        path.lineTo(size.width() * 0.4, size.height() * 0.3)
        path.lineTo(size.width() * 0.45, size.height() * 0.4)
        path.lineTo(size.width() * 0.8, size.height() * 0.4)
        path.lineTo(size.width() * 0.7, size.height() * 0.7)
        path.lineTo(size.width() * 0.2, size.height() * 0.7)
        path.closeSubpath()
        
        painter.drawPath(path)
    
    @staticmethod
    def _draw_delete_icon(painter, size, color):
        """Draw a unique delete/trash icon"""
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        
        # Draw trash can lid
        lid_path = QPainterPath()
        lid_path.moveTo(size.width() * 0.2, size.height() * 0.25)
        lid_path.lineTo(size.width() * 0.8, size.height() * 0.25)
        lid_path.lineTo(size.width() * 0.75, size.height() * 0.3)
        lid_path.lineTo(size.width() * 0.25, size.height() * 0.3)
        lid_path.closeSubpath()
        
        painter.drawPath(lid_path)
        
        # Draw trash can body
        body_path = QPainterPath()
        body_path.moveTo(size.width() * 0.3, size.height() * 0.3)
        body_path.lineTo(size.width() * 0.7, size.height() * 0.3)
        body_path.lineTo(size.width() * 0.65, size.height() * 0.8)
        body_path.lineTo(size.width() * 0.35, size.height() * 0.8)
        body_path.closeSubpath()
        
        painter.drawPath(body_path)

    @staticmethod
    def _draw_add_icon(painter, size, color):
        """Draw a unique add/plus icon"""
        pen = QPen(color, size.width() * 0.15)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Draw plus sign
        painter.drawLine(QPoint(int(size.width() * 0.5), int(size.height() * 0.25)), 
                        QPoint(int(size.width() * 0.5), int(size.height() * 0.75)))
        painter.drawLine(QPoint(int(size.width() * 0.25), int(size.height() * 0.5)), 
                        QPoint(int(size.width() * 0.75), int(size.height() * 0.5)))

    @staticmethod
    def _draw_settings_icon(painter, size, color):
        """Draw a unique settings/gear icon"""
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        
        # Draw gear teeth
        center = QPoint(int(size.width() / 2), int(size.height() / 2))
        outer_radius = min(size.width(), size.height()) * 0.4
        inner_radius = outer_radius * 0.6
        teeth = 8
        
        path = QPainterPath()
        
        for i in range(teeth * 2):
            angle = i * 3.14159 / teeth
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = center.x() + radius * math.cos(angle)
            y = center.y() + radius * math.sin(angle)
            
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
                
        path.closeSubpath()
        painter.drawPath(path)
        
        # Draw inner circle
        painter.drawEllipse(center, int(inner_radius * 0.5), int(inner_radius * 0.5))
    
    @staticmethod
    def _draw_profile_icon(painter, size, color):
        """Draw a unique profile/user icon"""
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        
        # Draw head circle
        head_center = QPoint(int(size.width() * 0.5), int(size.height() * 0.35))
        head_radius = int(size.width() * 0.2)
        painter.drawEllipse(head_center, head_radius, head_radius)
        
        # Draw body shape
        body_path = QPainterPath()
        body_path.moveTo(size.width() * 0.3, size.height() * 0.85)
        body_path.quadTo(QPoint(int(size.width() * 0.5), int(size.height() * 0.6)), 
                        QPoint(int(size.width() * 0.7), int(size.height() * 0.85)))
        body_path.closeSubpath()
        
        painter.drawPath(body_path)
    
    @staticmethod
    def _draw_window_icon(painter, size, color):
        """Draw a unique window icon"""
        painter.setPen(QPen(color, max(1, int(size.width() * 0.05))))
        painter.setBrush(Qt.NoBrush)
        
        # Draw window frame
        frame = QRect(int(size.width() * 0.2), int(size.height() * 0.2),
                     int(size.width() * 0.6), int(size.height() * 0.6))
        painter.drawRect(frame)
        
        # Draw title bar
        title_bar = QRect(int(size.width() * 0.2), int(size.height() * 0.2),
                         int(size.width() * 0.6), int(size.height() * 0.15))
        painter.setBrush(QBrush(color))
        painter.drawRect(title_bar)
    
    @staticmethod
    def _draw_hotkey_icon(painter, size, color):
        """Draw a unique hotkey/keyboard icon"""
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        
        # Draw keyboard outline
        rect = QRect(int(size.width() * 0.2), int(size.height() * 0.3),
                    int(size.width() * 0.6), int(size.height() * 0.4))
        painter.drawRoundedRect(rect, 2, 2)
        
        # Draw key symbols
        key_size = size.width() * 0.12
        spacing = size.width() * 0.15
        start_x = size.width() * 0.25
        start_y = size.height() * 0.35
        
        for i in range(3):
            x = start_x + (i * spacing)
            key_rect = QRect(int(x), int(start_y), int(key_size), int(key_size))
            painter.drawRect(key_rect)
    
    @staticmethod
    def _draw_analytics_icon(painter, size, color):
        """Draw a unique analytics/chart icon"""
        painter.setPen(QPen(color, max(1, int(size.width() * 0.08))))
        painter.setBrush(Qt.NoBrush)
        
        # Draw bar chart
        painter.drawLine(QPoint(int(size.width() * 0.3), int(size.height() * 0.7)),
                        QPoint(int(size.width() * 0.3), int(size.height() * 0.4)))
        painter.drawLine(QPoint(int(size.width() * 0.5), int(size.height() * 0.7)),
                        QPoint(int(size.width() * 0.5), int(size.height() * 0.3)))
        painter.drawLine(QPoint(int(size.width() * 0.7), int(size.height() * 0.7)),
                        QPoint(int(size.width() * 0.7), int(size.height() * 0.5)))
        
        # Draw base line
        painter.drawLine(QPoint(int(size.width() * 0.2), int(size.height() * 0.7)),
                        QPoint(int(size.width() * 0.8), int(size.height() * 0.7)))
    
    @staticmethod
    def _draw_info_icon(painter, size, color):
        """Draw a unique info icon"""
        painter.setPen(QPen(color, max(1, int(size.width() * 0.05))))
        painter.setBrush(QBrush(color))
        
        # Draw circle
        center = QPoint(int(size.width() / 2), int(size.height() / 2))
        painter.drawEllipse(center, int(size.width() * 0.35), int(size.height() * 0.35))
        
        # Draw 'i' in white
        painter.setPen(QPen(Qt.white, max(1, int(size.width() * 0.1))))
        painter.drawLine(QPoint(int(size.width() * 0.5), int(size.height() * 0.35)),
                        QPoint(int(size.width() * 0.5), int(size.height() * 0.4)))
        painter.drawLine(QPoint(int(size.width() * 0.5), int(size.height() * 0.45)),
                        QPoint(int(size.width() * 0.5), int(size.height() * 0.65)))
    
    @staticmethod
    def _draw_warning_icon(painter, size, color):
        """Draw a unique warning/triangle icon"""
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        
        # Draw warning triangle
        path = QPainterPath()
        path.moveTo(size.width() * 0.5, size.height() * 0.2)
        path.lineTo(size.width() * 0.8, size.height() * 0.75)
        path.lineTo(size.width() * 0.2, size.height() * 0.75)
        path.closeSubpath()
        
        painter.drawPath(path)
        
        # Draw exclamation mark in white
        painter.setPen(QPen(Qt.white, max(1, int(size.width() * 0.1))))
        painter.drawLine(QPoint(int(size.width() * 0.5), int(size.height() * 0.35)),
                        QPoint(int(size.width() * 0.5), int(size.height() * 0.55)))
        painter.drawEllipse(QPoint(int(size.width() * 0.5), int(size.height() * 0.65)),
                          int(size.width() * 0.03), int(size.width() * 0.03))
    
    @staticmethod
    def _draw_error_icon(painter, size, color):
        """Draw a unique error/x icon"""
        painter.setPen(QPen(color, max(1, int(size.width() * 0.05))))
        painter.setBrush(QBrush(color))
        
        # Draw circle
        center = QPoint(int(size.width() / 2), int(size.height() / 2))
        painter.drawEllipse(center, int(size.width() * 0.35), int(size.height() * 0.35))
        
        # Draw 'X' in white
        painter.setPen(QPen(Qt.white, max(1, int(size.width() * 0.1))))
        painter.drawLine(QPoint(int(size.width() * 0.35), int(size.height() * 0.35)),
                        QPoint(int(size.width() * 0.65), int(size.height() * 0.65)))
        painter.drawLine(QPoint(int(size.width() * 0.65), int(size.height() * 0.35)),
                        QPoint(int(size.width() * 0.35), int(size.height() * 0.65)))
    
    @staticmethod
    def _draw_logo_icon(painter, size, color):
        """Draw application logo"""
        painter.setPen(QPen(color, max(1, int(size.width() * 0.08))))
        painter.setBrush(Qt.NoBrush)
        
        # Draw stylized 'A' for Aura
        path = QPainterPath()
        path.moveTo(size.width() * 0.3, size.height() * 0.8)
        path.lineTo(size.width() * 0.5, size.height() * 0.2)
        path.lineTo(size.width() * 0.7, size.height() * 0.8)
        
        # Draw crossbar
        path.moveTo(size.width() * 0.35, size.height() * 0.6)
        path.lineTo(size.width() * 0.65, size.height() * 0.6)
        
        painter.drawPath(path)
    
    @staticmethod
    def _draw_text_icon(painter, size, text, color):
        """Draw a fallback text icon"""
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        
        # Draw circle background
        center = QPoint(int(size.width() / 2), int(size.height() / 2))
        painter.drawEllipse(center, int(size.width() * 0.35), int(size.height() * 0.35))
        
        # Draw text in white
        font = QFont()
        font.setPointSize(int(size.height() * 0.4))
        font.setBold(True)
        painter.setFont(font)
        
        painter.setPen(Qt.white)
        painter.drawText(QRect(0, 0, size.width(), size.height()),
                        Qt.AlignCenter, text)
