import sys
import keyboard
import pyautogui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from overlay import OverlayWindow
from input_mapper import InputMapper

class MouseYoke:
    def __init__(self):
        self.active = False
        self.locked = False  # 新增锁定状态
        self.locked_joystick_pos = None  # 锁定的摇杆位置
        self.last_mouse_pos = (0, 0)
        self.app = QApplication(sys.argv)
        self.overlay = OverlayWindow()

        # 获取真实屏幕尺寸
        self.screen_width = self.overlay.width()
        self.screen_height = self.overlay.height()
        print(f"检测到屏幕尺寸: {self.screen_width} x {self.screen_height}")

        # 将屏幕尺寸传递给input_mapper
        self.input_mapper = InputMapper(self.screen_width, self.screen_height)

        # If input mapper failed to init, don't bother setting up the rest
        if not self.input_mapper.device:
            return

        # 注册热键
        keyboard.add_hotkey('f1', self.toggle_active)
        keyboard.add_hotkey('esc', self.exit_yoke_mode)

        # 设置定时器来持续更新摇杆状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_yoke)
        self.timer.start(16)  # ~60 FPS

    def toggle_active(self):
        """切换激活状态：未激活 -> 激活 ↔ 锁定"""
        if not self.input_mapper.device:
            return

        if not self.active and not self.locked:
            # 状态1: 未激活 -> 激活模式
            self.last_mouse_pos = pyautogui.position()
            # 如果有锁定位置，从锁定位置开始，否则从屏幕中心开始
            if self.locked_joystick_pos:
                pyautogui.moveTo(self.locked_joystick_pos[0], self.locked_joystick_pos[1])
            else:
                pyautogui.moveTo(self.overlay.center_x, self.overlay.center_y)
            self.active = True
            self.overlay.show_active()
            print("进入激活模式")

        elif self.active and not self.locked:
            # 状态2: 激活 -> 锁定模式
            current_pos = pyautogui.position()
            self.locked_joystick_pos = current_pos  # 保存当前摇杆位置
            self.overlay.show_locked(current_pos[0], current_pos[1])
            # 不移动鼠标，让鼠标保持在当前位置
            self.active = False
            self.locked = True
            # 保持摇杆在当前位置，不重置
            self.input_mapper.map_position(current_pos[0], current_pos[1])
            print(f"锁定摇杆位置: ({current_pos[0]}, {current_pos[1]})，鼠标保持当前位置")

        elif not self.active and self.locked:
            # 状态3: 锁定 -> 激活模式 (从锁定位置重新开始)
            if self.locked_joystick_pos:
                # 不需要保存当前鼠标位置，因为我们要移动到锁定位置
                pyautogui.moveTo(self.locked_joystick_pos[0], self.locked_joystick_pos[1])  # 跳到锁定位置
                self.active = True
                self.locked = False
                self.overlay.show_active()  # 清除锁定十字架，只显示中心十字架
                print(f"从锁定位置重新激活: ({self.locked_joystick_pos[0]}, {self.locked_joystick_pos[1]})，鼠标移动到锁定位置")

    def exit_yoke_mode(self):
        """完全退出摇杆模式，重置所有状态"""
        if self.active or self.locked:
            if self.active:
                # 如果当前是激活状态，恢复鼠标位置
                pyautogui.moveTo(self.last_mouse_pos[0], self.last_mouse_pos[1])
            self.active = False
            self.locked = False
            self.locked_joystick_pos = None
            self.overlay.show_active()  # 清除所有十字架，只显示中心十字架
            self.input_mapper.reset()  # 重置摇杆到中心位置
            print("完全退出摇杆模式")

    def update_yoke(self):
        """如果激活，则根据鼠标位置更新摇杆；如果锁定，则保持摇杆在锁定位置"""
        if self.active and not self.locked:
            # 激活状态：鼠标控制摇杆
            pos = pyautogui.position()
            self.input_mapper.map_position(pos[0], pos[1])
        elif self.locked and self.locked_joystick_pos:
            # 锁定状态：摇杆保持在锁定位置
            self.input_mapper.map_position(self.locked_joystick_pos[0], self.locked_joystick_pos[1])

    def run(self):
        """运行主循环"""
        # 如果vJoy设备未初始化，input_mapper会打印详细错误，这里只做最后检查
        if not self.input_mapper.device:
            # The app will exit gracefully as the Qt loop won't start
            return

        self.overlay.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    yoke = MouseYoke()
    yoke.run()
