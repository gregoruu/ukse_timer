import tkinter as tk
from time import sleep
import threading

class DualTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dual Timer")
        
        self.timer1_running = False
        self.timer2_running = False
        self.timer1_paused = False
        self.timer2_paused = False
        self.timer1_value = 0
        self.timer2_value = 0
        self.root.geometry("300x300")
        self.label1 = tk.Label(root, text="00:00", font=("Arial", 14))
        self.label1.pack()
        
        self.label2 = tk.Label(root, text="00:00", font=("Arial", 14))
        self.label2.pack()
        
        self.start_stop_button = tk.Button(root, text="Start/Stop", command=self.toggle_timers)
        self.start_stop_button.pack()
        
        self.pause_button1 = tk.Button(root, text="Pause/Resume Timer 1", command=self.pause_resume_timer1)
        self.pause_button1.pack()
        
        self.pause_button2 = tk.Button(root, text="Pause/Resume Timer 2", command=self.pause_resume_timer2)
        self.pause_button2.pack()
        
        self.reset_button = tk.Button(root, text="Reset", command=self.reset_timers)
        self.reset_button.pack()
        
        self.timer1_thread = threading.Thread(target=self.run_timer1, daemon=True)
        self.timer2_thread = threading.Thread(target=self.run_timer2, daemon=True)

    def toggle_timers(self):
        if not self.timer1_running and not self.timer2_running:
            self.timer1_running = True
            self.timer2_running = True
            if not self.timer1_thread.is_alive():
                self.timer1_thread = threading.Thread(target=self.run_timer1, daemon=True)
                self.timer1_thread.start()
            if not self.timer2_thread.is_alive():
                self.timer2_thread = threading.Thread(target=self.run_timer2, daemon=True)
                self.timer2_thread.start()
        else:
            self.timer1_running = False
            self.timer2_running = False

    def pause_resume_timer1(self):
        if self.timer1_running:
            self.timer1_paused = not self.timer1_paused

    def pause_resume_timer2(self):
        if self.timer2_running:
            self.timer2_paused = not self.timer2_paused

    def reset_timers(self):
        self.timer1_running = False
        self.timer2_running = False
        self.timer1_value = 0
        self.timer2_value = 0
        self.label1.config(text="00:00")
        self.label2.config(text="00:00")

    def run_timer1(self):
        while True:
            if self.timer1_running and not self.timer1_paused:
                self.timer1_value += 1
                minutes, seconds = divmod(self.timer1_value, 60)
                self.label1.config(text=f"{minutes:02}:{seconds:02}")
            sleep(1)

    def run_timer2(self):
        while True:
            if self.timer2_running and not self.timer2_paused:
                self.timer2_value += 1
                minutes, seconds = divmod(self.timer2_value, 60)
                self.label2.config(text=f"{minutes:02}:{seconds:02}")
            sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = DualTimerApp(root)
    root.mainloop()