##
#- Low level Servo PWM control using the PCA9685
##    

import time
import math
from smbus2 import SMBus

# --- PCA9685 low-level control class ---
class PCA9685:
    MODE1 = 0x00
    PRESCALE = 0xFE
    LED0 = 0x06

    def __init__(self, bus_num=7, addr=0x40, freq=50):
        self.bus = SMBus(bus_num)
        self.addr = addr
        self.set_pwm_freq(freq)

    def write8(self, reg, val):
        self.bus.write_byte_data(self.addr, reg, val)

    def read8(self, reg):
        return self.bus.read_byte_data(self.addr, reg)

    def set_pwm_freq(self, freq_hz):
        # Formula from datasheet
        prescale = int(math.floor(25_000_000 / (4096 * freq_hz) - 0.5))
        old = self.read8(self.MODE1)
        self.write8(self.MODE1, (old & 0x7F) | 0x10)  # sleep
        self.write8(self.PRESCALE, prescale)
        self.write8(self.MODE1, old)
        time.sleep(0.005)
        self.write8(self.MODE1, old | 0x80)

    def set_pwm(self, channel, on, off):
        self.write8(self.LED0 + 4*channel    , on & 0xFF)
        self.write8(self.LED0 + 4*channel +1 , (on >> 8) & 0xFF)
        self.write8(self.LED0 + 4*channel +2 , off & 0xFF)
        self.write8(self.LED0 + 4*channel +3 , (off >> 8) & 0xFF)

    def pulse_us_to_ticks(self, pulse_us, freq_hz=50):
        period_us = 1_000_000 / freq_hz
        return int(round(pulse_us / period_us * 4096))

# --- Example usage ---
if __name__ == "__main__":
    pca = PCA9685(bus_num=7, addr=0x40, freq=50)
    channel = 0

    # Example PWM bounds (adjust later)
    servo_min = 1000  # µs
    servo_mid = 1500  # µs (rest)
    servo_max = 2000  # µs

    print("Sweeping from min to max pulse")
    for pulse in (servo_min, servo_mid, servo_max):
        ticks = pca.pulse_us_to_ticks(pulse)
        pca.set_pwm(channel, 0, ticks)
        print(f"Pulse: {pulse} μs → Ticks: {ticks}")
        time.sleep(1)

