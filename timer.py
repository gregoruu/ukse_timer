import tkinter as tk
from time import sleep, time
import threading
import pygame
from evdev import InputDevice, categorize, ecodes, list_devices

class DualTimerApp:
    def __init__(self, root, device_name):
        self.root = root
        self.root.title("Dual Timer")
        
        self.timer1_running = False
        self.timer2_running = False
        self.timer1_paused = False
        self.timer2_paused = False
        self.timer1_value = 0
        self.timer2_value = 0
        self.timer1_max_value = None
        self.timer2_min_value = None
        self.countdown = False
        self.presets = [
            (15*60, 3*60, "RC 2 UP"),
            (20*60, 5*60, "RC 3 UP"),
            (30*60, 10*60, "RC 4 UP"),
            (35*60, 15*60, "RC 5 UP"),
            (40*60, 20*60, "RC 6 UP"),
            (15*60, 3*60, True, "RC 2 DOWN"),
            (20*60, 5*60, True, "RC 3 DOWN"),
            (30*60, 10*60, True, "RC 4 DOWN"),
            (35*60, 15*60, True, "RC 5 DOWN"),
            (40*60, 20*60, True, "RC 6 DOWN")
        ]
        self.current_preset_index = 0
        self.root.attributes("-fullscreen", True)

        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)

        self.preset_label = tk.Label(self.container, text="", font=("Arial", 80), anchor="w")
        self.preset_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.label1 = tk.Label(self.container, text="00:00", font=("Arial", 300))
        self.label1.grid(row=0, column=1, padx=20, pady=10)

        self.label2 = tk.Label(self.container, text="00:00", font=("Arial", 300))
        self.label2.grid(row=1, column=1, padx=20, pady=10)

        pygame.mixer.init()

        self.device = self.find_device(device_name)
        if self.device:
            self.input_thread = threading.Thread(target=self.read_input, daemon=True)
            self.input_thread.start()

        self.set_preset(*self.presets[self.current_preset_index])

    def find_device(self, device_name):
        for path in list_devices():
            device = InputDevice(path)
            if device_name in device.name:
                return InputDevice(path)
        return None

    def read_input(self):
        for event in self.device.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == key_event.key_down:
                    if key_event.keycode == 'KEY_LEFT':
                        self.previous_preset()
                    elif key_event.keycode == 'KEY_RIGHT':
                        self.next_preset()
                    elif key_event.keycode == 'KEY_ENTER':
                        self.pause_resume_timer2()
                    elif key_event.keycode == 'KEY_ESC':
                        self.reset_timers()

    def set_preset(self, timer1_value, timer2_value, *args):
        self.countdown = args[0] if len(args) > 0 and isinstance(args[0], bool) else False
        preset_name = args[1] if len(args) > 1 else args[0] if len(args) > 0 else ""
        self.preset_label.config(text=preset_name)
        if self.countdown:
            self.timer1_value = timer1_value
            self.timer2_value = timer2_value
        else:
            self.timer1_value = 0
            self.timer2_value = 0
            self.timer1_max_value = timer1_value
            self.timer2_min_value = timer2_value
        self.update_timer1_display()
        self.update_timer2_display()

    def update_timer1_display(self):
        minutes, seconds = divmod(int(self.timer1_value), 60)
        self.label1.config(text=f"{minutes:02}:{seconds:02}")

    def update_timer2_display(self):
        minutes, seconds = divmod(int(self.timer2_value), 60)
        self.label2.config(text=f"{minutes:02}:{seconds:02}")

    def reset_timers(self):
        self.timer1_running = False
        self.timer2_running = False
        self.timer1_paused = False
        self.timer2_paused = False
        self.timer1_value = 0
        self.timer2_value = 0
        self.update_timer1_display()
        self.update_timer2_display()

    def play_alarm(self):
        pygame.mixer.music.load("alarm.mp3")
        pygame.mixer.music.play()

    def run_timer1(self):
        while True:
            if self.timer1_running and not self.timer1_paused:
                current_time = time()
                elapsed_time = current_time - self.timer1_last_time
                if self.countdown:
                    self.timer1_value -= elapsed_time
                    if self.timer1_value <= 0:
                        self.timer1_value = 0
                        self.timer1_running = False
                        self.timer2_running = False
                        self.play_alarm()
                else:
                    self.timer1_value += elapsed_time
                    if self.timer1_max_value is not None and self.timer1_value >= self.timer1_max_value:
                        self.timer1_running = False
                        self.timer2_running = False
                        self.play_alarm()
                self.timer1_last_time = current_time
                self.update_timer1_display()
            sleep(0.1)

    def run_timer2(self):
        while True:
            if self.timer2_running and not self.timer2_paused:
                current_time = time()
                elapsed_time = current_time - self.timer2_last_time
                if self.countdown:
                    self.timer2_value -= elapsed_time
                    if self.timer2_value <= 0:
                        self.timer2_value = 0
                        self.timer1_running = False
                        self.timer2_running = False
                        self.play_alarm()
                else:
                    self.timer2_value += elapsed_time
                    if self.timer2_min_value is not None and self.timer2_value >= self.timer2_min_value:
                        self.timer1_running = False
                        self.timer2_running = False
                        self.play_alarm()
                self.timer2_last_time = current_time
                self.update_timer2_display()
            sleep(0.1)

    def previous_preset(self):
        self.current_preset_index = (self.current_preset_index - 1) % len(self.presets)
        self.set_preset(*self.presets[self.current_preset_index])

    def next_preset(self):
        self.current_preset_index = (self.current_preset_index + 1) % len(self.presets)
        self.set_preset(*self.presets[self.current_preset_index])

    def pause_resume_timer2(self):
        self.timer2_paused = not self.timer2_paused
        if not self.timer2_paused:
            self.run_timer2()

if __name__ == "__main__":
    root = tk.Tk()
    device_name = "000001 KbMouse"
    app = DualTimerApp(root, device_name)
    root.mainloop()
