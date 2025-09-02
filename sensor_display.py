import pygame
import time
import sys
import smbus2

# --- Seaded ---
I2C_BUS = 0           # I²C bus (tavaliselt 1 Orange Pi 3 LTS)
PTE7300_ADDR = 0x6C   # PTE7300 I²C aadress, kontrolli datasheetist
THRESHOLD = 1000      # läve väärtus
COUNTDOWN = 10        # sekundites

# --- I²C seadistus ---
try:
    bus = smbus2.SMBus(I2C_BUS)
except Exception as e:
    print("Ei saanud I²C bussi avada:", e)
    sys.exit(1)

def read_pressure():
    try:
        data = bus.read_i2c_block_data(PTE7300_ADDR, 0, 2)  # 2 baiti lugemiseks
        raw = (data[0] << 8) | data[1]
        return raw
    except Exception as e:
        print("I²C error:", e)
        return None

# --- Pygame seaded ---
pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PTE7300 Live Monitor")
font_big = pygame.font.SysFont("Arial", 60)
font_small = pygame.font.SysFont("Arial", 30)

# Countdown olek
countdown_active = False
countdown_end = 0

clock = pygame.time.Clock()

# --- Põhitsükkel ---
while True:
    # --- Event handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            bus.close()
            sys.exit()

    # --- Loe sensorit ---
    sensor_value = read_pressure()

    # Trigger loogika
    if sensor_value is not None and sensor_value > THRESHOLD and not countdown_active:
        countdown_active = True
        countdown_end = time.time() + COUNTDOWN

    # --- Graafika ---
    screen.fill((30, 30, 30))  # taust

    if sensor_value is not None:
        text_sensor = font_big.render(f"Sensor: {sensor_value}", True, (0, 200, 0))
        screen.blit(text_sensor, (50, 100))
    else:
        text_sensor = font_big.render("No Data", True, (200, 0, 0))
        screen.blit(text_sensor, (50, 100))

    # Countdown kuvamine
    if countdown_active:
        remaining = int(countdown_end - time.time())
        if remaining > 0:
            text_timer = font_big.render(f"Countdown: {remaining}s", True, (200, 200, 0))
            screen.blit(text_timer, (50, 200))
        else:
            text_timer = font_big.render("Countdown lõppes!", True, (200, 0, 0))
            screen.blit(text_timer, (50, 200))
            countdown_active = False

    # Läve kuvamine
    text_thresh = font_small.render(f"Threshold: {THRESHOLD}", True, (180, 180, 180))
    screen.blit(text_thresh, (50, 20))

    pygame.display.flip()
    clock.tick(30)  # 30 FPS
