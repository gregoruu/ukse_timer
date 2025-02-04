import tkinter as tk
from time import sleep, time
import threading
import pygame
from evdev import InputDevice, categorize, ecodes

class DualTimerApp:
    def __init__(self, root, device_path):
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
            (15*60, 3*60),
            (20*60, 5*60),
            (30*60, 10*60),
            (35*60, 15*60),
            (40*60, 20*60),
            (15*60, 3*60, True),
            (20*60, 5*60, True),
            (30*60, 10*60, True),
            (35*60, 15*60, True),
            (40*60, 20*60, True)
        ]
        self.current_preset_index = 0
        self.root.geometry("300x400")
        self.label1 = tk.Label(root, text="00:00", font=("Arial", 14))
        self.label1.pack()
        
        self.label2 = tk.Label(root, text="00:00", font=("Arial", 14))
        self.label2.pack()
        
        self.reset_button = tk.Button(root, text="Reset", command=self.reset_timers)
        self.reset_button.pack()
        
        self.start_pause_button = tk.Button(root, text="Start/Pause", command=self.pause_resume_timer2)
        self.start_pause_button.pack()
        
        self.timer1_thread = threading.Thread(target=self.run_timer1, daemon=True)
        self.timer2_thread = threading.Thread(target=self.run_timer2, daemon=True)
        self.timer1_thread.start()
        self.timer2_thread.start()

        pygame.mixer.init()

        self.device = InputDevice(device_path)
        self.input_thread = threading.Thread(target=self.read_input, daemon=True)
        self.input_thread.start()

        self.set_preset(*self.presets[self.current_preset_index])

    def read_input(self):
        for event in self.device.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == key_event.key_down:
                    if key_event.keycode == 'KEY_LEFT':
                        self.previous_preset()
                    elif key_event.keycode == 'KEY_RIGHT':
                        self.next_preset()
                    elif key_event.keycode == 'KEY_OK':
                        self.pause_resume_timer2()
                    elif key_event.keycode == 'KEY_BACK':
                        self.reset_timers()

    def previous_preset(self):
        self.current_preset_index = (self.current_preset_index - 1) % len(self.presets)
        self.set_preset(*self.presets[self.current_preset_index])

    def next_preset(self):
        self.current_preset_index = (self.current_preset_index + 1) % len(self.presets)
        self.set_preset(*self.presets[self.current_preset_index])

    def pause_resume_timer2(self):
        if not self.timer1_running and not self.timer2_running:
            self.timer1_running = True
            self.timer2_running = True
            self.timer1_last_time = time()
            self.timer2_last_time = time()
        elif self.timer2_running:
            self.timer2_paused = not self.timer2_paused
            if not self.timer2_paused:
                self.timer2_last_time = time()

    def set_preset(self, timer1_value, timer2_value, countdown=False):
        self.countdown = countdown
        if countdown:
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
        self.timer1_max_value = None
        self.timer2_min_value = None
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

if __name__ == "__main__":
    root = tk.Tk()
    device_path = '/dev/input/event0'  #Device path
    app = DualTimerApp(root, device_path)
    root.mainloop()