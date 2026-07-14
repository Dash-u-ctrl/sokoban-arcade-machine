from machine import SPI, Pin, ADC
import utime
import st7789

# Display
spi = SPI(0, baudrate=40000000, polarity=1, phase=0, bits=8, endia=0, sck=Pin(6), mosi=Pin(8))
display = st7789.ST7789(spi, 240, 240, reset=Pin(11, func=Pin.GPIO, dir=Pin.OUT), dc=Pin(7, func=Pin.GPIO, dir=Pin.OUT))
display.init()

# Buttons
pinA = Pin(14, Pin.IN)
pinB = Pin(0, Pin.IN)
pinC = Pin(1, Pin.IN)
pinD = Pin(2, Pin.IN)

# Joystick
adcX = ADC(Pin(12))
adcY = ADC(Pin(13))

# Colors
BLACK = st7789.color565(0, 0, 0)
WALL_COLOR = st7789.color565(255, 255, 255)
FLOOR_COLOR = st7789.color565(30, 30, 30)
PLAYER_COLOR = st7789.color565(200, 50, 50)
BOX_COLOR = st7789.color565(220, 160, 0)
TARGET_COLOR = st7789.color565(0, 200, 0)
BOX_OK_COLOR = st7789.color565(0, 255, 0)
TEXT_COLOR = st7789.color565(255, 255, 255)
TITLE_COLOR = st7789.color565(255, 215, 0)

# Map params
CELL = 24
GW = 10
GH = 10
OX = (240 - GW * CELL) // 2
OY = (240 - GH * CELL) // 2

# Tile types
E = 0   # Empty
W = 1   # Wall
B = 2   # Box
T = 3   # Target
P = 4   # Player
BT = 5  # Box on Target
PT = 6  # Player on Target

# Levels (all verified solvable)
levels = [
    [
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, E, E, E, E, E, E, W, W],
        [W, W, E, P, B, E, T, E, W, W],
        [W, W, E, E, E, E, E, E, W, W],
        [W, W, E, E, E, E, E, E, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
    ],
    [
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, T, W, W, W, W, W],
        [W, W, W, W, E, W, W, W, W, W],
        [W, W, W, W, B, B, E, T, W, W],
        [W, W, T, B, P, E, W, W, W, W],
        [W, W, W, W, W, B, W, W, W, W],
        [W, W, W, W, W, T, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
    ],
    [
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, T, E, E, E, W, W, W, W],
        [W, W, T, B, P, E, W, W, W, W],
        [W, W, E, B, E, E, W, W, W, W],
        [W, W, E, E, E, E, W, W, W, W],
        [W, W, E, E, E, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
    ],
    [
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, E, E, T, W, W, W],
        [W, W, W, P, B, E, T, W, W, W],
        [W, W, W, E, E, B, E, W, W, W],
        [W, W, W, W, E, E, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
    ],
    [
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, E, E, W, W, W, W],
        [W, W, W, W, P, E, W, W, W, W],
        [W, W, E, E, B, T, W, W, W, W],
        [W, W, E, E, B, T, W, W, W, W],
        [W, W, E, E, B, T, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
        [W, W, W, W, W, W, W, W, W, W],
    ],
]

cl = []
px = 3
py = 3
step = 0
total_steps = 0
level = 0
total_levels = len(levels)

def load_level(n):
    global cl, px, py, step
    cl = [row[:] for row in levels[n]]
    step = 0
    for y in range(GH):
        for x in range(GW):
            if cl[y][x] == P:
                px = x
                py = y
                return

def dm():
    display.fill(BLACK)
    for y in range(GH):
        for x in range(GW):
            xx = OX + x * CELL
            yy = OY + y * CELL
            t = cl[y][x]
            if t == W:
                display.fill_rect(xx, yy, CELL, CELL, WALL_COLOR)
            elif t == T:
                display.fill_rect(xx, yy, CELL, CELL, FLOOR_COLOR)
                cx = xx + CELL // 2
                cy = yy + CELL // 2
                r = CELL // 3
                display.fill_rect(cx - r, cy - 2, r * 2, 4, TARGET_COLOR)
                display.fill_rect(cx - 2, cy - r, 4, r * 2, TARGET_COLOR)
            elif t == B:
                display.fill_rect(xx, yy, CELL, CELL, FLOOR_COLOR)
                display.fill_rect(xx + 3, yy + 3, CELL - 6, CELL - 6, BOX_COLOR)
            elif t == BT:
                display.fill_rect(xx, yy, CELL, CELL, FLOOR_COLOR)
                display.fill_rect(xx + 3, yy + 3, CELL - 6, CELL - 6, BOX_OK_COLOR)
                cx = xx + CELL // 2
                cy = yy + CELL // 2
                display.fill_rect(cx - 2, cy - 2, 4, 4, TARGET_COLOR)
            elif t == P or t == PT:
                display.fill_rect(xx, yy, CELL, CELL, FLOOR_COLOR)
                display.fill_rect(xx + 4, yy + 4, CELL - 8, CELL - 8, PLAYER_COLOR)
                if t == PT:
                    cx = xx + CELL // 2
                    cy = yy + CELL // 2
                    r = CELL // 3
                    display.fill_rect(cx - r, cy - 2, r * 2, 4, TARGET_COLOR)
                    display.fill_rect(cx - 2, cy - r, 4, r * 2, TARGET_COLOR)
            else:
                display.fill_rect(xx, yy, CELL, CELL, FLOOR_COLOR)
    sy = OY + GH * CELL + 2
    if sy < 240:
        display.fill_rect(0, sy, 240, 240 - sy, BLACK)
    info = "Lv." + str(level + 1) + "  Step:" + str(step)
    display.fill_rect(0, 0, 240, 18, BLACK)
    display.draw_string(5, 0, info, size=2, color=TEXT_COLOR)

def ok():
    for r in cl:
        for t in r:
            if t == B:
                return False
    return True

def mv(dx, dy):
    global px, py, step
    nx = px + dx
    ny = py + dy
    if nx < 0 or nx >= GW or ny < 0 or ny >= GH:
        return
    tt = cl[ny][nx]
    if tt == W:
        return
    # Player current tile (E or T)
    on_target = (cl[py][px] == PT)
    if tt == E or tt == T:
        # Restore T if player was on target, else E
        cl[py][px] = T if on_target else E
        # Mark PT if new tile is target, else P
        cl[ny][nx] = PT if tt == T else P
        px = nx
        py = ny
        step = step + 1
    elif tt == B or tt == BT:
        bx = nx + dx
        by = ny + dy
        if bx < 0 or bx >= GW or by < 0 or by >= GH:
            return
        bt = cl[by][bx]
        # Box was on target?
        box_on_target = (tt == BT)
        if bt == E:
            cl[by][bx] = B
            cl[ny][nx] = PT if box_on_target else P
            cl[py][px] = T if on_target else E
            px = nx
            py = ny
            step = step + 1
        elif bt == T:
            cl[by][bx] = BT
            cl[ny][nx] = PT if box_on_target else P
            cl[py][px] = T if on_target else E
            px = nx
            py = ny
            step = step + 1
    dm()
    if ok():
        sw()

def sw():
    global level, total_steps
    total_steps += step
    for _ in range(3):
        display.fill(BLACK)
        utime.sleep(0.12)
        display.fill(PLAYER_COLOR)
        utime.sleep(0.12)
    display.fill(BLACK)
    display.draw_string(40, 80, "Clear!", size=4, color=TITLE_COLOR)
    display.draw_string(30, 110, "Steps:" + str(step), size=3, color=TEXT_COLOR)
    if level + 1 < total_levels:
        display.draw_string(20, 140, "Next Level...", size=2, color=TEXT_COLOR)
    else:
        display.draw_string(20, 140, "All Clear!", size=3, color=TITLE_COLOR)
    utime.sleep(2)
    level = level + 1
    if level >= total_levels:
        display.fill(BLACK)
        display.draw_string(30, 100, "You Win!", size=4, color=TITLE_COLOR)
        display.draw_string(30, 130, "Total:" + str(total_steps), size=3, color=TEXT_COLOR)
        utime.sleep(3)
        import machine
        machine.reset()
    load_level(level)
    dm()

def rd():
    dx = 0
    dy = 0
    x = adcX.read()
    y = adcY.read()
    if x < 500:
        dx = -1
    elif x > 1500:
        dx = 1
    if y > 1500:
        dy = -1
    elif y < 500:
        dy = 1
    return dx, dy

display.fill(BLACK)
display.draw_string(40, 100, "Sokoban", size=4, color=TITLE_COLOR)
display.draw_string(20, 140, "Push Box Game", size=2, color=TEXT_COLOR)
utime.sleep(1.5)

load_level(0)
dm()
last_move = utime.ticks_ms()

while True:
    if pinA.value() == 0:
        load_level(level)
        dm()
        last_move = utime.ticks_ms()
        utime.sleep(0.3)
        continue
    dx, dy = rd()
    now = utime.ticks_ms()
    if dx != 0 or dy != 0:
        if utime.ticks_diff(now, last_move) > 150:
            mv(dx, dy)
            last_move = now
    utime.sleep(0.02)
