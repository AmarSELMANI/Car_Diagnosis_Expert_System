# gui/diagnosis.py
import tkinter as tk
from PIL import Image, ImageTk
from engine.inference_engine import ExpertSystem


class DiagnosisScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.system = ExpertSystem("engine/rules.json", "engine/questions.json")
        self.current_question = None
        self.selected_option = tk.StringVar()

        # ----- Background + dark overlay (same style as welcome) -----
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

        # Title (moved higher to avoid overlap with options)
        self.title_text = self.canvas.create_text(
            550, 50,
            text="Car Diagnosis",
            fill="#f2e8d5",
            font=("Montserrat", 32, "bold")
        )

        # ----- Panel (sharp corners, larger to fit all options) -----
        self.panel_bg = "#5a4636"
        panel_width, panel_height = 600, 500

        self.panel = tk.Frame(self, bg=self.panel_bg, highlightthickness=2, highlightbackground="#3b2f2f")
        self.canvas.create_window(550, 380, window=self.panel,
                                  width=panel_width, height=panel_height)
        # Ensure title stays on top of the panel
        self.canvas.tag_raise(self.title_text)

        self.render_question()

    def render_question(self):
        # Clear previous content
        for w in self.panel.winfo_children():
            w.destroy()

        # Decision-tree override: if user selected 'starting_issues', follow a compact branch
        # Prefer the explicit decision flow to reduce questions (engine_cranks -> branch)
        # Otherwise fall back to the generic next question lookup.
        self.current_question = None
        # If main_symptom chosen and it's starting_issues, drive a small decision tree
        main = self.system.facts.get("main_symptom")
        if main == "starting_issues":
            # If engine_cranks not yet asked, ask it first (crank split)
            if "engine_cranks" not in self.system.asked_questions:
                # find the question by id
                for q in self.system.questions:
                    if q["id"] == "engine_cranks":
                        self.current_question = q
                        break
            else:
                # If engine_cranks is answered True (engine cranks), ask combustion questions
                if self.system.facts.get("engine_cranks") == True:
                    # Ask engine_wont_start -> no_spark -> fuel_smell in order
                    for qid in ("engine_wont_start", "no_spark", "fuel_smell"):
                        if qid not in self.system.asked_questions:
                            self.current_question = next((q for q in self.system.questions if q["id"] == qid), None)
                            break
                else:
                    # Engine does not crank: ask headlights_dim then clicking_sound
                    for qid in ("headlights_dim", "clicking_sound"):
                        if qid not in self.system.asked_questions:
                            self.current_question = next((q for q in self.system.questions if q["id"] == qid), None)
                            break

        # Fallback to default behavior
        if not self.current_question:
            self.current_question = self.system.get_next_question()
        if not self.current_question:
            # No more questions, run diagnosis
            self.run_diagnosis()
            return

        # Question text at top
        tk.Label(
            self.panel,
            text=self.current_question["text"],
            bg=self.panel_bg,
            fg="#E0C9A6",
            font=("Montserrat", 16, "bold"),
            wraplength=550,
            justify="center"
        ).place(relx=0.5, rely=0.05, anchor="n")

        # Scrollable frame for options to prevent overflow
        scrollable_frame = tk.Frame(self.panel, bg=self.panel_bg)
        scrollable_frame.place(relx=0.5, rely=0.22, relwidth=0.95, relheight=0.65, anchor="n")

        # Create a canvas with scrollbar for options
        options_canvas = tk.Canvas(
            scrollable_frame,
            bg=self.panel_bg,
            highlightthickness=0,
            bd=0
        )
        scrollbar = tk.Scrollbar(scrollable_frame, orient="vertical", command=options_canvas.yview)
        scrollable_options_frame = tk.Frame(options_canvas, bg=self.panel_bg)
        scrollable_options_frame.bind(
            "<Configure>",
            lambda e: options_canvas.configure(scrollregion=options_canvas.bbox("all"))
        )
        options_canvas.create_window((0, 0), window=scrollable_options_frame, anchor="nw")
        options_canvas.configure(yscrollcommand=scrollbar.set)

        options_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.selected_option.set("")  # Reset selection

        for i, option in enumerate(self.current_question["options"]):
            tk.Radiobutton(
                scrollable_options_frame,
                text=option["text"],
                variable=self.selected_option,
                value=str(i),
                bg=self.panel_bg,
                fg="white",
                selectcolor=self.panel_bg,
                font=("Montserrat", 12),
                activebackground=self.panel_bg,
                activeforeground="white",
                command=self.on_option_select
            ).pack(anchor="w", padx=20, pady=4)

        # Next button
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
        btn_canvas.place(relx=0.5, rely=0.9, anchor="center")

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

        self.next_btn = tk.Button(
            btn_canvas,
            text="NEXT",
            font=("Montserrat", 13, "bold"),
            bg="#C56A2D",
            fg="white",
            bd=0,
            activebackground="#C56A2D",
            activeforeground="white",
            highlightthickness=0,
            command=self.next_question,
            state="disabled"  # Disabled until selection
        )
        btn_canvas.create_window(btn_width // 2, btn_height // 2, window=self.next_btn)

    def on_option_select(self):
        self.next_btn.config(state="normal")

    def next_question(self):
        if not self.selected_option.get():
            return
        idx = int(self.selected_option.get())
        option = self.current_question["options"][idx]
        fact = option["fact"]
        self.system.add_initial_facts(fact)
        self.system.answers.append(f"{self.current_question['text']}: {option['text']}")
        self.system.mark_question_asked(self.current_question["id"])
        # After each answer, run inference to see if a definitive problem was reached.
        # If so, stop immediately and show the result (early-exit decision tree behavior).
        self.system.run_inference()
        if self.system.facts.get("problem"):
            self.run_diagnosis()
            return

        # Otherwise continue asking according to decision flow / prerequisites
        self.render_question()

    def run_diagnosis(self):
        self.system.run_inference()
        diagnoses, reasoning = self.system.get_results()
        rules_fired = [fr["rule_id"] for fr in self.system.fired_rules]

        result = {
            "diagnosis": diagnoses[0] if diagnoses else "No specific problem could be identified.",
            "reasoning": reasoning or ["No rules applied."],
            "rules_fired": rules_fired
        }
        self.controller.screens["ResultScreen"].update_result(result)
        self.controller.show_screen("ResultScreen")

    def reset(self):
        self.system = ExpertSystem("engine/rules.json", "engine/questions.json")
        self.current_question = None
        self.selected_option.set("")
        self.render_question()

    def fade_in(self):
        self.controller.attributes("-alpha", 0)
        from gui.animations import fade_in
        fade_in(self.controller)
