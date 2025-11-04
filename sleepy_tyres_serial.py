import cv2
import mediapipe as mp
import time
import threading
from playsound import playsound
from arduino_comm import ArduinoComm, send_state

def play_alert():
    try:
        playsound("alert.mp3")
    except Exception as e:
        print("Sound error:", e)

# Connect to Arduino
arduino = ArduinoComm(port="COM8")  # change COM8 if needed
last_sent_state = None

# Face mesh setup
cap = cv2.VideoCapture(0)
mp_face = mp.solutions.face_mesh
face = mp_face.FaceMesh(refine_landmarks=True)

eye_closed = False
closed_time = 0
alert_triggered = False
recovery_delay = 2
recovery_start_time = None
led_color = (128, 128, 128)
motor_speed = 100

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face.process(rgb)
        status = "Unknown"

        if results.multi_face_landmarks:
            for lm in results.multi_face_landmarks:
                left = abs(lm.landmark[159].y - lm.landmark[145].y)
                right = abs(lm.landmark[386].y - lm.landmark[374].y)
                avg = (left + right) / 2

                if avg < 0.011:  # eyes closed
                    if not eye_closed:
                        closed_time = time.time()
                        eye_closed = True
                    elif time.time() - closed_time > 1.5:
                        status = "Eyes Closed"
                        led_color = (0, 0, 255)
                        motor_speed = max(motor_speed - 5, 0)
                        if not alert_triggered:
                            threading.Thread(target=play_alert, daemon=True).start()
                            alert_triggered = True
                        recovery_start_time = None
                else:
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

        # Draw LED + text
        cv2.rectangle(frame, (30, 30), (80, 80), led_color, -1)
        cv2.putText(frame, f"Motor Speed: {motor_speed}", (100, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        cv2.putText(frame, status, (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
        cv2.imshow("Sleepy Tyres System", frame)

        # Serial communication to Arduino
        desired_state = "drowsy" if status == "Eyes Closed" else "normal" if status == "Eyes Open" else None
        if desired_state and desired_state != last_sent_state:
            ok = send_state(arduino, desired_state)
            if ok:
                last_sent_state = desired_state
                print(f"[SERIAL] Sent -> {desired_state}")

        if cv2.waitKey(1) & 0xFF == 27:
            break

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    arduino.close()
    cap.release()
    cv2.destroyAllWindows()
