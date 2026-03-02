# gui/result.py
import tkinter as tk
from PIL import Image, ImageTk


class ResultScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ----- Background + dark overlay (same as other screens) -----
        base_img = Image.open("assets/background.jpg").resize((1100, 650))
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
        self.canvas.create_text(
            550, 80,
            text="Diagnosis Result",
            fill="#f2e8d5",
            font=("Montserrat", 32, "bold")
        )

        # ----- Main panel (taller now: 460px) -----
        self.panel_bg = "#5a4636"
        panel_width, panel_height = 600, 500  # TALLER PANEL

        self.panel = tk.Frame(self, bg=self.panel_bg)
        self.canvas.create_window(
            550, 380,
            window=self.panel,
            width=panel_width,
            height=panel_height
        )

    # --------------------------------------------------

    def update_result(self, result):
        """
        result = {
            'diagnosis': str,
            'reasoning': [str],
            'rules_fired': [str],
            'answers': list
        }
        """

        for w in self.panel.winfo_children():
            w.destroy()

        # Diagnosis title
        tk.Label(
            self.panel,
            text="Diagnosis",
            bg=self.panel_bg,
            fg="#E0C9A6",
            font=("Montserrat", 18, "bold")
        ).place(relx=0.5, rely=0.06, anchor="center")

        # Diagnosis text
        tk.Label(
            self.panel,
            text=result.get("diagnosis", "No diagnosis found"),
            bg=self.panel_bg,
            fg="white",
            font=("Montserrat", 15),
            wraplength=540,
            justify="center"
        ).place(relx=0.5, rely=0.12, anchor="n")

        # Rules Fired title
        tk.Label(
            self.panel,
            text="Rules Applied",
            bg=self.panel_bg,
            fg="#E0C9A6",
            font=("Montserrat", 14, "bold")
        ).place(relx=0.03, rely=0.22, anchor="w")

        rules_fired = result.get("rules_fired", [])
        if not rules_fired:
            rules_fired = ["No rules fired"]

        # Rules fired list
        rules_frame = tk.Frame(self.panel, bg=self.panel_bg)
        rules_frame.place(relx=0.03, rely=0.27, anchor="nw")

        rules_text = " → ".join(rules_fired) if rules_fired else "No rules fired"
        tk.Label(
            rules_frame,
            text=rules_text,
            bg=self.panel_bg,
            fg="white",
            font=("Montserrat", 11),
            wraplength=540,
            justify="left"
        ).pack(anchor="w", pady=2)

        # Reasoning title
        tk.Label(
            self.panel,
            text="Reasoning Chain",
            bg=self.panel_bg,
            fg="#E0C9A6",
            font=("Montserrat", 14, "bold")
        ).place(relx=0.03, rely=0.40, anchor="w")

        reasoning = result.get("reasoning", [])
        if not reasoning:
            reasoning = ["No reasoning available"]

        # Reasoning list
        reason_frame = tk.Frame(self.panel, bg=self.panel_bg)
        reason_frame.place(relx=0.03, rely=0.45, anchor="nw")

        for r in reasoning:
            tk.Label(
                reason_frame,
                text=r,
                bg=self.panel_bg,
                fg="white",
                font=("Montserrat", 9),
                wraplength=540,
                justify="left"
            ).pack(anchor="w", pady=1)

        # ----- Rounded BACK button (plenty of space now) -----
        btn_width, btn_height = 160, 48
        radius = 24
        border_width = 3

        btn_canvas = tk.Canvas(
            self.panel,
            width=btn_width,
            height=btn_height,
            bg=self.panel_bg,
            highlightthickness=0,
            bd=0
        )
        btn_canvas.place(relx=0.5, rely=0.90, anchor="center")  # safe with taller panel

        x0, y0 = 0, 0
        x1, y1 = btn_width, btn_height

        btn_canvas.create_oval(
            x0, y0, x0 + 2 * radius, y1,
            fill="#C56A2D", outline="#3b2f2f", width=border_width
        )
        btn_canvas.create_oval(
            x1 - 2 * radius, y0, x1, y1,
            fill="#C56A2D", outline="#3b2f2f", width=border_width
        )
        btn_canvas.create_rectangle(
            x0 + radius, y0, x1 - radius, y1,
            fill="#C56A2D", outline="", width=0
        )

        back_btn = tk.Button(
            btn_canvas,
            text="BACK",
            bg="#C56A2D",
            fg="white",
            font=("Montserrat", 12, "bold"),
            bd=0,
            activebackground="#C56A2D",
            activeforeground="white",
            highlightthickness=0,
            command=self.go_back
        )
        btn_canvas.create_window(btn_width // 2, btn_height // 2, window=back_btn)

    # --------------------------------------------------

    def go_back(self):
        # Reset the diagnosis screen to start fresh
        self.controller.screens["DiagnosisScreen"].reset()
        self.controller.show_screen("DiagnosisScreen")

    # --------------------------------------------------

    def fade_in(self):
        self.controller.attributes("-alpha", 0)
        from gui.animations import fade_in
        fade_in(self.controller)
