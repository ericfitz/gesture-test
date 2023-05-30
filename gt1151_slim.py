import RPi.GPIO as GPIO
import time
from smbus import SMBus

# GPIO pin assignments for WaveShare 2.13 touch e-ink hat
TRST = 22
INT = 27

address = 0x14
gesture_mode = 0
bus = SMBus(1)

MAX_TOUCH = 5


class Touch:
    def __init__(self):
        self.Touch = 0
        self.TouchpointFlag = 0
        self.TouchCount = 0
        for i in range(0, MAX_TOUCH, 1):
            self.Touchkeytrackid = i
            self.X = i
            self.Y = i
            self.S = i


class GT1151:
    def __init__(self):
        self.TRST = TRST
        self.INT = INT
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(TRST, GPIO.OUT)
        GPIO.setup(INT, GPIO.IN)
        self.disable_gesture_mode()
        print("constructor")

    def __del__(self):
        bus.close()
        GPIO.output(TRST, 0)
        GPIO.cleanup()
        print("destructor")

    def reset(self):
        GPIO.output(TRST, 1)
        self.delay_ms(100)
        GPIO.output(TRST, 0)
        self.delay_ms(100)
        GPIO.output(TRST, 1)
        self.delay_ms(100)
        print("reset")

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def i2c_writebyte(self, reg, value):
        # write a byte as a word to the I2C bus, shifted to the left by 8 bits
        bus.write_word_data(
            address, (reg >> 8) & 0xFF, (reg & 0xFF) | ((value & 0xFF) << 8)
        )

    def i2c_write(self, reg):
        # write one byte to the I2C bus
        bus.write_byte_data(address, (reg >> 8) & 0xFF, reg & 0xFF)

    def i2c_readbyte(self, reg, len):
        # read len bytes from the I2C bus
        self.i2c_write(reg)
        rbuf = []
        for i in range(len):
            rbuf.append(int(bus.read_byte(address)))
        return rbuf

    def read_version(self):
        buf = self.i2c_readbyte(0x8140, 4)
        print("Version: ", buf[0], buf[1], buf[2], buf[3])

    def init(self):
        self.reset()
        self.read_version()

    def scan(self, curr_touch, old_touch):
        # detect touch and update touch info
        buf = []
        mask = 0x00

        if curr_touch.Touch == 1:
            curr_touch.Touch = 0
            buf = self.i2c_readbyte(0x814E, 1)

            if buf[0] & 0x80 == 0x00:
                self.i2c_writebyte(0x814E, mask)
                self.delay_ms(10)

            else:
                curr_touch.TouchpointFlag = buf[0] & 0x80
                curr_touch.TouchCount = buf[0] & 0x0F

                if curr_touch.TouchCount > 5 or curr_touch.TouchCount < 1:
                    self.i2c_writebyte(0x814E, mask)
                    return

                buf = self.i2c_readbyte(0x814F, curr_touch.TouchCount * 8)
                self.i2c_writebyte(0x814E, mask)

                for i in range(0, MAX_TOUCH, 1):
                    old_touch.X[i] = curr_touch.X[i]
                    old_touch.Y[i] = curr_touch.Y[i]
                    old_touch.S[i] = curr_touch.S[i]

                for i in range(0, curr_touch.TouchCount, 1):
                    curr_touch.Touchkeytrackid[i] = buf[0 + 8 * i]
                    curr_touch.X[i] = (buf[2 + 8 * i] << 8) + buf[1 + 8 * i]
                    curr_touch.Y[i] = (buf[4 + 8 * i] << 8) + buf[3 + 8 * i]
                    curr_touch.S[i] = (buf[6 + 8 * i] << 8) + buf[5 + 8 * i]
                    print(
                        "touch ",
                        i,
                        ":",
                        curr_touch.X[i],
                        curr_touch.Y[i],
                        curr_touch.S[i],
                    )

    def gesture_mode(self):
        # put the GT1151 into gesture mode
        self.i2c_writebyte(0x8040, 0x08)
        self.i2c_writebyte(0x8041, 0x00)
        self.i2c_writebyte(0x8042, 0xF8)
        gesture_mode = 1

    def gesture_scan(self, curr_touch, old_touch):
        # detect gesture and return gesture info
        buf = self.i2c_readbyte(0x814C, 1)
        if buf == 0xCC:
            gesture_mode = 0
            self.reset()
            for i in range(0, MAX_TOUCH, 1):
                old_touch.X[i] = curr_touch.X[i]
                old_touch.Y[i] = curr_touch.Y[i]
                old_touch.S[i] = curr_touch.S[i]
        else:
            buf = 0x00
            self.i2c_writebyte(0x814C, buf)

    def disable_gesture_mode(self):
        # put the GT1151 into normal mode
        self.i2c_writebyte(0x8040, 0x00)
        gesture_mode = 0
