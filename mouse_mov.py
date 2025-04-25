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

# GUI colors
colors = {
    "cursor": (255, 0, 255),
    "drag": (0, 255, 255),
    "click": (0, 255, 0),
    "right_click": (0, 0, 255),
    "text": (0, 255, 255),
    "scroll": (255, 255, 0),
    "info_bg": (50, 50, 50)
}

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmlist, bbox = detector.findPosition(img)

    action_text = "Waiting for hand..."
    hand_detected = False

    if len(lmlist) != 0:
        hand_detected = True
        x1, y1 = lmlist[8][1:]   # Index finger tip
        fingers = detector.fingersUp()

        # Handle pinky interrupt
        pinky_interrupt = fingers[4] == 1

        # Draw boundary rectangle
        cv2.rectangle(img, (frameR, frameR), (width - frameR, height - frameR), colors["cursor"], 2)

        # Move Cursor
        if not pinky_interrupt and fingers == [1, 1, 0, 0, 0]:
            x_screen = np.interp(x1, (frameR, width - frameR), (0, screen_width))
            y_screen = np.interp(y1, (frameR, height - frameR), (0, screen_height))

            curr_x = prev_x + (x_screen - prev_x) / smoothening
            curr_y = prev_y + (y_screen - prev_y) / smoothening

            pyautogui.moveTo(screen_width - curr_x, curr_y)
            cv2.circle(img, (x1, y1), 12, colors["cursor"], cv2.FILLED)
            prev_x, prev_y = curr_x, curr_y
            action_text = "🖱 Move Cursor"

        # Scroll Up
        elif fingers == [0, 0, 0, 1, 1]:
            pyautogui.scroll(30)
            action_text = "⬆️ Scroll Up"

        # Scroll Down
        elif fingers == [0, 1, 0, 0, 1]:
            pyautogui.scroll(-30)
            action_text = "⬇️ Scroll Down"

        # Left Click
        if not pinky_interrupt and fingers[0] == 1 and fingers[1] == 1:
            length, img, lineInfo = detector.findDistance(4, 8, img)
            if length < 30:
                pyautogui.leftClick()
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 20, colors["click"], cv2.FILLED)
                action_text = "✅ Left Click"
                time.sleep(0.3)

        # Right Click
        elif fingers[1] == 1 and fingers[2] == 1 and sum(fingers) <= 2:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if length < 25:
                pyautogui.rightClick()
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 20, colors["right_click"], cv2.FILLED)
                action_text = "❎ Right Click"
                time.sleep(0.3)

        # Drag Start
        elif fingers == [0, 0, 0, 0, 0] and not dragging:
            pyautogui.mouseDown()
            dragging = True
            action_text = "📥 Drag Start"

        # Drag Stop
        elif fingers == [1, 1, 1, 1, 1] and dragging:
            pyautogui.mouseUp()
            dragging = False
            action_text = "📤 Drag Stop"

        if pinky_interrupt:
            action_text = "🛑 Pinky Up — Disabled"

    else:
        if dragging:
            pyautogui.mouseUp()
            dragging = False
            action_text = "❌ Hand Lost — Drag Stopped"

    # Status Info Panel
    cv2.rectangle(img, (0, height - 60), (width, height), colors["info_bg"], -1)
    cv2.putText(img, f'Status: {action_text}', (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors["text"], 2)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime - pTime else 0
    pTime = cTime
    cv2.putText(img, f'{int(fps)} FPS', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Display
    cv2.imshow("🖐 Virtual Mouse Controller", img)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
        break

cap.release()
cv2.destroyAllWindows()
