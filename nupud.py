import time
import threading
from evdev import InputDevice, list_devices, categorize, ecodes

def monitor_device(device_path):
    try:
        device = InputDevice(device_path)
        print(f"Monitoring: {device_path}")
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == key_event.key_down:
                    print(f"Key pressed on {device_path}: {key_event.keycode}")
    except Exception as e:
        print(f"Error with {device_path}: {e}")

def switch_devices():
    devices = list_devices()
    index = 0
    
    while True:
        if devices:
            device_path = devices[index % len(devices)]
            monitor_thread = threading.Thread(target=monitor_device, args=(device_path,), daemon=True)
            monitor_thread.start()
            time.sleep(3)
            index += 1
        else:
            print("No input devices found.")
            time.sleep(3)

if __name__ == "__main__":
    switch_devices()
