import cv2
import mediapipe as mp
import time
import pygame
import threading

pygame.mixer.init()

def play_alert():
    pygame.mixer.music.load("alert.mp3")
    pygame.mixer.music.play()


cap = cv2.VideoCapture(0)
mp_face = mp.solutions.face_mesh
face = mp_face.FaceMesh(refine_landmarks=True)

eye_closed = False
closed_time = 0
motor_speed = 100
led_color = (128, 128, 128)
alert_triggered = False
recovery_delay = 2  # seconds
recovery_start_time = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face.process(rgb)

    h, w, _ = frame.shape
    status = "Unknown"

    if results.multi_face_landmarks:
        for lm in results.multi_face_landmarks:
            
            left = abs(lm.landmark[159].y - lm.landmark[145].y)
            right = abs(lm.landmark[386].y - lm.landmark[374].y)
            print(f"Eye Distances → Left: {left:.4f}, Right: {right:.4f}")

            if left < 0.012 and right < 0.010:
                print("Eyes Open")
            # # Closed


            # left = lm.landmark[159].y - lm.landmark[145].y
            # right = lm.landmark[386].y - lm.landmark[374].y

            # if left < 0.01 and right < 0.01:
                if not eye_closed:
                    closed_time = time.time()
                    eye_closed = True
                elif time.time() - closed_time > 1.5:
                    status = "Eyes Closed"
                    led_color = (0, 0, 255)  # Red
                    if motor_speed > 0:
                        motor_speed -= 2
                        motor_speed = max(motor_speed, 0)
                    if not alert_triggered:
                        threading.Thread(target=play_alert, daemon=True).start()
                        alert_triggered = True
                    recovery_start_time = None
            else:
                print("Eyes Closed")
                if eye_closed:
                    eye_closed = False
                    recovery_start_time = time.time()
                if recovery_start_time:
                    if time.time() - recovery_start_time > recovery_delay:
                        status = "Eyes Open"
                        led_color = (0, 255, 0)
                        motor_speed = 100
                        alert_triggered = False
                        recovery_start_time = None
                    else:
                        status = "Recovering..."
                else:
                    status = "Eyes Open"
                    led_color = (0, 255, 0)

    # Simulated LED
    cv2.rectangle(frame, (30, 30), (80, 80), led_color, -1)

    # Display motor speed and status
    cv2.putText(frame, f"Motor Speed: {motor_speed}", (100, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
    cv2.putText(frame, status, (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

    cv2.imshow("Eye Control Simulation", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()