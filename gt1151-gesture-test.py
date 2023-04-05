#!/opt/homebrew/bin/python3

from gt1151ef import TouchData, GT1151
import logging
import threading

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"
)

logger = logging.getLogger(__name__)

flag_t = 1

def pthread_irq():
    logger.debug("pthread running")
    while flag_t == 1:
        if gt.digital_read(gt.INT) == 0:
            gest_current.Touch = 1
        else:
            gest_current.Touch = 0
    print("thread:exit")

def main():
    gt = GT1151()

    gest_current = TouchData()
    gest_old = TouchData()


    logger.info("testing gt1151 gesture functionality")

    try:

        gt.GT_Init()  # initialize GT1151 touch controller
        gt.Gesture()  # enable gesture mode

        t = threading.Thread(target=pthread_irq)
        t.setDaemon(True)
        t.start()

        while 1:
            gt.GT_Gesture_Scan(gest_current, gest_old)
            logging.debug(f"Touch: {gest_current.Touch}")
            logging.debug(f"TouchpointFlag: {gest_current.TouchpointFlag}")
            logging.debug(f"TouchCount: {gest_current.TouchCount}")
            logging.debug(f"Touchkeytrackid: {gest_current.Touchkeytrackid}")
            logging.debug(f"X: {gest_current.X}")
            logging.debug(f"Y: {gest_current.Y}")
            logging.debug(f"S: {gest_current.S}")
            gest_old = gest_current


    except IOError as e:
        logging.error(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        flag_t = 0
        t.join()
        exit()

if __name__ == '__main__':
    main()
    logger.info("main:exit")
