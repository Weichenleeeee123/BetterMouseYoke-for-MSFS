import math
import pyvjoy
from config import Config

class InputMapper:
    def __init__(self, screen_width=None, screen_height=None):
        self.device = None
        self.vjoy_id = None

        # 使用传入的屏幕尺寸，如果没有传入则使用Config中的默认值
        self.screen_width = screen_width if screen_width is not None else Config.SCREEN_WIDTH
        self.screen_height = screen_height if screen_height is not None else Config.SCREEN_HEIGHT

        # 使用整个屏幕作为操作范围
        # 最大偏移量设置为从屏幕中心到边缘的距离
        self.max_offset_x = self.screen_width // 2   # 水平方向最大偏移
        self.max_offset_y = self.screen_height // 2  # 垂直方向最大偏移

        # 死区设置为屏幕尺寸的一个很小比例
        min_dimension = min(self.screen_width, self.screen_height)
        self.dead_zone = int(min_dimension * Config.DEAD_ZONE_FACTOR)

        print(f"输入映射设置: 水平最大偏移={self.max_offset_x}px, 垂直最大偏移={self.max_offset_y}px, 死区={self.dead_zone}px")

        # 尝试初始化vJoy设备 (从1到16)
        for i in range(1, 17):
            try:
                self.device = pyvjoy.VJoyDevice(i)
                self.vjoy_id = i
                print(f"成功连接到 vJoy 设备 #{self.vjoy_id}")
                self.reset()
                return  # 成功找到并初始化设备，退出函数
            except pyvjoy.exceptions.vJoyException:
                # 捕获特定vJoy异常，继续尝试下一个
                continue
        
        # 如果循环结束都没有找到设备
        if not self.device:
            print("="*50)
            print("vJoy 初始化失败: 未能找到任何可用的vJoy设备。")
            print("请检查:")
            print("  1. 是否已正确安装vJoy驱动？")
            print("  2. 是否在vJoy配置工具(vJoyConf.exe)中至少启用了一个设备？")
            print("  3. 设备是否被其他程序独占？ (建议重启电脑)")
            print("="*50)

    def map_position(self, x, y):
        """将鼠标位置映射为摇杆输入"""
        if not self.device:
            return

        # 计算相对中心点的偏移量
        offset_x = x - self.screen_width // 2
        offset_y = y - self.screen_height // 2
        
        # 计算中心死区半径
        center_dead_zone = int(min(self.screen_width, self.screen_height) * Config.CENTER_DEAD_ZONE_FACTOR)
        print(f"中心死区半径: {center_dead_zone}px, 当前距离: {math.sqrt(offset_x**2 + offset_y**2):.1f}px")
        
        # 检查是否在中心死区内
        distance = math.sqrt(offset_x**2 + offset_y**2)
        if distance < center_dead_zone:
            print("进入中心死区 - 摇杆回中")
            self.reset()  # 在中心死区内，直接回中
            return
            
        # 应用常规死区
        if abs(offset_x) < self.dead_zone:
            offset_x = 0
        if abs(offset_y) < self.dead_zone:
            offset_y = 0
            
        # 将偏移量限制在各自的最大值内
        offset_x = max(-self.max_offset_x, min(self.max_offset_x, offset_x))
        offset_y = max(-self.max_offset_y, min(self.max_offset_y, offset_y))

        # 计算摇杆值 (0-32767)，分别使用X和Y的最大偏移量进行归一化
        joy_x = int((offset_x / self.max_offset_x) * 16383 + 16384)
        joy_y = int((offset_y / self.max_offset_y) * 16383 + 16384)
        
        try:
            self.device.set_axis(pyvjoy.HID_USAGE_X, joy_x)
            self.device.set_axis(pyvjoy.HID_USAGE_Y, joy_y)
        except Exception as e:
            print(f"设置摇杆轴失败: {e}")
        
    def reset(self):
        """重置摇杆位置"""
        if self.device:
            self.device.set_axis(pyvjoy.HID_USAGE_X, 16384)
            self.device.set_axis(pyvjoy.HID_USAGE_Y, 16384)
        
    def __del__(self):
        """释放设备"""
        self.reset()
