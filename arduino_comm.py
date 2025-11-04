import serial
import serial.tools.list_ports
import time

class ArduinoComm:
    def __init__(self, port=None, baudrate=9600):
        if port is None:
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                print("⚠️  No Arduino ports found.")
                self.arduino = None
                return
            for p in ports:
                if "Arduino" in p.description or "CH340" in p.description:
                    port = p.device
                    break
            if port is None:
                port = ports[0].device  # fallback
        try:
            self.arduino = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)  # wait for Arduino reset
            print(f"✅ Connected to Arduino on {port}")
        except Exception as e:
            print(f"❌ Could not connect to Arduino: {e}")
            self.arduino = None

    def send(self, message):
        if not self.arduino:
            print("⚠️ Arduino not connected.")
            return False
        try:
            self.arduino.write(message.encode())
            return True
        except Exception as e:
            print(f"Serial write error: {e}")
            return False

    def close(self):
        if self.arduino:
            self.arduino.close()

def send_state(arduino, state):
    """
    Sends 'N' for normal and 'D' for drowsy.
    """
    if not arduino:
        return False
    try:
        if state == "normal":
            return arduino.send('N')
        elif state == "drowsy":
            return arduino.send('D')
        else:
            print(f"Unknown state: {state}")
            return False
    except Exception as e:
        print(f"send_state error: {e}")
        return False
