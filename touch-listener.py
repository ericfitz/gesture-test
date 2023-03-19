#!/opt/homebrew/bin/python3

#from pynput import mouse
from gt1151ef import TouchData, GT1151
from datetime import datetime

movement_sensitivity = 1  # pixels
longtap_sensitivity = 1000  # ms

# lastx = 0
lasty = 0
inGesture = False  # True if a gesture is in progress
swiped = False  # True if a swipe has been detected

def on_move(x, y):
    # print(f'Pointer moved to {x}, {y}')
    # global lastx, mdeltax
    global lasty, mdeltay
    global swiped, inGesture, move_gesture

    # mdeltax = x - lastx
    mdeltay = int(y - lasty)
    # lastx = x
    lasty = int(y)
    ymag = 0
    if inGesture:
        # xmag = abs(mdeltax) if abs(mdeltax) > movement_sensitivity else 0
        # if xmag > 0:
            # xdir = "right" if mdeltax > 0 else "left"
        ymag = 0 if abs(mdeltay) < movement_sensitivity else int(abs(mdeltay))

        ydir = "none"
        if ymag > 0:
            ydir = "down" if mdeltay > 0 else "up"  # y-axis is inverted vs. cartesian (positive = down)
        
        if ydir == "up":
            move_gesture = "swipe-up"
            swiped = True
        elif ydir == "down":
            move_gesture = "swipe-down"
            swiped = True
        else:
            move_gesture = "none"
        print(f"Gesture: {move_gesture}; Magnitude: {ymag}")
    pass


def on_click(x, y, button, pressed):
    
    global presstime, releasetime, deltats, deltatms 
    global startx, deltax
    global starty, deltay
    global inGesture, gesture, swiped

    presstext = "pressed" if pressed else "released"
    print(f"{button} {presstext} at {int(x)}, {int(y)}")
    if pressed:
        presstime = datetime.now()
        inGesture = True
        startx = int(x)
        starty = int(y)
        pass
    elif not pressed:
        releasetime = datetime.now()
        inGesture = False
        deltax = int(int(x) - startx)
        deltay = int(int(y) - starty)
        deltats = int((releasetime - presstime).seconds * 1000)
        deltatms = int((releasetime - presstime).microseconds // 1000 + deltats)
        if not swiped:
            gesture = "tap" if deltatms < longtap_sensitivity else "longtap"
        elif swiped:
            gesture = "swipe"
        print(
            f"Movement vector {deltax}, {deltay} in {deltatms} ms; Gesture: {gesture}"
        )
        swiped = False
        pass


# Collect events until released
def main():
    with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()


if __name__ == "__main__":
    main()
