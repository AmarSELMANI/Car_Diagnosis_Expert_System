# gui/welcome.py
import tkinter as tk
from PIL import Image, ImageTk
from gui.animations import fade_out


class WelcomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ----- Background + dark overlay -----
        base_img = Image.open("assets/background.jpg").resize((1100, 650))

        # Semi‑transparent overlay (#1f1a17 at ~62% opacity)
        overlay_color = (0x1F, 0x1A, 0x17, int(255 * 0.62))
        overlay = Image.new("RGBA", base_img.size, overlay_color)

        base_img = base_img.convert("RGBA")
        bg_with_overlay = Image.alpha_composite(base_img, overlay)

        self.bg_image = ImageTk.PhotoImage(bg_with_overlay)

        self.canvas = tk.Canvas(
            self, width=1100, height=650,
            highlightthickness=0, bd=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # ----- Title -----
        self.title = self.canvas.create_text(
            550, 200,
            text="Car Diagnosis Expert System",
            fill="#f2e8d5",
            font=("Montserrat", 36, "bold")
        )

        # ----- Subtitle -----
        self.subtitle = self.canvas.create_text(
            550, 260,
            text="Intelligent Vehicle Problem Analysis",
            fill="#E0C9A6",
            font=("Montserrat", 18, "italic")
        )

        # ----- Rounded START button background shape -----
        btn_width, btn_height = 180, 56
        x_center, y_center = 550, 330
        radius = 28

        x0 = x_center - btn_width // 2
        y0 = y_center - btn_height // 2
        x1 = x_center + btn_width // 2
        y1 = y_center + btn_height // 2

        # Left rounded end
        self.canvas.create_oval(
            x0, y0, x0 + 2 * radius, y1,
            fill="#C56A2D", outline="#3b2f2f", width=2
        )
        # Right rounded end
        self.canvas.create_oval(
            x1 - 2 * radius, y0, x1, y1,
            fill="#C56A2D", outline="#3b2f2f", width=2
        )
        # Middle rectangle (no outline to avoid double stroke)
        self.canvas.create_rectangle(
            x0 + radius, y0, x1 - radius, y1,
            fill="#C56A2D", outline="", width=0
        )

        # Transparent button on top of the shape
        self.start_btn = tk.Button(
            self,
            text="START",
            font=("Montserrat", 14, "bold"),
            bg="#C56A2D",
            fg="white",
            bd=0,
            activebackground="#C56A2D",
            activeforeground="white",
            highlightthickness=0,
            command=self.start
        )
        self.canvas.create_window(x_center, y_center, window=self.start_btn)

    def fade_in(self):
        self.controller.attributes("-alpha", 0)
        from gui.animations import fade_in
        fade_in(self.controller)

    def start(self):
        fade_out(
            self.controller,
            callback=lambda: self.controller.show_screen("DiagnosisScreen")
        )
