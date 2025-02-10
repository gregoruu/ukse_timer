import time
import threading
import tkinter as tk
from evdev import InputDevice, list_devices, categorize, ecodes

class DeviceMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Device Monitor")
        self.root.geometry("500x300")
        
        self.device_label = tk.Label(root, text="Monitoring: None", font=("Arial", 14))
        self.device_label.pack(pady=10)
        
        self.log_text = tk.Text(root, height=10, width=50)
        self.log_text.pack()
        
        self.devices = list_devices()
        self.index = 0
        
        self.switch_thread = threading.Thread(target=self.switch_devices, daemon=True)
        self.switch_thread.start()
    
    def log_event(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
    
    def monitor_device(self, device_path):
        try:
            device = InputDevice(device_path)
            self.device_label.config(text=f"Monitoring: {device_path}")
            for event in device.read_loop():
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == key_event.key_down:
                        self.root.after(0, self.log_event, f"Key on {device_path}: {key_event.keycode}")
        except Exception as e:
            self.root.after(0, self.log_event, f"Error with {device_path}: {e}")
    
    def switch_devices(self):
        while True:
            if self.devices:
                device_path = self.devices[self.index % len(self.devices)]
                monitor_thread = threading.Thread(target=self.monitor_device, args=(device_path,), daemon=True)
                monitor_thread.start()
                time.sleep(3)
                self.index += 1
            else:
                self.root.after(0, self.log_event, "No input devices found.")
                time.sleep(3)

if __name__ == "__main__":
    root = tk.Tk()
    app = DeviceMonitorApp(root)
    root.mainloop()
