import cv2
import numpy as np
import time
import HandTracking as ht
import pyautogui

# Setup
pTime = 0
width, height = 640, 480
frameR = 100
smoothening = 3
prev_x, prev_y = 0, 0
curr_x, curr_y = 0, 0
dragging = False
pinky_interrupt = False

cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

detector = ht.handDetector(maxHands=1, detectionCon=0.8, trackCon=0.8)
screen_width, screen_height = pyautogui.size()

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmlist, bbox = detector.findPosition(img)

    action_text = ""

    if len(lmlist) != 0:
        x1, y1 = lmlist[8][1:]   # Index finger tip
        fingers = detector.fingersUp()

        # Handle pinky interrupt
        if fingers[4] == 1:
            pinky_interrupt = True
        else:
            pinky_interrupt = False

        # Draw boundary
        cv2.rectangle(img, (frameR, frameR), (width - frameR, height - frameR), (255, 0, 255), 2)

        # Move Cursor: Only if pinky is not up and only Thumb + Index are up
        if not pinky_interrupt and fingers == [1, 1, 0, 0, 0]:
            x_screen = np.interp(x1, (frameR, width - frameR), (0, screen_width))
            y_screen = np.interp(y1, (frameR, height - frameR), (0, screen_height))

            curr_x = prev_x + (x_screen - prev_x) / smoothening
            curr_y = prev_y + (y_screen - prev_y) / smoothening

            pyautogui.moveTo(screen_width - curr_x, curr_y)
            cv2.circle(img, (x1, y1), 8, (255, 0, 255), cv2.FILLED)
            prev_x, prev_y = curr_x, curr_y
            action_text = "Move Cursor"

        # Scroll Up: Ring + Pinky
        elif fingers == [0, 0, 0, 1, 1]:
            pyautogui.scroll(30)
            action_text = "Scroll Up"

        # Scroll Down: Index + Pinky
        elif fingers == [0, 1, 0, 0, 1]:
            pyautogui.scroll(-30)
            action_text = "Scroll Down"
        
        # Left Click: Thumb + Index close together
        if not pinky_interrupt and fingers[0] == 1 and fingers[1] == 1:
            length, img, lineInfo = detector.findDistance(4, 8, img)
            if length < 30:
                pyautogui.leftClick()
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                action_text = "Left Click"
                time.sleep(0.3)


        # Right Click: Index + Middle close
        elif fingers[1] == 1 and fingers[2] == 1 and sum(fingers) <= 2:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if length < 25:
                pyautogui.rightClick()
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 0, 255), cv2.FILLED)
                action_text = "Right Click"
                time.sleep(0.3)

        # Drag Start
        elif fingers == [0, 0, 0, 0, 0] and not dragging:
            pyautogui.mouseDown()
            dragging = True
            action_text = "Drag Start"

        # Drag Stop
        elif fingers == [1, 1, 1, 1, 1] and dragging:
            pyautogui.mouseUp()
            dragging = False
            action_text = "Drag Stop"

        if pinky_interrupt:
            action_text = "🛑 Pinky Up — Movement/Click Disabled"

    else:
        if dragging:
            pyautogui.mouseUp()
            dragging = False
            action_text = "Hand Lost - Drag Stopped"

    # Action label
    if action_text:
        cv2.putText(img, action_text, (30, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime - pTime else 0
    pTime = cTime
    cv2.putText(img, f'{int(fps)} FPS', (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    cv2.imshow("Virtual Mouse", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
