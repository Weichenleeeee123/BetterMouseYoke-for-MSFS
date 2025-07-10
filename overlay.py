from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from config import Config
import math

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        
        self.center_x = screen.width() // 2
        self.center_y = screen.height() // 2
        self.locked_x = None
        self.locked_y = None
        self.rudder_line_visible = False
        self.rudder_activation_pos = None
        
    def paintEvent(self, a0):
        painter = QtGui.QPainter(self)
        
        # 绘制白色中心十字架
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255), 2)
        painter.setPen(pen)
        
        painter.drawLine(
            self.center_x - Config.CENTER_CROSS_SIZE, self.center_y,
            self.center_x + Config.CENTER_CROSS_SIZE, self.center_y
        )
        painter.drawLine(
            self.center_x, self.center_y - Config.CENTER_CROSS_SIZE,
            self.center_x, self.center_y + Config.CENTER_CROSS_SIZE
        )
        
        # 绘制锁定十字架
        if self.locked_x and self.locked_y:
            offset_x = self.locked_x - self.center_x
            offset_y = self.locked_y - self.center_y
            distance = math.sqrt(offset_x**2 + offset_y**2)
            center_dead_zone = int(min(self.width(), self.height()) * Config.CENTER_DEAD_ZONE_FACTOR)
            
            if distance >= center_dead_zone:
                pen = QtGui.QPen(QtGui.QColor(255, 255, 0), 2)
                painter.setPen(pen)
                
                painter.drawLine(
                    self.locked_x - Config.LOCKED_CROSS_SIZE, self.locked_y,
                    self.locked_x + Config.LOCKED_CROSS_SIZE, self.locked_y
                )
                painter.drawLine(
                    self.locked_x, self.locked_y - Config.LOCKED_CROSS_SIZE,
                    self.locked_x, self.locked_y + Config.LOCKED_CROSS_SIZE
                )

        # 绘制滑行轴线
        if self.rudder_line_visible:
            pen = QtGui.QPen(QtGui.QColor(0, 255, 255), 2, Qt.DashLine)
            painter.setPen(pen)
            half_width = Config.RUDDER_AXIS_WIDTH // 2
            start_x = self.rudder_activation_pos[0] - half_width
            end_x = self.rudder_activation_pos[0] + half_width
            y = self.rudder_activation_pos[1]

            # 绘制水平线
            painter.drawLine(start_x, y, end_x, y)

            # 绘制两端箭头
            arrow_size = 5
            painter.drawLine(start_x, y, start_x + arrow_size, y - arrow_size)
            painter.drawLine(start_x, y, start_x + arrow_size, y + arrow_size)
            painter.drawLine(end_x, y, end_x - arrow_size, y - arrow_size)
            painter.drawLine(end_x, y, end_x - arrow_size, y + arrow_size)

    def show_active(self):
        self.locked_x = None
        self.locked_y = None
        self.update()
        
    def show_locked(self, x, y):
        self.locked_x = x
        self.locked_y = y
        self.update()

    def show_rudder_line(self, visible, pos=None):
        """控制滑行轴线的显示和位置"""
        self.rudder_line_visible = visible
        self.rudder_activation_pos = pos
        self.update()