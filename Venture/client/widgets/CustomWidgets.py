from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QEvent

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