from PyQt5.QtWidgets import QWidget, QApplication, QDesktopWidget
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from config import Config
import math

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 移除无法识别的属性，使用默认窗口设置
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 获取主屏幕尺寸
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(0, 0, screen.width(), screen.height())
        
        self.center_x = screen.width() // 2
        self.center_y = screen.height() // 2
        self.locked_x = None
        self.locked_y = None
        
    def paintEvent(self, a0):
        painter = QtGui.QPainter(self)
        
        # 绘制白色中心十字架
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255), 2)
        painter.setPen(pen)
        
        # 水平线
        painter.drawLine(
            self.center_x - Config.CENTER_CROSS_SIZE, self.center_y,
            self.center_x + Config.CENTER_CROSS_SIZE, self.center_y
        )
        # 垂直线
        painter.drawLine(
            self.center_x, self.center_y - Config.CENTER_CROSS_SIZE,
            self.center_x, self.center_y + Config.CENTER_CROSS_SIZE
        )
        
        # 如果有锁定位置且不在中心死区内，绘制黄色十字架
        if self.locked_x and self.locked_y:
            # 计算与中心距离
            offset_x = self.locked_x - self.center_x
            offset_y = self.locked_y - self.center_y
            distance = math.sqrt(offset_x**2 + offset_y**2)
            center_dead_zone = int(min(self.width(), self.height()) * Config.CENTER_DEAD_ZONE_FACTOR)
            
            if distance >= center_dead_zone:
                pen = QtGui.QPen(QtGui.QColor(255, 255, 0), 2)
                painter.setPen(pen)
                
                # 水平线
                painter.drawLine(
                    self.locked_x - Config.LOCKED_CROSS_SIZE, self.locked_y,
                    self.locked_x + Config.LOCKED_CROSS_SIZE, self.locked_y
                )
                # 垂直线
                painter.drawLine(
                    self.locked_x, self.locked_y - Config.LOCKED_CROSS_SIZE,
                    self.locked_x, self.locked_y + Config.LOCKED_CROSS_SIZE
                )
    
    def show_active(self):
        """显示激活状态"""
        self.locked_x = None
        self.locked_y = None
        self.update()
        
    def show_locked(self, x, y):
        """显示锁定状态"""
        self.locked_x = x
        self.locked_y = y
        self.update()