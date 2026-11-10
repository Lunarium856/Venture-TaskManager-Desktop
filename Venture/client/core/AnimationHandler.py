import SettingsHandler, Themes, DummyList
from ProjectClasses import Project, Task, Subtask, Tag
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import sys, json, os, time, datetime, re, sqlite3

class Animator(QObject):
    @staticmethod
    def getStyleRule(target: QObject, rule: str):
        targetStyles = target.styleSheet()
        if not targetStyles: return None
        pattern = re.compile(rf"\b{re.escape(rule)}\s*:\s*([^;]+);")
        style_match = pattern.search(targetStyles)
        if style_match: return style_match.group(1).strip()
        return None

    def createAnimation(self, target: QObject, type: str, start_val, end_val, duration: int = 200, easing: QEasingCurve.Type = QEasingCurve.Type.InOutQuad):
        """ Helper Function that creates & returns an individual animation """
        if type == "opacity":
            effect = target.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(target)
                target.setGraphicsEffect(effect)
            anim = QVariantAnimation(self)
            anim.setStartValue(float(start_val))
            anim.setEndValue(float(end_val))
            anim.setDuration(duration)
            anim.setEasingCurve(easing)
            anim.valueChanged.connect(effect.setOpacity)
            return anim

        if type == "geometry":
            anim = QPropertyAnimation(target, b"geometry", self)
            anim.setStartValue(start_val)
            anim.setEndValue(end_val)
            anim.setDuration(duration)
            anim.setEasingCurve(easing)
            return anim

        anim = QVariantAnimation(self)
        if isinstance(start_val, (str, QColor)):
            anim.setStartValue(QColor(start_val))
            anim.setEndValue(QColor(end_val))
        else:
            anim.setStartValue(start_val)
            anim.setEndValue(end_val)

        anim.setDuration(duration)
        anim.setEasingCurve(easing)

        original_stylesheet = target.styleSheet() or ""

        if type == "text":
            rule_name = "color"
            def update_style(val):
                try:
                    col_str = val.name() if isinstance(val, QColor) else str(val)
                    curr_ss = target.styleSheet() or original_stylesheet
                    if re.search(rf"\b{rule_name}\s*:", curr_ss):
                        new_ss = re.sub(rf"\b{rule_name}\s*:[^;]+;", f"{rule_name}: {col_str};", curr_ss)
                    else:
                        new_ss = curr_ss.rstrip(";") + f"; {rule_name}: {col_str};"
                    target.setStyleSheet(new_ss)
                except RuntimeError:
                    return
            anim.valueChanged.connect(update_style)

        elif type == "border":
            rule_name = "border"
            existing_border = self.getStyleRule(target, "border") or "3px solid black"
            b_match = re.search(r"(\d+px\s+\w+)", existing_border)
            b_width_style = b_match.group(1) if b_match else "3px solid"

            def update_border(val):
                try:
                    col_str = val.name() if isinstance(val, QColor) else str(val)
                    new_border_val = f"{b_width_style} {col_str}"
                    curr_ss = target.styleSheet() or original_stylesheet
                    if re.search(rf"\b{rule_name}\s*:", curr_ss):
                        new_ss = re.sub(rf"\b{rule_name}\s*:[^;]+;", f"{rule_name}: {new_border_val};", curr_ss)
                    else:
                        new_ss = curr_ss.rstrip(";") + f"; {rule_name}: {new_border_val};"
                    target.setStyleSheet(new_ss)
                except RuntimeError:
                    return
            anim.valueChanged.connect(update_border)

        elif type == "background":
            rule_name = "background"
            def update_bg(val):
                try:
                    if isinstance(val, QColor):
                        bg_str = f"rgba({val.red()}, {val.green()}, {val.blue()}, {val.alpha()})"
                    else:
                        bg_str = str(val)
                    curr_ss = target.styleSheet() or original_stylesheet
                    if re.search(rf"\b{rule_name}\s*:", curr_ss):
                        new_ss = re.sub(rf"\b{rule_name}\s*:[^;]+;", f"{rule_name}: {bg_str};", curr_ss)
                    else:
                        new_ss = curr_ss.rstrip(";") + f"; {rule_name}: {bg_str};"
                    target.setStyleSheet(new_ss)
                except RuntimeError:
                    return
            anim.valueChanged.connect(update_bg)

        elif type == "icon":
            if isinstance(target, QPushButton) and not target.icon().isNull():
                icon_size = target.iconSize()
                pixmaps = target.icon().availableSizes()
                size = pixmaps[0] if pixmaps else icon_size
                
                if not hasattr(target, '_original_pixmap'):
                    target._original_pixmap = target.icon().pixmap(size)
                    target._original_icon_size = size

                def update_btn_icon_color(color: QColor):
                    try:
                        if not hasattr(target, '_original_pixmap'):
                            return
                        temp_pixmap = target._original_pixmap
                        colored_pixmap = QPixmap(temp_pixmap.size())
                        colored_pixmap.fill(Qt.GlobalColor.transparent)
                        painter = QPainter(colored_pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                        painter.drawPixmap(0, 0, temp_pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                        painter.fillRect(colored_pixmap.rect(), color)
                        painter.end()
                        
                        target.setIcon(QIcon(colored_pixmap))
                    except RuntimeError:
                        return

                anim.valueChanged.connect(update_btn_icon_color)

            elif isinstance(target, QLabel) and target.pixmap():
                original_pixmap = target.pixmap() 
                
                if not hasattr(target, '_original_pixmap'):
                    target._original_pixmap = original_pixmap.copy()
                    target._original_icon_size = target.pixmap().size()

                def update_icon_color(color: QColor):
                    try:
                        if not hasattr(target, '_original_pixmap'):
                            return
                        temp_pixmap = target._original_pixmap
                        colored_pixmap = QPixmap(temp_pixmap.size())
                        colored_pixmap.fill(Qt.GlobalColor.transparent)
                        painter = QPainter(colored_pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                        painter.drawPixmap(0, 0, temp_pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
                        painter.fillRect(colored_pixmap.rect(), color)
                        painter.end()
                        
                        target.setPixmap(colored_pixmap)
                    except RuntimeError:
                        return

                anim.valueChanged.connect(update_icon_color)
        return anim

    def animateOnHover(self, target: QObject, types: list[str], start_values: list[any], end_values: list[any], duration: int = 200, easing: QEasingCurve.Type = QEasingCurve.Type.InOutQuad):
        if hasattr(target, '_anim_group') and target._anim_group.state() == QParallelAnimationGroup.State.Running:
            target._anim_group.stop()
        full_anim = QParallelAnimationGroup(self)
        for anim_type, start_val, end_val in zip(types, start_values, end_values):
            anim = self.createAnimation(target, anim_type, start_val, end_val, duration, easing)
            if anim:
                full_anim.addAnimation(anim)
        if full_anim.animationCount() > 0:
            target._anim_group = full_anim
            full_anim.start()
        return full_anim