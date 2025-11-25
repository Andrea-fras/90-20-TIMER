import argparse
import dataclasses
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional


ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_GREEN = "\033[92m"
ANSI_BLUE = "\033[94m"
ANSI_YELLOW = "\033[93m"
ANSI_CYAN = "\033[96m"


@dataclasses.dataclass
class TimerConfig:
    work_minutes: int = 90
    rest_minutes: int = 20
    cycles: int = 1
    demo: bool = False
    sound: bool = True
    notifications: bool = True


def format_duration(seconds: int) -> str:
    minutes, sec = divmod(max(0, seconds), 60)
    return f"{minutes:02d}:{sec:02d}"


def play_sound(sound_enabled: bool) -> None:
    if not sound_enabled:
        return

    sound_paths = [
        "/System/Library/Sounds/Glass.aiff",
        "/System/Library/Sounds/Pop.aiff",
        "/System/Library/Sounds/Submarine.aiff",
    ]

    for path in sound_paths:
        try:
            subprocess.run(["afplay", path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except FileNotFoundError:
            break
        except subprocess.CalledProcessError:
            continue

    print("\a", end="", flush=True)


def send_notification(title: str, message: str, notifications_enabled: bool) -> None:
    if not notifications_enabled:
        return

    script = f'display notification "{message}" with title "{title}"'
    try:
        subprocess.run(["osascript", "-e", script], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return


class TimerApp:
    def __init__(self, config: TimerConfig) -> None:
        self.config = config
        self.root = tk.Tk()
        self.root.title("90/20 Timer")
        self.root.geometry("420x360")
        self.root.configure(bg="#0f172a")

        self.work_var = tk.StringVar(value=str(config.work_minutes))
        self.rest_var = tk.StringVar(value=str(config.rest_minutes))
        self.cycles_var = tk.StringVar(value=str(config.cycles))
        self.demo_var = tk.BooleanVar(value=config.demo)

        self.current_cycle = 1
        self.current_phase = "work"
        self.remaining_seconds = self._calculate_seconds(config.work_minutes)
        self.running = False
        self.after_id: Optional[str] = None

        self._build_ui()
        self._reset_state()

    def _build_ui(self) -> None:
        header = tk.Label(
            self.root,
            text="90/20 Focus Timer",
            font=("SF Pro Display", 18, "bold"),
            fg="#e2e8f0",
            bg="#0f172a",
        )
        header.pack(pady=(16, 6))

        subtitle = tk.Label(
            self.root,
            text="Work 90 / Rest 20 with clear visual + sound cues",
            font=("SF Pro Display", 11),
            fg="#94a3b8",
            bg="#0f172a",
        )
        subtitle.pack(pady=(0, 12))

        form = tk.Frame(self.root, bg="#0f172a")
        form.pack(pady=8)

        self._add_labeled_entry(form, "Work (minutes)", self.work_var, 0)
        self._add_labeled_entry(form, "Rest (minutes)", self.rest_var, 1)
        self._add_labeled_entry(form, "Cycles", self.cycles_var, 2)

        demo_check = tk.Checkbutton(
            form,
            text="Demo (treat values as seconds)",
            variable=self.demo_var,
            fg="#e2e8f0",
            bg="#0f172a",
            activebackground="#0f172a",
            selectcolor="#0f172a",
            anchor="w",
        )
        demo_check.grid(row=3, column=0, columnspan=2, sticky="w", pady=(6, 0))

        self.status_label = tk.Label(
            self.root,
            text="Ready to start",
            font=("SF Pro Display", 12, "bold"),
            fg="#cbd5e1",
            bg="#0f172a",
        )
        self.status_label.pack(pady=(16, 6))

        self.timer_label = tk.Label(
            self.root,
            text=format_duration(self.remaining_seconds),
            font=("SF Pro Display", 44, "bold"),
            fg="#f8fafc",
            bg="#0f172a",
        )
        self.timer_label.pack(pady=4)

        self.progress_label = tk.Label(
            self.root,
            text="Cycle 1 of 1",
            font=("SF Pro Display", 11),
            fg="#94a3b8",
            bg="#0f172a",
        )
        self.progress_label.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(
            self.root,
            orient="horizontal",
            length=320,
            mode="determinate",
        )
        self.progress.pack(pady=6)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor="#1e293b", bordercolor="#1e293b", background="#22c55e")

        buttons = tk.Frame(self.root, bg="#0f172a")
        buttons.pack(pady=(12, 4))

        self.start_button = tk.Button(
            buttons,
            text="Start",
            command=self.toggle_start_pause,
            font=("SF Pro Display", 12, "bold"),
            fg="#0f172a",
            bg="#22c55e",
            activebackground="#16a34a",
            activeforeground="#0f172a",
            width=10,
            bd=0,
            padx=6,
            pady=6,
        )
        self.start_button.grid(row=0, column=0, padx=6)

        reset_button = tk.Button(
            buttons,
            text="Reset",
            command=self._reset_state,
            font=("SF Pro Display", 12),
            fg="#e2e8f0",
            bg="#1e293b",
            activebackground="#334155",
            activeforeground="#e2e8f0",
            width=10,
            bd=0,
            padx=6,
            pady=6,
        )
        reset_button.grid(row=0, column=1, padx=6)

        self._update_colors("work")

    def _add_labeled_entry(self, parent: tk.Frame, label_text: str, var: tk.StringVar, row: int) -> None:
        label = tk.Label(parent, text=label_text, font=("SF Pro Display", 11), fg="#cbd5e1", bg="#0f172a")
        label.grid(row=row, column=0, sticky="w", pady=3, padx=(0, 10))
        entry = tk.Entry(parent, textvariable=var, width=8, font=("SF Pro Display", 11))
        entry.grid(row=row, column=1, sticky="w", pady=3)

    def _calculate_seconds(self, minutes: int) -> int:
        return minutes if self.demo_var.get() else minutes * 60

    def toggle_start_pause(self) -> None:
        if self.running:
            self.running = False
            if self.after_id is not None:
                self.root.after_cancel(self.after_id)
            self.start_button.configure(text="Resume", bg="#fbbf24", activebackground="#f59e0b")
            self.status_label.configure(text="Paused", fg="#fbbf24")
            return

        if self.current_phase == "idle":
            if not self._load_config():
                return
        self.running = True
        self.start_button.configure(text="Pause", bg="#22c55e", activebackground="#16a34a")
        self._tick()

    def _load_config(self) -> bool:
        try:
            work = int(self.work_var.get())
            rest = int(self.rest_var.get())
            cycles = int(self.cycles_var.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter whole numbers for work, rest, and cycles.")
            return False

        if work <= 0:
            messagebox.showerror("Invalid work length", "Work duration must be greater than zero.")
            return False
        if rest < 0:
            messagebox.showerror("Invalid rest length", "Rest duration cannot be negative.")
            return False
        if cycles <= 0:
            messagebox.showerror("Invalid cycles", "Number of cycles must be at least 1.")
            return False

        self.config.work_minutes = work
        self.config.rest_minutes = rest
        self.config.cycles = cycles
        self.config.demo = self.demo_var.get()

        self.current_cycle = 1
        self.current_phase = "work"
        self.remaining_seconds = self._calculate_seconds(self.config.work_minutes)
        self._update_display()
        self._update_cycle_text()
        self._update_colors("work")
        self.status_label.configure(text="Work session", fg="#22c55e")
        return True

    def _tick(self) -> None:
        if not self.running:
            return

        self._update_display()
        self._update_progress()

        if self.remaining_seconds <= 0:
            self._handle_phase_complete()
            return

        self.remaining_seconds -= 1
        self.after_id = self.root.after(1000, self._tick)

    def _handle_phase_complete(self) -> None:
        play_sound(self.config.sound)
        send_notification("90/20 Timer", f"{self.current_phase.title()} session complete", self.config.notifications)

        if self.current_phase == "work" and self.config.rest_minutes > 0:
            self.current_phase = "rest"
            self.remaining_seconds = self._calculate_seconds(self.config.rest_minutes)
            self.status_label.configure(text="Rest break", fg="#38bdf8")
            self._update_colors("rest")
            self._update_display()
            self._update_progress(reset=True)
            self.after_id = self.root.after(1000, self._tick)
            return

        if self.current_phase == "rest":
            self.current_cycle += 1

        if self.current_cycle > self.config.cycles:
            self.running = False
            self.current_phase = "idle"
            self.start_button.configure(text="Start", bg="#22c55e", activebackground="#16a34a")
            self.status_label.configure(text="All cycles complete", fg="#c084fc")
            self._update_colors("done")
            messagebox.showinfo("Finished", "All work/rest cycles are complete!")
            return

        self.current_phase = "work"
        self.remaining_seconds = self._calculate_seconds(self.config.work_minutes)
        self.status_label.configure(text="Work session", fg="#22c55e")
        self._update_colors("work")
        self._update_cycle_text()
        self._update_display()
        self._update_progress(reset=True)
        self.after_id = self.root.after(1000, self._tick)

    def _update_display(self) -> None:
        self.timer_label.configure(text=format_duration(self.remaining_seconds))

    def _update_cycle_text(self) -> None:
        self.progress_label.configure(text=f"Cycle {self.current_cycle} of {self.config.cycles}")

    def _update_progress(self, reset: bool = False) -> None:
        if reset:
            self.progress.configure(value=0, maximum=self.remaining_seconds or 1)
            return

        total = self._calculate_seconds(self.config.work_minutes if self.current_phase == "work" else self.config.rest_minutes)
        elapsed = total - self.remaining_seconds
        self.progress.configure(maximum=total, value=elapsed)

    def _update_colors(self, phase: str) -> None:
        if phase == "work":
            accent = "#22c55e"
        elif phase == "rest":
            accent = "#38bdf8"
        else:
            accent = "#a855f7"

        self.timer_label.configure(fg="#f8fafc")
        self.root.configure(bg="#0f172a")
        self.status_label.configure(bg="#0f172a")
        self.progress_label.configure(bg="#0f172a")

        style = ttk.Style()
        style.configure("TProgressbar", troughcolor="#1e293b", bordercolor="#1e293b", background=accent)
        self.start_button.configure(bg=accent, activebackground=accent)

    def _reset_state(self) -> None:
        self.running = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.current_phase = "idle"
        self.remaining_seconds = self._calculate_seconds(int(self.work_var.get()))
        self.status_label.configure(text="Ready to start", fg="#cbd5e1")
        self.start_button.configure(text="Start", bg="#22c55e", activebackground="#16a34a")
        self._update_colors("work")
        self._update_display()
        self._update_cycle_text()
        self._update_progress(reset=True)

    def run(self) -> None:
        self.root.mainloop()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GUI-focused 90/20 timer")
    parser.add_argument("--demo", action="store_true", help="Treat duration values as seconds for quick demos")
    parser.add_argument("--no-sound", action="store_true", help="Disable completion sounds")
    parser.add_argument("--no-notifications", action="store_true", help="Disable macOS notifications")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    config = TimerConfig(
        demo=args.demo,
        sound=not args.no_sound,
        notifications=not args.no_notifications,
    )

    app = TimerApp(config)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
