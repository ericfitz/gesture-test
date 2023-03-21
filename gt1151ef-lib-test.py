#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

picdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "pic"
)
libdir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "lib"
)
if os.path.exists(libdir):
    sys.path.append(libdir)

from TP_lib import gt1151
from TP_lib import epd2in13_V2
import time
import logging
from PIL import Image, ImageDraw
import threading

logging.basicConfig(level=logging.DEBUG)
flag_t = 1


def pthread_irq():
    print("pthread running")
    while flag_t == 1:
        if gt.digital_read(gt.INT) == 0:
            GT_Dev.Touch = 1
        else:
            GT_Dev.Touch = 0
    print("thread:exit")


def Read_BMP(File, x, y):
    newimage = Image.open(os.path.join(picdir, File))
    image.paste(newimage, (x, y))


# def inRect(gtd, rectangle):
#    if (
#        gtd.X[0] >= rectangle.X[0]
#        and gtd.X[0] <= rectangle.X[1]
#        and gtd.Y[0] >= rectangle.Y[0]
#        and gtd.Y[0] <= rectangle.Y[1]
#    ):
#        return 1
#    else:
#        return 0


try:
    logging.info("epd2in13_V2 Touch Demo")

    epd = epd2in13_V2.EPD()
    gt = gt1151.GT1151()
    GT_Dev = gt1151.GT_Development()
    GT_Old = gt1151.GT_Development()

    logging.info("init and Clear")
    epd.init(epd.FULL_UPDATE)
    gt.GT_Init()
    epd.Clear(0xFF)

    t = threading.Thread(target=pthread_irq)
    t.setDaemon(True)
    t.start()

    # Drawing on the image
    image = Image.open(os.path.join(picdir, "White_board.bmp"))
    epd.displayPartBaseImage(epd.getbuffer(image))
    DrawImage = ImageDraw.Draw(image)
    epd.init(epd.PART_UPDATE)

    i = j = k = ReFlag = SelfFlag = Page = 0

    PagePath = ["White_board.bmp"]

    while 1:
        if i > 12 or ReFlag == 1:
            if Page == 1 and SelfFlag == 0:
                epd.displayPartial(epd.getbuffer(image))
            else:
                epd.displayPartial_Wait(epd.getbuffer(image))
            i = 0
            k = 0
            j += 1
            ReFlag = 0
            print("*** Draw Refresh ***\r\n")
        elif k > 50000 and i > 0 and Page == 1:
            epd.displayPartial(epd.getbuffer(image))
            i = 0
            k = 0
            j += 1
            print("*** Overtime Refresh ***\r\n")
        elif j > 50 or SelfFlag:
            SelfFlag = 0
            j = 0
            epd.init(epd.FULL_UPDATE)
            epd.displayPartBaseImage(epd.getbuffer(image))
            epd.init(epd.PART_UPDATE)
            print("--- Self Refresh ---\r\n")
        else:
            k += 1

        gt.GT_Scan(GT_Dev, GT_Old)
        if (
            GT_Old.X[0] == GT_Dev.X[0]
            and GT_Old.Y[0] == GT_Dev.Y[0]
            and GT_Old.S[0] == GT_Dev.S[0]
        ):
            continue

        if GT_Dev.TouchpointFlag:
            i += 1
            GT_Dev.TouchpointFlag = 0

            if Page == 0 and ReFlag == 0:  # white board
                DrawImage.rectangle(
                    [
                        (GT_Dev.X[0], GT_Dev.Y[0]),
                        (
                            GT_Dev.X[0] + GT_Dev.S[0] / 8 + 1,
                            GT_Dev.Y[0] + GT_Dev.S[0] / 8 + 1,
                        ),
                    ],
                    fill=0,
                )
                if (
                    GT_Dev.X[0] > 96
                    and GT_Dev.X[0] < 118
                    and GT_Dev.Y[0] > 113
                    and GT_Dev.Y[0] < 136
                ):
                    print("Clear ...\r\n")
                    Page = 0
                    Read_BMP(PagePath[Page], 0, 0)
                    ReFlag = 1
                elif (
                    GT_Dev.X[0] > 96
                    and GT_Dev.X[0] < 118
                    and GT_Dev.Y[0] > 220
                    and GT_Dev.Y[0] < 242
                ):
                    print("Refresh ...\r\n")
                    SelfFlag = 1
                    ReFlag = 1


except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    flag_t = 0
    epd.sleep()
    time.sleep(2)
    t.join()
    epd.Dev_exit()
    exit()
