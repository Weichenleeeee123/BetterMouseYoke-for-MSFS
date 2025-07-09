class Config:
    # 热键设置
    HOTKEY = 'f1'
    
    # 十字架样式
    CENTER_CROSS_SIZE = 20
    LOCKED_CROSS_SIZE = 15
    
    # 输入映射参数 (整个屏幕作为操作范围)
    # 死区参数说明:
    # DEAD_ZONE_FACTOR - 防止微小抖动的常规死区(线性死区)
    # CENTER_DEAD_ZONE_FACTOR - 中心回中区域(圆形死区)
    DEAD_ZONE_FACTOR = 0.001  # 常规死区(更灵敏)
    CENTER_DEAD_ZONE_FACTOR = 0.01  # 中心死区(稍缩小)
    
    # 屏幕尺寸 (由overlay模块初始化)
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080