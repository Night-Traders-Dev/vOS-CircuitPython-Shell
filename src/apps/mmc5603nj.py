import time
import board
import busio
from adafruit_mmc56x3 import MMC5603

i2cl = busio.I2C(scl = board.GP11, sda = board.GP10)

magnetometer = MMC5603(i2cl)
magnetometer.data_rate = 1000
magnetometer.continuous_mode = True

while True:
    print(magnetometer.magnetic)
    time.sleep(0.1)
