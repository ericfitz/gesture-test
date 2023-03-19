#!/opt/homebrew/bin/python3

from gt1151ef import TouchData, GT1151
import threading
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z"
)

logger = logging.getLogger(__name__)

flag_t = 1

def pthread_irq() :
    print("pthread running")
    while flag_t == 1 :
        if(gt.digital_read(gt.INT) == 0) :
            GT_Dev.Touch = 1
        else :
            GT_Dev.Touch = 0
    print("thread:exit")

def main():
    gt = GT1151()
    GT_Dev = TouchData()
    GT_Old = TouchData()


if __name__ == '__main__':
    main()
    logger.info("main:exit")
