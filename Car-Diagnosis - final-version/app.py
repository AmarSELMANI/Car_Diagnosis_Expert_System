# gui/app.py
import tkinter as tk
from gui.welcome import WelcomeScreen
from gui.diagnosis import DiagnosisScreen
from gui.result import ResultScreen

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Car Diagnosis Expert System")
        self.geometry("1100x650")
        # Start maximized for fullscreen experience
        try:
            self.state("zoomed")
        except Exception:
            pass
        self.resizable(True, True)

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.screens = {}
        for Screen in (WelcomeScreen, DiagnosisScreen, ResultScreen):
            screen = Screen(self.container, self)
            self.screens[Screen.__name__] = screen
            screen.place(relwidth=1, relheight=1)

        self.show_screen("WelcomeScreen")

    def show_screen(self, name):
        screen = self.screens[name]
        screen.tkraise()
        screen.fade_in()

if __name__ == "__main__":
    app = App()
    app.mainloop()
