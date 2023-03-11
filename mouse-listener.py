from pynput import mouse
from datetime import datetime

tap_duration_threshold = 100  # ms
move_threshold = 1  # pixels
lastx = lasty = 0
inGesture = False
gesture = "none"

def on_move(x, y):
    # print(f'Pointer moved to {x}, {y}')
    global lastx, lasty, mdeltax, mdeltay
    mdeltax = x - lastx
    mdeltay = y - lasty
    lastx, lasty = x, y
    xmag = ymag = 0
    xdir = ydir = gesture = "none"
    if inGesture:
        xmag = abs(mdeltax) if abs(mdeltax) > move_threshold else 0
        if xmag > 0:
            xdir = "right" if mdeltax > 0 else "left"
        ymag = abs(mdeltay) if abs(mdeltay) > move_threshold else 0
        if ymag > 0:
            ydir = "down" if mdeltay > 0 else "up" # y-axis is inverted vs. cartesian
        if ydir == "none":
            gesture = "tap" if xdir == "none" else "swipe-right" if xdir == "right" else "swipe-left"
        if xdir == "none" and gesture == "none":
            gesture = "tap" if ydir == "none" else "swipe-up" if ydir == "up" else "swipe-down"
        # print(f'Pointer moved by {mdeltax}, {mdeltay}; direction: {xdir}, {ydir}')
        print(f'Gesture: {gesture}')
    pass


def on_click(x, y, button, pressed):
    global presstime, releasetime, startx, starty, deltax, deltay, deltats, deltatms, inGesture
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
        tapgesture = "tap" if deltatms < tap_duration_threshold else gesture
        print(f"Movement vector {deltax}, {deltay} in {deltatms} ms; Gesture: {gesture}")
        pass


# Collect events until released
def main():
    with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()


if __name__ == "__main__":
    main()
