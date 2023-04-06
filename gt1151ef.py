import time
import logging
import RPi.GPIO as GPIO
from smbus import SMBus

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"
)

logger = logging.getLogger(__name__)

# Waveshare epd2in13 touchpad GPIO pin assignments
TRST = 22
INT = 27

# initialize GPIO
address = 0x0
bus = SMBus(1)

max_touches = 2


class TouchData:
    def __init__(self):
        self.Touch = 0
        self.TouchpointFlag = 0
        self.TouchCount = 0
        self.Touchkeytrackid = [0, 1, 2, 3, 4]
        self.X = [0, 1, 2, 3, 4]
        self.Y = [0, 1, 2, 3, 4]
        self.S = [0, 1, 2, 3, 4]


# this is a modified version of the GT1151 class from the Waveshare epd2in13 software
# it merges dependent functions into a single class and isolates touchpad functionality
class GT1151:
    def __init__(self):
        self.TRST = TRST
        self.INT = INT
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(TRST, GPIO.OUT)
        GPIO.setup(INT, GPIO.IN)
        # spi.max_speed_hz = 10000000
        # spi.mode = 0b00

    def digital_write(self, pin, value):
        GPIO.output(pin, value)

    def digital_read(self, pin):
        return GPIO.input(pin)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def i2c_writebyte(self, reg, value):
        bus.write_word_data(
            address, (reg >> 8) & 0xFF, (reg & 0xFF) | ((value & 0xFF) << 8)
        )

    def i2c_write(self, reg):
        bus.write_byte_data(address, (reg >> 8) & 0xFF, reg & 0xFF)

    def i2c_readbyte(self, reg, len):
        self.i2c_write(reg)
        rbuf = []
        for i in range(len):
            rbuf.append(int(bus.read_byte(address)))
        return rbuf

    def GT_Reset(self):
        self.digital_write(TRST, 1)
        self.delay_ms(100)
        self.digital_write(TRST, 0)
        self.delay_ms(100)
        self.digital_write(TRST, 1)
        self.delay_ms(100)

    def GT_Write(self, Reg, Data):
        self.i2c_writebyte(Reg, Data)

    def GT_Read(self, Reg, len):
        return self.i2c_readbyte(Reg, len)

    def GT_ReadVersion(self):
        buf = self.GT_Read(0x8140, 4)
        print(buf)

    def GT_Init(self):
        self.GT_Reset()
        self.GT_ReadVersion()

    def GT_Scan(self, current_touch, old_touch):
        buf = []
        mask = 0x00

        if current_touch.Touch == 1:
            current_touch.Touch = 0
            buf = self.GT_Read(0x814E, 1)

            if buf[0] & 0x80 == 0x00:
                self.GT_Write(0x814E, mask)
                self.delay_ms(10)

            else:
                current_touch.TouchpointFlag = buf[0] & 0x80
                current_touch.TouchCount = buf[0] & 0x0F

                if current_touch.TouchCount > 5 or current_touch.TouchCount < 1:
                    self.GT_Write(0x814E, mask)
                    return

                buf = self.GT_Read(0x814F, current_touch.TouchCount * 8)
                self.GT_Write(0x814E, mask)

                logger.debug(f"TouchCount: {current_touch.TouchCount}")

                # it might be the right thing to do to set the touch count to 0 here and ignore more than double touch
                touch_count = (
                    max_touches
                    if current_touch.TouchCount > max_touches
                    else current_touch.TouchCount
                )

                for i in range(0, touch_count, 1):
                    old_touch.X[i] = current_touch.X[i]
                    old_touch.Y[i] = current_touch.Y[i]
                    old_touch.S[i] = current_touch.S[i]
                    current_touch.Touchkeytrackid[i] = buf[0 + 8 * i]
                    current_touch.X[i] = (buf[2 + 8 * i] << 8) + buf[1 + 8 * i]
                    current_touch.Y[i] = (buf[4 + 8 * i] << 8) + buf[3 + 8 * i]
                    current_touch.S[i] = (buf[6 + 8 * i] << 8) + buf[5 + 8 * i]
                    logger.debug(
                        f"Touch {i}:  X: {current_touch.X[i]}, Y:{current_touch.Y[i]}, Pressure:{current_touch.S[i]}"
                    )

    def GT_Gesture(self):
        buf = [0x08, 0x00, 0xF8]
        self.GT_Write(0x8040, buf[0], 1)
        self.GT_Write(0x8041, buf[1], 1)
        self.GT_Write(0x8042, buf[2], 1)
        GT_Gesture_Mode = 1
        logger.debug("Gesture mode started")
        self.delay_ms(1)

    def GT_Gesture_Scan(self, current_touch, old_touch):
        buf = []
        self.GT_Read(0x814C, buf, 1)
        logger.debug(f"Gesture: {buf}")
        if buf == 0xCC:
            logger.debug("Gesture mode exiting")
            GT_Gesture_Mode = 0
            self.GT_Reset()
        else:
            buf = 0x00
            self.GT_Write(0x814C, buf, 1)
