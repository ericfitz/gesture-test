from pynput import mouse
import time


def on_move(x, y):
    print("Pointer moved to {0}".format((x, y)))


def on_click(x, y, button, pressed):
    print("{0} at {1}".format("Pressed" if pressed else "Released", (x, y)))
    if not pressed:
        # Stop listener
        # return False
        pass


def main():
    listener = mouse.Listener(on_move=on_move, on_click=on_click)
    listener.start()
    print("Listener started")
    try:
        while True:
            time.sleep(0.1)
            pass
    except KeyboardInterrupt:
        listener.stop()
        print("Listener stopped")
        exit(0)


if __name__ == "__main__":
    main()
