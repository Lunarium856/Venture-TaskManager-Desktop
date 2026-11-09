from PyQt6.QtWidgets import QPushButton, QScrollBar, QStyleOptionSlider, QStyle
from PyQt6.QtCore import QEvent, Qt, QVariantAnimation
from PyQt6.QtGui import QColor, QPainter, QPen
import Themes

class HoverButton(QPushButton):
    def __init__(self, text, parent=None, animator=None):
        super().__init__(text, parent)
        self.animator = animator
        
        # Default colors (create settings in Settings.py)
        self.anim_type = ["border"]
        self.start_val = []
        self.end_val = []

    def setHoverData(self, anim_type, start_val, end_val):
        """
        Store animation details
        """
        self.anim_type = anim_type
        self.start_val = start_val
        self.end_val = end_val

    def enterEvent(self, event):
        """Auto-triggers when mouse enters"""
        if self.animator and self.start_val and self.end_val:
            self.animator.animateOnHover(
                self, 
                self.anim_type, 
                self.start_val, 
                self.end_val
            )
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Auto-triggers when mouse leaves"""
        if self.animator and self.start_val and self.end_val:
            # Swap start and end values to reverse the animation
            self.animator.animateOnHover(
                self, 
                self.anim_type, 
                self.end_val, 
                self.start_val
            )
        super().leaveEvent(event)


class RoundedScrollBar(QScrollBar):
    """Custom painted scrollbar because QSS is annoying"""
    def __init__(self, orientation=Qt.Orientation.Vertical, parent=None, controller=None):
        super().__init__(orientation, parent)
        self.controller = controller
        theme = self.controller.current_theme if (self.controller and hasattr(self.controller, 'current_theme')) else Themes.THEME_DEFAULT
        
        self.handle_color = QColor(f"{theme.scroll_handle}")
        self.setMouseTracking(True)
        
        # Smooth color fading animation for hover state
        self.color_anim = QVariantAnimation(self)
        self.color_anim.setDuration(200)
        self.color_anim.valueChanged.connect(self._on_color_anim_value)

    def _on_color_anim_value(self, color):
        self.handle_color = color
        self.update()

    def enterEvent(self, event):
        self.is_hovered = True
        theme = self.controller.current_theme if (self.controller and hasattr(self.controller, 'current_theme')) else Themes.THEME_DEFAULT
        self.color_anim.stop()
        self.color_anim.setStartValue(self.handle_color)
        self.color_anim.setEndValue(QColor(f"{theme.scroll_handle_hover}"))
        self.color_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.is_hovered = False
        theme = self.controller.current_theme if (self.controller and hasattr(self.controller, 'current_theme')) else Themes.THEME_DEFAULT
        self.color_anim.stop()
        self.color_anim.setStartValue(self.handle_color)
        self.color_anim.setEndValue(QColor(f"{theme.scroll_handle}"))
        self.color_anim.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        
        theme = self.controller.current_theme if (self.controller and hasattr(self.controller, 'current_theme')) else Themes.THEME_DEFAULT
        
        # Draw Custom Rounded Track with active theme colours
        track_rect = self.rect()
        painter.setPen(QPen(QColor(f"{theme.scroll_border}"), 2))
        painter.setBrush(QColor(f"{theme.scroll_track}"))
        
        if self.orientation() == Qt.Orientation.Vertical:
            draw_rect = track_rect.adjusted(1, 10, -1, -10)
            painter.drawRoundedRect(draw_rect, 7, 7)
        else:
            draw_rect = track_rect.adjusted(10, 1, -10, -1)
            painter.drawRoundedRect(draw_rect, 7, 7)
        
        # Draw Custom Rounded Handle
        handle_rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ScrollBar, opt, QStyle.SubControl.SC_ScrollBarSlider, self
        )
        if handle_rect.isValid() and not handle_rect.isEmpty():
            painter.setPen(QPen(QColor(f"{theme.scroll_border}"), 2))
            painter.setBrush(self.handle_color)
            
            if self.orientation() == Qt.Orientation.Vertical:
                h_rect = handle_rect.adjusted(2, 2, -2, -2)
                painter.drawRoundedRect(h_rect, 5, 5)
            else:
                h_rect = handle_rect.adjusted(2, 2, -2, -2)
                painter.drawRoundedRect(h_rect, 5, 5)