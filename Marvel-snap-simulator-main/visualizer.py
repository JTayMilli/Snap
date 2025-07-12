import tkinter as tk
from tkinter import ttk
import re

class SnapVisualizer:
    def __init__(self, log_file):
        self.log_file = log_file
        self.game_turns = []
        self.current_turn_index = -1
        
        self.window = tk.Tk()
        self.window.title("Marvel Snap - Game Visualizer")
        self.window.geometry("1000x800")
        self.window.configure(bg="#282c34")

        self.parse_log_file()
        self.setup_ui()
        self.display_turn()

    def parse_log_file(self):
        """Parses the game_log.txt file to build a turn-by-turn history."""
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            return

        current_turn_data = None
        for line in lines:
            line = line.strip()
            if line.startswith("VIZ_TURN"):
                if current_turn_data:
                    self.game_turns.append(current_turn_data)
                turn_num = int(line.split(":")[1])
                current_turn_data = {
                    "turn": turn_num,
                    "locations": [{}, {}, {}],
                    "p1_hand": "", "p2_hand": "",
                    "p1_energy": "", "p2_energy": ""
                }
            elif line.startswith("VIZ_LOCATION") and current_turn_data:
                _, loc_idx, name, p1_power, p2_power = line.split(":")
                current_turn_data["locations"][int(loc_idx)] = {
                    "name": name, "p1_power": p1_power, "p2_power": p2_power,
                    "p1_cards": [], "p2_cards": []
                }
            elif line.startswith("VIZ_CARD") and current_turn_data:
                _, loc_idx, player, name, power = line.split(":")
                card_text = f"{name} ({power})"
                if player == "1":
                    current_turn_data["locations"][int(loc_idx)]["p1_cards"].append(card_text)
                else:
                    current_turn_data["locations"][int(loc_idx)]["p2_cards"].append(card_text)
            elif line.startswith("VIZ_P1_HAND") and current_turn_data:
                current_turn_data["p1_hand"] = line.split(":", 1)[1]
            elif line.startswith("VIZ_P2_HAND") and current_turn_data:
                current_turn_data["p2_hand"] = line.split(":", 1)[1]
            elif line.startswith("VIZ_P1_ENERGY") and current_turn_data:
                current_turn_data["p1_energy"] = line.split(":", 1)[1]
            elif line.startswith("VIZ_P2_ENERGY") and current_turn_data:
                current_turn_data["p2_energy"] = line.split(":", 1)[1]

        if current_turn_data:
            self.game_turns.append(current_turn_data)

    def setup_ui(self):
        main_frame = ttk.Frame(self.window, style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.window.style = ttk.Style()
        self.window.style.configure("Main.TFrame", background="#282c34")
        self.window.style.configure("TLabel", background="#282c34", foreground="white", font=("Segoe UI", 10))
        self.window.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        self.window.style.configure("Location.TFrame", background="#3c4049", relief=tk.SUNKEN, borderwidth=2)

        # Header for turn info
        header_frame = ttk.Frame(main_frame, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=5)
        self.turn_info_label = ttk.Label(header_frame, text="Turn: 0", style="Title.TLabel")
        self.turn_info_label.pack()
        self.energy_info_label = ttk.Label(header_frame, text="Energy P1: 0/0 | P2: 0/0", font=("Segoe UI", 12))
        self.energy_info_label.pack()

        # Board frame
        board_frame = ttk.Frame(main_frame, style="Main.TFrame")
        board_frame.pack(pady=10, expand=True, fill=tk.BOTH)
        board_frame.grid_columnconfigure((0, 1, 2), weight=1)
        board_frame.grid_rowconfigure(0, weight=1)

        self.location_frames = []
        for i in range(3):
            loc_frame = ttk.Frame(board_frame, style="Location.TFrame", padding=10)
            loc_frame.grid(row=0, column=i, sticky="nsew", padx=10)
            self.location_frames.append(loc_frame)

        # Footer for hands and navigation
        footer_frame = ttk.Frame(main_frame, style="Main.TFrame")
        footer_frame.pack(fill=tk.X, pady=5)
        self.p1_hand_label = ttk.Label(footer_frame, text="Player 1 Hand: ")
        self.p1_hand_label.pack()
        self.p2_hand_label = ttk.Label(footer_frame, text="Player 2 Hand: ")
        self.p2_hand_label.pack()

        nav_frame = ttk.Frame(footer_frame, style="Main.TFrame")
        nav_frame.pack(pady=10)
        prev_button = ttk.Button(nav_frame, text="<< Prev", command=self.prev_turn)
        prev_button.pack(side=tk.LEFT, padx=20)
        next_button = ttk.Button(nav_frame, text="Next >>", command=self.next_turn)
        next_button.pack(side=tk.LEFT, padx=20)

    def display_turn(self):
        if not self.game_turns:
            self.turn_info_label.config(text="No game data loaded.")
            return

        if self.current_turn_index < 0:
            self.turn_info_label.config(text="Game Start. Press 'Next' to begin.")
            return

        turn_data = self.game_turns[self.current_turn_index]
        self.turn_info_label.config(text=f"Turn: {turn_data['turn']}")
        self.energy_info_label.config(text=f"Energy P1: {turn_data['p1_energy']} | P2: {turn_data['p2_energy']}")
        self.p1_hand_label.config(text=f"Player 1 Hand: {turn_data['p1_hand']}")
        self.p2_hand_label.config(text=f"Player 2 Hand: {turn_data['p2_hand']}")

        for i, loc_data in enumerate(turn_data["locations"]):
            loc_frame = self.location_frames[i]
            for widget in loc_frame.winfo_children():
                widget.destroy()

            ttk.Label(loc_frame, text=loc_data.get('name', '...'), font=("Segoe UI", 12, "bold")).pack(pady=5)
            
            p2_power = loc_data.get('p2_power', '0')
            ttk.Label(loc_frame, text=f"P2 Power: {p2_power}", foreground="#e06c75", font=("Segoe UI", 10, "bold")).pack()
            for card_text in loc_data.get('p2_cards', []):
                tk.Label(loc_frame, text=card_text, bg="#e06c75", fg="white", relief=tk.RAISED, borderwidth=1, padx=5, pady=2).pack(pady=2, fill=tk.X)

            # Spacer
            ttk.Label(loc_frame, text="").pack(pady=10)
            
            p1_power = loc_data.get('p1_power', '0')
            ttk.Label(loc_frame, text=f"P1 Power: {p1_power}", foreground="#61afef", font=("Segoe UI", 10, "bold")).pack()
            for card_text in loc_data.get('p1_cards', []):
                tk.Label(loc_frame, text=card_text, bg="#61afef", fg="white", relief=tk.RAISED, borderwidth=1, padx=5, pady=2).pack(pady=2, fill=tk.X)

    def next_turn(self):
        if self.current_turn_index < len(self.game_turns) - 1:
            self.current_turn_index += 1
            self.display_turn()

    def prev_turn(self):
        if self.current_turn_index > -1:
            self.current_turn_index -= 1
            self.display_turn()

    def run(self):
        self.window.mainloop()
