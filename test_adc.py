# ===== ADC 摇杆校准测试 =====
# 在 Waffle Nano 上单独运行此脚本，观察串口输出
from machine import Pin, ADC
import utime

pinA = Pin(14, Pin.IN)
pinB = Pin(0, Pin.IN)
pinC = Pin(1, Pin.IN)
pinD = Pin(2, Pin.IN)
adcX = ADC(Pin(12))
adcY = ADC(Pin(13))

print("=== ADC 摇杆校准测试 ===")
print("请按以下步骤操作：")
print("1. 不碰摇杆，观察空闲值")
print("2. 推摇杆上/下/左/右到底，记录范围")
print("3. 按 A/B/C/D 按钮，观察 GPIO 值")
print("=" * 40)

while True:
    x = adcX.read()
    y = adcY.read()
    a = pinA.value()
    b = pinB.value()
    c = pinC.value()
    d = pinD.value()

    msg = "X=%5d  Y=%5d  |  A=%d B=%d C=%d D=%d" % (x, y, a, b, c, d)

    # 标记方向
    dirs = []
    if x < 10000: dirs.append("LEFT")
    elif x > 50000: dirs.append("RIGHT")
    if y < 10000: dirs.append("UP")
    elif y > 50000: dirs.append("DOWN")
    if a == 0: dirs.append("[A]")
    if b == 0: dirs.append("[B]")
    if c == 0: dirs.append("[C]")
    if d == 0: dirs.append("[D]")

    if dirs:
        msg += "  --> " + " ".join(dirs)

    print(msg)
    utime.sleep(0.3)
