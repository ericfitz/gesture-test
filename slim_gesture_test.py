from gt1151_slim import Touch, GT1151

gt = GT1151()
gt.reset()
gt.gesture_mode()
old_touch = Touch()
curr_touch = Touch()

while True:
    gt.enable_gesture_mode()
    gesture = gt.gesture_scan(old_touch, new_touch)
    print(new_touch.X[0], new_touch.Y[0], new_touch.S[0])
