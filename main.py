import sys
import keyboard
import pyautogui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from pynput import mouse
from overlay import OverlayWindow
from input_mapper import InputMapper

class MouseYoke:
    def __init__(self):
        self.active = False
        self.locked = False
        self.rudder_mode = False  # 新增方向舵模式
        self.locked_joystick_pos = None
        self.rudder_activation_pos = None  # 按下左键激活方向舵模式时的鼠标位置
        self.last_mouse_pos = (0, 0)
        self.smoothing_factor = 0.3  # 鼠标平滑移动因子 (0.1到1.0之间)
        self.app = QApplication(sys.argv)
        self.overlay = OverlayWindow()

        self.screen_width = self.overlay.width()
        self.screen_height = self.overlay.height()
        print(f"检测到屏幕尺寸: {self.screen_width} x {self.screen_height}")

        self.input_mapper = InputMapper(self.screen_width, self.screen_height)

        if not self.input_mapper.device:
            return

        keyboard.add_hotkey('ctrl+f', self.toggle_active)
        keyboard.add_hotkey('esc', self.exit_yoke_mode)

        # 设置鼠标监听器
        self.mouse_listener = mouse.Listener(
            on_click=self.on_click
        )
        self.mouse_listener.start()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_yoke)
        self.timer.start(16)

    def on_click(self, x, y, button, pressed):
        """处理鼠标点击事件"""
        if not self.active or self.locked:
            return

        if button == mouse.Button.left:
            if pressed:
                # 进入方向舵模式
                self.rudder_activation_pos = (x, y)
                self.rudder_mode = True
                self.overlay.show_rudder_line(True, self.rudder_activation_pos)
                print(f"进入方向舵模式，激活位置: ({x}, {y})")
            else:
                # 退出方向舵模式
                self.rudder_mode = False
                self.rudder_activation_pos = None
                self.overlay.show_rudder_line(False)
                # 恢复鼠标到激活方向舵前的Y坐标，X坐标保持当前，避免跳跃
                current_x, _ = pyautogui.position()
                pyautogui.moveTo(current_x, y)
                # 重置方向舵到中心位置
                self.input_mapper.reset_z()
                print("退出方向舵模式并重置方向舵")

    def toggle_active(self):
        """切换激活状态：未激活 -> 激活 ↔ 锁定"""
        if not self.input_mapper.device:
            return

        if not self.active and not self.locked:
            self.last_mouse_pos = pyautogui.position()
            if self.locked_joystick_pos:
                pyautogui.moveTo(self.locked_joystick_pos[0], self.locked_joystick_pos[1])
            else:
                pyautogui.moveTo(self.overlay.center_x, self.overlay.center_y)
            self.active = True
            self.overlay.show_active()
            print("进入激活模式")

        elif self.active and not self.locked:
            current_pos = pyautogui.position()
            self.locked_joystick_pos = current_pos
            self.overlay.show_locked(current_pos[0], current_pos[1])
            self.active = False
            self.locked = True
            self.input_mapper.map_position(current_pos[0], current_pos[1])
            print(f"锁定摇杆位置: ({current_pos[0]}, {current_pos[1]})")

        elif not self.active and self.locked:
            if self.locked_joystick_pos:
                pyautogui.moveTo(self.locked_joystick_pos[0], self.locked_joystick_pos[1])
                self.active = True
                self.locked = False
                self.overlay.show_active()
                print(f"从锁定位置重新激活: ({self.locked_joystick_pos[0]}, {self.locked_joystick_pos[1]})")

    def exit_yoke_mode(self):
        """完全退出摇杆模式，重置所有状态"""
        if self.active or self.locked:
            if self.active:
                pyautogui.moveTo(self.last_mouse_pos[0], self.last_mouse_pos[1])
            self.active = False
            self.locked = False
            self.rudder_mode = False # 退出时重置方向舵模式
            self.locked_joystick_pos = None
            self.overlay.show_active()
            self.overlay.show_rudder_line(False) # 隐藏方向舵线
            self.input_mapper.reset()
            print("完全退出摇杆模式")

    def update_yoke(self):
        """根据模式更新摇杆"""
        rudder_activation_pos = self.rudder_activation_pos
        if self.rudder_mode and rudder_activation_pos:
            # 方向舵模式
            current_pos = pyautogui.position()
            target_y = rudder_activation_pos[1]

            # 平滑地将鼠标Y坐标移向目标Y坐标
            new_y = int(current_pos[1] * (1 - self.smoothing_factor) + target_y * self.smoothing_factor)
            
            # 只有在鼠标位置发生变化时才移动，避免不必要的pyautogui调用
            if new_y != current_pos[1]:
                pyautogui.moveTo(current_pos[0], new_y)

            self.input_mapper.map_rudder_position(current_pos[0], rudder_activation_pos[0], rudder_activation_pos[1])
        elif self.active and not self.locked:
            # 激活状态：鼠标控制摇杆
            pos = pyautogui.position()
            self.input_mapper.map_position(pos[0], pos[1])
        elif self.locked and self.locked_joystick_pos:
            # 锁定状态：摇杆保持在锁定位置
            self.input_mapper.map_position(self.locked_joystick_pos[0], self.locked_joystick_pos[1])

    def run(self):
        """运行主循环"""
        if not self.input_mapper.device:
            return

        self.overlay.show()
        self.app.exec_()
        # 停止监听器
        self.mouse_listener.stop()


if __name__ == "__main__":
    yoke = MouseYoke()
    yoke.run()
