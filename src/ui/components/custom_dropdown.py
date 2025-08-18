from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PySide6.QtCore import Qt, Signal, QRect, QPropertyAnimation, QEasingCurve, QEvent
from PySide6.QtGui import (
    QPainter,
    QPen,
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QPainterPath,
)
from typing import List, Optional


class DropdownList(QWidget):
    """Custom dropdown list widget that appears below the main button"""

    ITEM_HEIGHT = 28  # Height of each dropdown item - more compact like Aqua Voice

    item_selected = Signal(int)  # Emits the index of selected item

    def __init__(self, items: List[str], parent=None, button_width: int = 200):
        super().__init__(parent)
        self.items = items
        self.hovered_index = -1
        self.selected_index = 0
        self.button_width = button_width

        # Configure widget
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Install global event filter to detect clicks outside
        QApplication.instance().installEventFilter(self)

        # Calculate size
        self.update_size()

    def update_size(self):
        """Calculate and set the widget size based on content"""
        if not self.items:
            return

        # Use exact button width to match perfectly
        width = self.button_width
        height = (
            len(self.items) * self.ITEM_HEIGHT + 12
        )  # Height per item + 6px top/bottom padding

        self.setFixedSize(width, height)

    def paintEvent(self, event):
        """Custom paint the dropdown list"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw background with shadow effect
        rect = self.rect().adjusted(2, 2, -2, -2)  # Leave space for shadow

        # Draw shadow (multiple layers for more realistic effect)
        for i in range(3):
            shadow_rect = rect.adjusted(i + 1, i + 1, i + 1, i + 1)
            shadow_path = QPainterPath()
            shadow_path.addRoundedRect(shadow_rect, 6, 6)
            alpha = 20 - (i * 5)  # Decreasing alpha for layers
            painter.fillPath(shadow_path, QColor(0, 0, 0, alpha))

        # Draw main background
        bg_path = QPainterPath()
        bg_path.addRoundedRect(rect, 6, 6)
        painter.fillPath(bg_path, QColor(255, 255, 255))

        # Draw border
        painter.setPen(QPen(QColor(200, 200, 200), 0.5))
        painter.drawPath(bg_path)

        # Draw items
        item_height = self.ITEM_HEIGHT
        start_y = rect.top() + 6

        for i, item in enumerate(self.items):
            item_rect = QRect(
                rect.left() + 12,
                start_y + i * item_height,
                rect.width() - 50,
                item_height,
            )

            # Draw item background if hovered or selected
            if i == self.hovered_index:
                hover_rect = QRect(
                    rect.left() + 6,
                    start_y + i * item_height + 2,
                    rect.width() - 12,
                    item_height - 4,
                )
                hover_path = QPainterPath()
                hover_path.addRoundedRect(hover_rect, 4, 4)
                painter.fillPath(hover_path, QColor(245, 245, 245))

            # Draw text - ALWAYS use dark color for visibility
            painter.setPen(QColor(40, 40, 40))  # Dark gray for ALL text
            if i == self.selected_index:
                font = QFont()
                font.setPointSize(14)
                font.setBold(True)
                painter.setFont(font)
            else:
                font = QFont()
                font.setPointSize(14)
                font.setBold(False)
                painter.setFont(font)

            painter.drawText(
                item_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                item,
            )

            # Draw checkmark for selected item
            if i == self.selected_index:
                check_rect = QRect(
                    rect.right() - 26, start_y + i * item_height + 12, 16, 16
                )
                painter.setPen(QPen(QColor(0, 122, 255), 2))
                # Draw checkmark
                painter.drawLine(
                    check_rect.left() + 2,
                    check_rect.center().y(),
                    check_rect.center().x() - 1,
                    check_rect.bottom() - 4,
                )
                painter.drawLine(
                    check_rect.center().x() - 1,
                    check_rect.bottom() - 4,
                    check_rect.right() - 2,
                    check_rect.top() + 4,
                )

        # Proper painter cleanup
        painter.end()

    def mouseMoveEvent(self, event):
        """Handle mouse movement for hover effects"""
        rect = self.rect().adjusted(2, 2, -2, -2)
        item_height = self.ITEM_HEIGHT
        start_y = rect.top() + 6

        y_pos = event.pos().y()
        if start_y <= y_pos <= rect.bottom() - 6:
            self.hovered_index = (y_pos - start_y) // item_height
            if self.hovered_index >= len(self.items):
                self.hovered_index = -1
        else:
            self.hovered_index = -1

        self.update()

    def mousePressEvent(self, event):
        """Handle mouse clicks"""
        if event.button() == Qt.MouseButton.LeftButton:
            rect = self.rect().adjusted(2, 2, -2, -2)
            item_height = self.ITEM_HEIGHT
            start_y = rect.top() + 6

            y_pos = event.pos().y()
            if start_y <= y_pos <= rect.bottom() - 6:
                clicked_index = (y_pos - start_y) // item_height
                if 0 <= clicked_index < len(self.items):
                    self.selected_index = clicked_index
                    self.item_selected.emit(clicked_index)
                    self.close()

    def keyPressEvent(self, event):
        """Handle keyboard navigation"""
        if event.key() == Qt.Key.Key_Up:
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update()
        elif event.key() == Qt.Key.Key_Down:
            if self.selected_index < len(self.items) - 1:
                self.selected_index += 1
                self.update()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.item_selected.emit(self.selected_index)
            self.close()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        """Handle losing focus - close dropdown without changing selection"""
        self.close()
        super().focusOutEvent(event)

    def eventFilter(self, obj, event):
        """Global event filter to detect clicks outside dropdown"""
        if event.type() == QEvent.Type.MouseButtonPress:
            # Get the global position of the mouse click
            global_pos = event.globalPos()
            # Check if the click is outside our dropdown bounds
            dropdown_rect = QRect(self.pos(), self.size())
            if not dropdown_rect.contains(global_pos):
                self.close()
                return False
        return super().eventFilter(obj, event)

    def closeEvent(self, event):
        """Clean up event filter when closing"""
        QApplication.instance().removeEventFilter(self)
        super().closeEvent(event)


class CustomDropdown(QWidget):
    """Custom dropdown widget with full control over appearance and behavior"""

    current_text_changed = Signal(str)  # Emits when selection changes
    current_index_changed = Signal(int)  # Emits when index changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []
        self.current_index = 0
        self.dropdown_list = None
        self.is_hovered = False
        self.is_pressed = False

        # Configure widget
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumHeight(32)
        self.setMaximumHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def add_item(self, text: str, data=None):
        """Add an item to the dropdown"""
        self.items.append({"text": text, "data": data})
        self.update()

    def add_items(self, items: List[str]):
        """Add multiple items to the dropdown"""
        for item in items:
            self.add_item(item)

    def clear(self):
        """Clear all items"""
        self.items.clear()
        self.current_index = 0
        self.update()

    def set_current_index(self, index: int):
        """Set the current selected index"""
        if 0 <= index < len(self.items):
            self.current_index = index
            self.update()

    def set_current_text(self, text: str):
        """Set the current selected item by text"""
        for i, item in enumerate(self.items):
            if item["text"] == text:
                self.set_current_index(i)
                break

    def current_text(self) -> str:
        """Get the current selected text"""
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index]["text"]
        return ""

    def current_data(self):
        """Get the current selected data"""
        if 0 <= self.current_index < len(self.items):
            return self.items[self.current_index]["data"]
        return None

    def paintEvent(self, event):
        """Custom paint the dropdown button"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Define colors based on state
        if self.is_pressed:
            bg_color = QColor(255, 255, 255)
            # border_color = QColor(0, 122, 255)
            border_color = QColor(192, 192, 192)
        elif self.is_hovered:
            bg_color = QColor(255, 255, 255)
            border_color = QColor(192, 192, 192)
        elif self.hasFocus():
            bg_color = QColor(255, 255, 255)
            # border_color = QColor(0, 122, 255)
            border_color = QColor(192, 192, 192)
        else:
            bg_color = QColor(255, 255, 255)
            border_color = QColor(224, 224, 224)  # default

        # Draw background
        rect = self.rect().adjusted(1, 1, -1, -1)
        bg_path = QPainterPath()
        bg_path.addRoundedRect(rect, 6, 6)
        painter.fillPath(bg_path, bg_color)

        # Draw border
        painter.setPen(QPen(border_color, 1))
        painter.drawPath(bg_path)

        # Draw focus ring if focused
        """if self.hasFocus():
            focus_rect = self.rect().adjusted(-2, -2, 2, 2)
            focus_path = QPainterPath()
            focus_path.addRoundedRect(focus_rect, 10, 10)
            painter.setPen(QPen(QColor(0, 122, 255, 50), 4))
            painter.drawPath(focus_path)"""

        # Draw text
        if self.items and 0 <= self.current_index < len(self.items):
            text = self.items[self.current_index]["text"]
            font = QFont()
            font.setPointSize(14)
            font.setBold(False)
            painter.setFont(font)
            painter.setPen(QColor(51, 51, 51))

            text_rect = rect.adjusted(16, 0, -40, 0)  # Leave space for arrow
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                text,
            )

        # Draw dropdown arrow
        arrow_rect = QRect(rect.right() - 30, rect.center().y() - 3, 8, 6)
        painter.setPen(QPen(QColor(153, 153, 153), 2))
        painter.setBrush(QBrush(QColor(153, 153, 153)))

        # Draw triangle arrow
        arrow_points = [
            arrow_rect.topLeft(),
            arrow_rect.topRight(),
            arrow_rect.bottomLeft() + arrow_rect.bottomRight(),
        ]
        # Simple triangle path
        painter.drawLine(
            arrow_rect.left(),
            arrow_rect.top(),
            arrow_rect.center().x(),
            arrow_rect.bottom(),
        )
        painter.drawLine(
            arrow_rect.center().x(),
            arrow_rect.bottom(),
            arrow_rect.right(),
            arrow_rect.top(),
        )

        # Proper painter cleanup
        painter.end()

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressed = True
            self.setFocus()
            self.update()
            self.show_dropdown()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.is_pressed = False
        self.update()

    def enterEvent(self, event):
        """Handle mouse enter"""
        self.is_hovered = True
        self.update()

    def leaveEvent(self, event):
        """Handle mouse leave"""
        self.is_hovered = False
        self.update()

    def keyPressEvent(self, event):
        """Handle keyboard events"""
        if event.key() == Qt.Key.Key_Space or event.key() == Qt.Key.Key_Return:
            self.show_dropdown()
        elif event.key() == Qt.Key.Key_Up:
            if self.current_index > 0:
                self.set_current_index(self.current_index - 1)
                self._emit_change_signals()
        elif event.key() == Qt.Key.Key_Down:
            if self.current_index < len(self.items) - 1:
                self.set_current_index(self.current_index + 1)
                self._emit_change_signals()
        else:
            super().keyPressEvent(event)

    def show_dropdown(self):
        """Show the dropdown list"""
        if not self.items:
            return

        if self.dropdown_list:
            self.dropdown_list.close()

        # Create dropdown list with exact button width
        item_texts = [item["text"] for item in self.items]
        button_width = self.width()
        self.dropdown_list = DropdownList(item_texts, self, button_width)
        self.dropdown_list.selected_index = self.current_index
        self.dropdown_list.item_selected.connect(self._on_item_selected)

        # Position dropdown directly below this widget like Aqua Voice
        button_bottom = self.mapToGlobal(self.rect().bottomLeft())
        dropdown_x = button_bottom.x()
        dropdown_y = button_bottom.y() + 25  # px gap for clean separation

        self.dropdown_list.move(dropdown_x, dropdown_y)

        # Show dropdown
        self.dropdown_list.show()
        self.dropdown_list.setFocus()

    def _on_item_selected(self, index: int):
        """Handle item selection from dropdown"""
        if 0 <= index < len(self.items):
            self.current_index = index
            self.update()
            self._emit_change_signals()

    def _emit_change_signals(self):
        """Emit change signals"""
        self.current_index_changed.emit(self.current_index)
        self.current_text_changed.emit(self.current_text())
