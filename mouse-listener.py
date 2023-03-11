from pynput import mouse
from datetime import datetime

tap_duration_sensitivity = 100  # ms
movement_sensitivity = 1  # pixels
longtap_sensitivity = 1000  # ms
lastx = lasty = 0
inGesture = False  # True if a gesture is in progress
gesture = "none"  # Detected gesture name


def on_move(x, y):
    # print(f'Pointer moved to {x}, {y}')
    global lastx, lasty, mdeltax, mdeltay
    mdeltax = x - lastx
    mdeltay = y - lasty
    lastx, lasty = x, y
    xmag = ymag = 0
    xdir = ydir = gesture = "none"
    if inGesture:
        xmag = abs(mdeltax) if abs(mdeltax) > movement_sensitivity else 0
        if xmag > 0:
            xdir = "right" if mdeltax > 0 else "left"
        ymag = abs(mdeltay) if abs(mdeltay) > movement_sensitivity else 0
        if ymag > 0:
            ydir = "down" if mdeltay > 0 else "up"  # y-axis is inverted vs. cartesian
        if ydir == "none":
            gesture = (
                "tap"
                if xdir == "none"
                else "swipe-right"
                if xdir == "right"
                else "swipe-left"
            )
        if xdir == "none" and gesture == "none":
            gesture = (
                "tap"
                if ydir == "none"
                else "swipe-up"
                if ydir == "up"
                else "swipe-down"
            )
        # print(f'Pointer moved by {mdeltax}, {mdeltay}; direction: {xdir}, {ydir}')
        print(f"Gesture: {gesture}")
    pass


def on_click(x, y, button, pressed):
    global presstime, releasetime, startx, starty, deltax, deltay, deltats, deltatms, inGesture, gesture
    presstext = "pressed" if pressed else "released"
    print(f"{button} {presstext} at {x}, {y}")
    if pressed:
        presstime = datetime.now()
        inGesture = True
        startx, starty = x, y
        pass
    elif not pressed:
        releasetime = datetime.now()
        inGesture = False
        deltax, deltay = x - startx, y - starty
        deltats = (releasetime - presstime).seconds * 1000
        deltatms = (releasetime - presstime).microseconds // 1000 + deltats
        if gesture == "tap":
            if deltatms > longtap_sensitivity:
                gesture = "longtap"
        print(
            f"Movement vector {deltax}, {deltay} in {deltatms} ms; Gesture: {gesture}"
        )
        pass


# Collect events until released
def main():
    with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()


if __name__ == "__main__":
    main()
