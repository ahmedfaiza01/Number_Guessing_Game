import tkinter as tk
from tkinter import messagebox
import random
import json
import os

# Constants for difficulties
DIFFICULTIES = {
    "Easy":    {"range": (1, 10),  "attempts": 6},
    "Medium":  {"range": (1, 50),  "attempts": 7},
    "Hard":    {"range": (1, 100), "attempts": 8},
}

HIGHSCORE_FILE = "number_guess_highscores.json"

class NumberGuessGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Number Guessing Game")
        self.geometry("400x300")
        self.resizable(False, False)

        self.difficulty = tk.StringVar(value="Easy")
        self.secret_number = None
        self.attempts_left = 0
        self.low = 1
        self.high = 10
        self.max_attempts = 0
        self.current_attempt = 0

        self.highscores = self.load_highscores()

        self.create_widgets()
        self.start_new_game()

    def create_widgets(self):
        # Difficulty selection
        frame_diff = tk.Frame(self)
        frame_diff.pack(pady=10)
        tk.Label(frame_diff, text="Select Difficulty:").pack(side=tk.LEFT)

        for diff in DIFFICULTIES.keys():
            rb = tk.Radiobutton(frame_diff, text=diff, variable=self.difficulty, value=diff, command=self.start_new_game)
            rb.pack(side=tk.LEFT, padx=5)

        # Info label
        self.info_label = tk.Label(self, text="", font=("Arial", 12))
        self.info_label.pack(pady=10)

        # Entry for guess
        self.guess_entry = tk.Entry(self, font=("Arial", 14), justify='center')
        self.guess_entry.pack()
        self.guess_entry.bind("<Return>", lambda event: self.check_guess())

        # Attempts left label
        self.attempts_label = tk.Label(self, text="", font=("Arial", 12))
        self.attempts_label.pack(pady=5)

        # Hint label
        self.hint_label = tk.Label(self, text="", font=("Arial", 11), fg="blue")
        self.hint_label.pack()

        # Submit button
        self.submit_btn = tk.Button(self, text="Guess", command=self.check_guess)
        self.submit_btn.pack(pady=5)

        # Play again button (hidden until round ends)
        self.play_again_btn = tk.Button(self, text="Play Again", command=self.start_new_game)
        self.play_again_btn.pack(pady=10)
        self.play_again_btn.pack_forget()

        # Highscore display
        self.highscore_label = tk.Label(self, text="", font=("Arial", 10, "italic"))
        self.highscore_label.pack(pady=5)

    def load_highscores(self):
        if os.path.exists(HIGHSCORE_FILE):
            try:
                with open(HIGHSCORE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_highscores(self):
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                json.dump(self.highscores, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save highscores:\n{e}")

    def start_new_game(self):
        diff = self.difficulty.get()
        self.low, self.high = DIFFICULTIES[diff]["range"]
        self.max_attempts = DIFFICULTIES[diff]["attempts"]
        self.secret_number = random.randint(self.low, self.high)
        self.attempts_left = self.max_attempts
        self.current_attempt = 0
        self.info_label.config(text=f"I'm thinking of a number between {self.low} and {self.high}.")
        self.attempts_label.config(text=f"Attempts left: {self.attempts_left}")
        self.hint_label.config(text="")
        self.guess_entry.config(state=tk.NORMAL)
        self.submit_btn.config(state=tk.NORMAL)
        self.play_again_btn.pack_forget()
        self.guess_entry.delete(0, tk.END)
        self.guess_entry.focus_set()

        self.show_highscore()

    def show_highscore(self):
        diff = self.difficulty.get()
        if diff in self.highscores:
            best = self.highscores[diff]
            self.highscore_label.config(text=f"Best score for {diff}: {best} attempt(s)")
        else:
            self.highscore_label.config(text=f"No high score yet for {diff} difficulty.")

    def check_guess(self):
        guess_text = self.guess_entry.get().strip()
        if not guess_text.isdigit():
            messagebox.showwarning("Invalid input", "Please enter a valid number.")
            self.guess_entry.delete(0, tk.END)
            return

        guess = int(guess_text)
        if guess < self.low or guess > self.high:
            messagebox.showwarning("Out of range", f"Please enter a number between {self.low} and {self.high}.")
            self.guess_entry.delete(0, tk.END)
            return

        self.current_attempt += 1
        self.attempts_left -= 1
        self.attempts_label.config(text=f"Attempts left: {self.attempts_left}")

        if guess == self.secret_number:
            self.win_game()
        elif guess < self.secret_number:
            self.hint_label.config(text="Too low ▲")
            self.check_hint()
        else:
            self.hint_label.config(text="Too high ▼")
            self.check_hint()

        if self.attempts_left == 0 and guess != self.secret_number:
            self.lose_game()

        self.guess_entry.delete(0, tk.END)

    def check_hint(self):
        # Provide parity hint after half attempts used
        if self.current_attempt == self.max_attempts // 2:
            parity = "even" if self.secret_number % 2 == 0 else "odd"
            self.hint_label.config(text=self.hint_label.cget("text") + f" | Hint: The number is {parity}.")

    def win_game(self):
        attempts_used = self.current_attempt
        diff = self.difficulty.get()

        # Check/update highscore
        current_best = self.highscores.get(diff)
        if current_best is None or attempts_used < current_best:
            self.highscores[diff] = attempts_used
            self.save_highscores()
            msg = f"🎉 You won in {attempts_used} attempts!\nNew high score for {diff}!"
        else:
            msg = f"🎉 You won in {attempts_used} attempts!"

        messagebox.showinfo("Congratulations!", msg)
        self.end_round()

    def lose_game(self):
        messagebox.showinfo("Game Over", f"Out of attempts! The number was {self.secret_number}.")
        self.end_round()

    def end_round(self):
        self.guess_entry.config(state=tk.DISABLED)
        self.submit_btn.config(state=tk.DISABLED)
        self.play_again_btn.pack()

if __name__ == "__main__":
    app = NumberGuessGame()
    app.mainloop()
